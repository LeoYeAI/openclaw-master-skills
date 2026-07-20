#!/usr/bin/env python3
"""
migration_gen.py — 对比两个 Go struct 版本，生成 ALTER TABLE 迁移 SQL
用法:
  python3 migration_gen.py old.go new.go --table users
  python3 migration_gen.py old.go new.go --table orders --db mysql
  python3 migration_gen.py --old-struct "Name string; Age int" --new-struct "Name string; Age int; Email string" --table users

输入格式: 包含 GORM struct 定义的 Go 文件（或 stdin）
"""

import sys
import re
import argparse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ── Go → MySQL 类型映射 ──────────────────────────────────────────────────────
GO_TO_MYSQL = {
    "string":      "VARCHAR(255)",
    "int":         "INT",
    "int8":        "TINYINT",
    "int16":       "SMALLINT",
    "int32":       "INT",
    "int64":       "BIGINT",
    "uint":        "INT UNSIGNED",
    "uint8":       "TINYINT UNSIGNED",
    "uint16":      "SMALLINT UNSIGNED",
    "uint32":      "INT UNSIGNED",
    "uint64":      "BIGINT UNSIGNED",
    "float32":     "FLOAT",
    "float64":     "DOUBLE",
    "bool":        "TINYINT(1)",
    "time.Time":   "DATETIME",
    "[]byte":      "BLOB",
    "datatypes.JSON": "JSON",
    "sql.NullString":  "VARCHAR(255)",
    "sql.NullInt64":   "BIGINT",
    "sql.NullFloat64": "DOUBLE",
    "sql.NullBool":    "TINYINT(1)",
    "sql.NullTime":    "DATETIME",
}

@dataclass
class FieldDef:
    name: str           # Go field name
    col_name: str       # DB column name (snake_case)
    go_type: str
    db_type: str        # 从 tag 或类型推断
    nullable: bool
    default: Optional[str]
    unique: bool
    index: List[str]    # index names
    unique_index: List[str]
    not_null: bool
    size: Optional[str]
    comment: Optional[str]
    raw_tag: str

def pascal_to_snake(name: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def parse_gorm_tag(tag_str: str) -> dict:
    """解析 `gorm:"column:x;type:varchar(100);not null;default:0"` 等"""
    result = {
        "column": None, "type": None, "not_null": False,
        "default": None, "unique": False, "primary_key": False,
        "index": [], "unique_index": [], "size": None, "comment": None,
        "auto_increment": False,
    }
    gorm_m = re.search(r'gorm:"([^"]*)"', tag_str)
    if not gorm_m:
        return result
    parts = gorm_m.group(1).split(";")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            k, v = part.split(":", 1)
            k = k.strip().lower()
            v = v.strip()
            if k == "column":
                result["column"] = v
            elif k == "type":
                result["type"] = v
            elif k == "size":
                result["size"] = v
            elif k == "default":
                result["default"] = v
            elif k == "index":
                result["index"].append(v)
            elif k == "uniqueindex":
                result["unique_index"].append(v)
            elif k == "comment":
                result["comment"] = v
        else:
            p_lower = part.lower()
            if p_lower in ("not null", "notnull"):
                result["not_null"] = True
            elif p_lower in ("unique", "uniqueindex"):
                result["unique"] = True
            elif p_lower == "primarykey":
                result["primary_key"] = True
            elif p_lower == "autoincrement":
                result["auto_increment"] = True
            elif p_lower == "index":
                result["index"].append("__auto__")
            elif p_lower == "uniqueindex":
                result["unique_index"].append("__auto__")
    return result

def parse_struct(source: str) -> Dict[str, FieldDef]:
    """从 Go 源码中提取 struct 字段"""
    fields: Dict[str, FieldDef] = {}

    # 提取 struct 内容（支持多个 struct，取第一个含 gorm 的）
    struct_bodies = re.findall(r'type\s+\w+\s+struct\s*\{([^}]+)\}', source, re.DOTALL)

    for body in struct_bodies:
        lines = body.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # 跳过 gorm.Model 嵌入（其字段 id/created_at 等已知）
            if line == "gorm.Model":
                for builtin_name, builtin_col, builtin_type in [
                    ("ID", "id", "uint"),
                    ("CreatedAt", "created_at", "time.Time"),
                    ("UpdatedAt", "updated_at", "time.Time"),
                    ("DeletedAt", "deleted_at", "time.Time"),
                ]:
                    db_type = "BIGINT UNSIGNED" if builtin_name == "ID" else GO_TO_MYSQL.get(builtin_type, "VARCHAR(255)")
                    fields[builtin_col] = FieldDef(
                        name=builtin_name, col_name=builtin_col,
                        go_type=builtin_type, db_type=db_type,
                        nullable=builtin_col == "deleted_at",
                        default=None, unique=builtin_name=="ID",
                        index=[], unique_index=[],
                        not_null=builtin_col != "deleted_at",
                        size=None, comment=None,
                        raw_tag=""
                    )
                continue

            # 解析字段行: FieldName Type `tags`
            field_m = re.match(r'(\w+)\s+([\w\[\]\*\.]+)\s*(`[^`]*`)?', line)
            if not field_m:
                continue

            fname = field_m.group(1)
            ftype = field_m.group(2)
            tag_str = field_m.group(3) or ""

            tag = parse_gorm_tag(tag_str)

            col_name = tag["column"] or pascal_to_snake(fname)

            # 推断 DB 类型
            base_type = ftype.lstrip('*')
            if tag["type"]:
                db_type = tag["type"].upper()
            elif tag["size"]:
                base = GO_TO_MYSQL.get(base_type, "VARCHAR(255)")
                db_type = re.sub(r'\(\d+\)', f'({tag["size"]})', base)
                if '(' not in db_type:
                    db_type += f'({tag["size"]})'
            else:
                db_type = GO_TO_MYSQL.get(base_type, "VARCHAR(255)")

            nullable = ftype.startswith('*') or base_type.startswith("sql.Null") or not tag["not_null"]

            fields[col_name] = FieldDef(
                name=fname, col_name=col_name,
                go_type=ftype, db_type=db_type,
                nullable=nullable,
                default=tag["default"], unique=tag["unique"],
                index=tag["index"], unique_index=tag["unique_index"],
                not_null=tag["not_null"], size=tag["size"],
                comment=tag["comment"], raw_tag=tag_str,
            )

    return fields


def generate_migration(
    old_fields: Dict[str, FieldDef],
    new_fields: Dict[str, FieldDef],
    table: str,
    db_type: str = "mysql",
) -> Tuple[str, str]:
    """返回 (up_sql, down_sql)"""
    up_stmts: List[str] = []
    down_stmts: List[str] = []

    added   = {k: v for k, v in new_fields.items() if k not in old_fields}
    removed = {k: v for k, v in old_fields.items() if k not in new_fields}
    changed = {}
    for k in new_fields:
        if k in old_fields:
            n, o = new_fields[k], old_fields[k]
            if n.db_type != o.db_type or n.nullable != o.nullable or n.default != o.default:
                changed[k] = (o, n)

    def col_def(f: FieldDef, include_null: bool = True) -> str:
        parts = [f.db_type]
        if include_null:
            parts.append("NULL" if f.nullable else "NOT NULL")
        if f.default is not None:
            parts.append(f"DEFAULT {f.default}")
        if f.comment:
            parts.append(f"COMMENT '{f.comment}'")
        return " ".join(parts)

    # 新增列
    for col, f in added.items():
        algorithm = ", ALGORITHM=INSTANT" if db_type == "mysql" else ""
        up_stmts.append(
            f"ALTER TABLE `{table}` ADD COLUMN `{col}` {col_def(f)}{algorithm};"
        )
        down_stmts.append(
            f"ALTER TABLE `{table}` DROP COLUMN `{col}`;"
        )

    # 删除列（up 删，down 加回）
    for col, f in removed.items():
        up_stmts.append(
            f"ALTER TABLE `{table}` DROP COLUMN `{col}`;"
        )
        down_stmts.append(
            f"ALTER TABLE `{table}` ADD COLUMN `{col}` {col_def(f)}, ALGORITHM=INSTANT;"
        )

    # 修改列
    for col, (old_f, new_f) in changed.items():
        up_stmts.append(
            f"ALTER TABLE `{table}` MODIFY COLUMN `{col}` {col_def(new_f)};"
            + (f"  -- was: {col_def(old_f)}" if col_def(old_f) != col_def(new_f) else "")
        )
        down_stmts.append(
            f"ALTER TABLE `{table}` MODIFY COLUMN `{col}` {col_def(old_f)};"
        )

    # 新增索引
    for col, f in added.items():
        if f.unique:
            up_stmts.append(f"ALTER TABLE `{table}` ADD UNIQUE INDEX `uk_{table}_{col}` (`{col}`);")
            down_stmts.append(f"DROP INDEX `uk_{table}_{col}` ON `{table}`;")
        for idx in f.index:
            idx_name = f"idx_{table}_{col}" if idx == "__auto__" else idx
            up_stmts.append(f"ALTER TABLE `{table}` ADD INDEX `{idx_name}` (`{col}`);")
            down_stmts.append(f"DROP INDEX `{idx_name}` ON `{table}`;")

    if not up_stmts:
        return "-- 无结构变更\n", "-- 无需回滚\n"

    version_hint = "-- 建议版本号: <下一个版本号>_<描述>.{up|down}.sql"
    up_sql = version_hint + "\n" + "\n".join(up_stmts) + "\n"
    down_sql = version_hint.replace(".up.", ".down.") + "\n" + "\n".join(reversed(down_stmts)) + "\n"

    return up_sql, down_sql


def main():
    parser = argparse.ArgumentParser(description="GORM struct diff → ALTER TABLE SQL")
    parser.add_argument("old_file", nargs="?", help="旧版 Go 文件")
    parser.add_argument("new_file", nargs="?", help="新版 Go 文件")
    parser.add_argument("--table", required=True, help="数据库表名")
    parser.add_argument("--db", default="mysql", choices=["mysql", "postgres"], help="数据库类型")
    parser.add_argument("--old-struct", help="旧 struct 字段（内联，格式: 'Field Type `tag`; ...'）")
    parser.add_argument("--new-struct", help="新 struct 字段（内联）")
    args = parser.parse_args()

    if args.old_struct and args.new_struct:
        def inline_to_src(s: str) -> str:
            result, in_tick = [], False
            for ch in s:
                if ch == '`': in_tick = not in_tick
                result.append('\n' if (ch == ';' and not in_tick) else ch)
            return "type T struct { " + "".join(result) + " }"
        old_src = inline_to_src(args.old_struct)
        new_src = inline_to_src(args.new_struct)
    elif args.old_file and args.new_file:
        with open(args.old_file, encoding="utf-8") as f:
            old_src = f.read()
        with open(args.new_file, encoding="utf-8") as f:
            new_src = f.read()
    else:
        parser.print_help()
        sys.exit(1)

    old_fields = parse_struct(old_src)
    new_fields = parse_struct(new_src)

    if not old_fields and not new_fields:
        print("❌ 未能解析到 struct 字段，请确认文件包含有效的 Go struct 定义", file=sys.stderr)
        sys.exit(1)

    print(f"-- 解析结果: 旧版 {len(old_fields)} 字段, 新版 {len(new_fields)} 字段")
    added   = [k for k in new_fields if k not in old_fields]
    removed = [k for k in old_fields if k not in new_fields]
    changed = [k for k in new_fields if k in old_fields and (
        new_fields[k].db_type != old_fields[k].db_type or
        new_fields[k].nullable != old_fields[k].nullable
    )]
    print(f"-- 变更: +{len(added)} 新增, -{len(removed)} 删除, ~{len(changed)} 修改\n")

    up_sql, down_sql = generate_migration(old_fields, new_fields, args.table, args.db)

    print("-- ===== UP (迁移) =====")
    print(up_sql)
    print("-- ===== DOWN (回滚) =====")
    print(down_sql)


if __name__ == "__main__":
    main()

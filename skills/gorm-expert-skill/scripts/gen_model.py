#!/usr/bin/env python3
"""
gen_model.py — 将 CREATE TABLE SQL 转换为带 GORM tag 的 Go struct
用法:
  python3 gen_model.py schema.sql
  echo "CREATE TABLE ..." | python3 gen_model.py -
  python3 gen_model.py --table users --fields "id:bigint,name:varchar(100),created_at:datetime"
"""

import sys
import re
import argparse
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ── MySQL 类型映射表 ────────────────────────────────────────────────────────
SQL_TO_GO_MYSQL = {
    "tinyint":"int8","smallint":"int16","mediumint":"int32",
    "int":"int32","integer":"int32","bigint":"int64",
    "tinyint unsigned":"uint8","smallint unsigned":"uint16",
    "mediumint unsigned":"uint32","int unsigned":"uint32","bigint unsigned":"uint64",
    "float":"float32","double":"float64","decimal":"float64","numeric":"float64",
    "char":"string","varchar":"string","tinytext":"string","text":"string",
    "mediumtext":"string","longtext":"string","enum":"string","set":"string",
    "date":"time.Time","datetime":"time.Time","timestamp":"time.Time",
    "time":"string","year":"int16",
    "bool":"bool","boolean":"bool",
    "blob":"[]byte","mediumblob":"[]byte","longblob":"[]byte",
    "binary":"[]byte","varbinary":"[]byte",
    "json":"datatypes.JSON",
}

# ── PostgreSQL 类型映射表 ────────────────────────────────────────────────────
SQL_TO_GO_PG = {
    "smallint":"int16","integer":"int32","int":"int32",
    "int2":"int16","int4":"int32","int8":"int64","bigint":"int64",
    "smallserial":"int16","serial":"int32","bigserial":"int64",
    "real":"float32","float4":"float32","double precision":"float64",
    "float8":"float64","numeric":"float64","decimal":"float64",
    "char":"string","character":"string","varchar":"string",
    "character varying":"string","text":"string","citext":"string","name":"string",
    "date":"time.Time","time":"string","timetz":"string",
    "time with time zone":"string",
    "timestamp":"time.Time","timestamptz":"time.Time",
    "timestamp with time zone":"time.Time",
    "timestamp without time zone":"time.Time","interval":"string",
    "bool":"bool","boolean":"bool",
    "bytea":"[]byte",
    "uuid":"string",
    "json":"datatypes.JSON","jsonb":"datatypes.JSON",
    "integer[]":"pq.Int64Array","bigint[]":"pq.Int64Array",
    "text[]":"pq.StringArray","varchar[]":"pq.StringArray",
    "inet":"string","cidr":"string","macaddr":"string","point":"string","money":"float64",
}

# 运行时由 --dialect 参数切换，默认 MySQL
SQL_TO_GO = SQL_TO_GO_MYSQL

@dataclass
class Column:
    name: str
    sql_type: str
    go_type: str
    nullable: bool
    is_pk: bool
    is_auto: bool
    has_default: bool
    default_val: Optional[str]
    comment: str
    unique: bool
    size: Optional[str]  # varchar(100) -> "100"

@dataclass
class Table:
    name: str
    columns: List[Column] = field(default_factory=list)
    indexes: List[Tuple[str, List[str]]] = field(default_factory=list)  # (name, cols)
    unique_indexes: List[Tuple[str, List[str]]] = field(default_factory=list)


def snake_to_pascal(s: str) -> str:
    """user_profile -> UserProfile"""
    return "".join(word.capitalize() for word in s.split("_"))

def get_go_type(sql_type_raw: str, nullable: bool) -> str:
    sql_type_raw = sql_type_raw.lower().strip()
    # 提取基本类型（去掉括号内容）
    base = re.sub(r'\(.*?\)', '', sql_type_raw).strip()
    # 处理 unsigned
    if "unsigned" in sql_type_raw:
        key = base + " unsigned"
        go_t = SQL_TO_GO.get(key) or SQL_TO_GO.get(base, "any")
    else:
        go_t = SQL_TO_GO.get(base, "any")

    if nullable and go_t not in ("[]byte", "datatypes.JSON"):
        # 使用 sql.Null* 或 *Type
        null_map = {
            "string":  "sql.NullString",
            "int32":   "sql.NullInt32",
            "int64":   "sql.NullInt64",
            "float64": "sql.NullFloat64",
            "bool":    "sql.NullBool",
            "time.Time": "sql.NullTime",
        }
        go_t = null_map.get(go_t, f"*{go_t}")
    return go_t

def get_size(sql_type_raw: str) -> Optional[str]:
    m = re.search(r'\((\d+)\)', sql_type_raw)
    return m.group(1) if m else None

def parse_create_table(sql: str) -> List[Table]:
    tables = []
    # 找所有 CREATE TABLE 块
    blocks = re.findall(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\(([\s\S]+?)\)\s*(?:ENGINE|DEFAULT|COMMENT|;|$)',
        sql, re.IGNORECASE
    )
    if not blocks:
        # 尝试简化匹配
        blocks = re.findall(
            r'CREATE\s+TABLE\s+`?(\w+)`?\s*\(([\s\S]+?)\);',
            sql, re.IGNORECASE
        )

    for table_name, body in blocks:
        table = Table(name=table_name)
        pk_cols = set()

        # 找 PRIMARY KEY
        pk_m = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', body, re.IGNORECASE)
        if pk_m:
            pk_cols = {c.strip().strip('`') for c in pk_m.group(1).split(',')}

        # 找 UNIQUE KEY / UNIQUE INDEX
        for um in re.finditer(r'UNIQUE\s+(?:KEY|INDEX)\s+`?(\w+)`?\s*\(([^)]+)\)', body, re.IGNORECASE):
            idx_name = um.group(1)
            idx_cols = [c.strip().strip('`') for c in um.group(2).split(',')]
            table.unique_indexes.append((idx_name, idx_cols))

        # 找普通 KEY / INDEX
        for km in re.finditer(r'(?<!UNIQUE\s)(?:KEY|INDEX)\s+`?(\w+)`?\s*\(([^)]+)\)', body, re.IGNORECASE):
            idx_name = km.group(1)
            idx_cols = [c.strip().strip('`') for c in km.group(2).split(',')]
            if idx_name.upper() not in ('PRIMARY',):
                table.indexes.append((idx_name, idx_cols))

        # 解析列定义
        col_lines = [l.strip() for l in body.split('\n') if l.strip()]
        for col_line in col_lines:
            # 跳过约束行
            if re.match(r'(PRIMARY|UNIQUE|KEY|INDEX|CONSTRAINT|CHECK)\b', col_line, re.IGNORECASE):
                continue
            # 匹配列: `col_name` TYPE [options] [COMMENT '...']
            cm = re.match(
                r'`?(\w+)`?\s+([a-zA-Z]+(?:\([^)]+\))?(?:\s+unsigned)?)'
                r'(.*?)(?:COMMENT\s+[\'"]([^\'"]*)[\'"])?[,]?\s*$',
                col_line, re.IGNORECASE
            )
            if not cm:
                continue

            col_name = cm.group(1)
            sql_type_raw = cm.group(2).strip()
            rest = cm.group(3) or ""
            comment = cm.group(4) or ""

            nullable = "NOT NULL" not in rest.upper()
            is_auto = "AUTO_INCREMENT" in rest.upper()
            is_pk = col_name in pk_cols or "PRIMARY KEY" in rest.upper()
            if is_pk:
                nullable = False

            has_default = "DEFAULT" in rest.upper()
            default_val = None
            dv_m = re.search(r"DEFAULT\s+(['\"]?[^'\"',\s]+['\"]?)", rest, re.IGNORECASE)
            if dv_m:
                default_val = dv_m.group(1).strip("'\"")

            size = get_size(sql_type_raw)
            go_type = get_go_type(sql_type_raw, nullable and not is_pk)

            # 检查是否在单列唯一索引中
            unique = any(len(cols) == 1 and col_name in cols
                        for _, cols in table.unique_indexes)

            col = Column(
                name=col_name, sql_type=sql_type_raw, go_type=go_type,
                nullable=nullable, is_pk=is_pk, is_auto=is_auto,
                has_default=has_default, default_val=default_val,
                comment=comment, unique=unique, size=size,
            )
            table.columns.append(col)

        if table.columns:
            tables.append(table)

    return tables


def build_gorm_tag(col: Column, table: Table) -> str:
    parts = []

    if col.is_pk:
        parts.append("primaryKey")
        if col.is_auto:
            parts.append("autoIncrement")

    col_type = col.sql_type.lower()
    # 加 type tag（对特殊类型）
    if any(t in col_type for t in ["text", "blob", "json", "enum", "decimal"]):
        parts.append(f"type:{col.sql_type}")
    elif col.size and "varchar" in col_type:
        parts.append(f"size:{col.size}")

    if not col.nullable and not col.is_pk:
        parts.append("not null")

    if col.unique:
        parts.append("uniqueIndex")

    # 普通索引
    for idx_name, idx_cols in table.indexes:
        if col.name in idx_cols:
            if len(idx_cols) == 1:
                parts.append(f"index:{idx_name}")
            else:
                pos = idx_cols.index(col.name) + 1
                parts.append(f"index:{idx_name},priority:{pos}")

    # 复合唯一索引
    for idx_name, idx_cols in table.unique_indexes:
        if col.name in idx_cols and len(idx_cols) > 1:
            pos = idx_cols.index(col.name) + 1
            parts.append(f"uniqueIndex:{idx_name},priority:{pos}")

    if col.has_default and col.default_val is not None:
        parts.append(f"default:{col.default_val}")

    if col.comment:
        parts.append(f"comment:{col.comment}")

    return f'gorm:"{";".join(parts)}"' if parts else ""


def generate_struct(table: Table) -> str:
    struct_name = snake_to_pascal(table.name)

    # 检测是否可以用 gorm.Model
    col_names = {c.name for c in table.columns}
    use_gorm_model = {"id", "created_at", "updated_at", "deleted_at"}.issubset(col_names)

    imports = {"time"}
    lines = []
    lines.append(f"// {struct_name} 对应表 {table.name}")
    lines.append(f"type {struct_name} struct {{")

    if use_gorm_model:
        lines.append("\tgorm.Model")
        skip = {"id", "created_at", "updated_at", "deleted_at"}
    else:
        skip = set()

    for col in table.columns:
        if col.name in skip:
            continue

        field_name = snake_to_pascal(col.name)
        go_type = col.go_type

        # 收集 import
        if "time.Time" in go_type:
            imports.add("time")
        if "sql.Null" in go_type:
            imports.add("database/sql")
        if "datatypes.JSON" in go_type:
            imports.add("gorm.io/datatypes")

        gorm_tag = build_gorm_tag(col, table)
        json_tag = f'json:"{col.name}"'

        tag_str = f'`{gorm_tag} {json_tag}`' if gorm_tag else f'`{json_tag}`'

        comment = f"  // {col.comment}" if col.comment else ""
        lines.append(f"\t{field_name:<24} {go_type:<20} {tag_str}{comment}")

    lines.append("}")
    lines.append("")

    # 生成 TableName 方法（如果没用 gorm.Model 或表名不规范）
    expected_table = table.name
    if not use_gorm_model:
        lines.append(f"func ({struct_name[0].lower()} {struct_name}) TableName() string {{")
        lines.append(f'\treturn "{expected_table}"')
        lines.append("}")
        lines.append("")

    # 导入头
    import_lines = ["package model", "", "import ("]
    import_lines.append('\t"gorm.io/gorm"')
    for imp in sorted(imports):
        if imp != "time" or "time.Time" in "\n".join(lines):
            if imp not in ("gorm.io/datatypes",):
                import_lines.append(f'\t"{imp}"')
    if "gorm.io/datatypes" in "\n".join(lines):
        import_lines.append('\t"gorm.io/datatypes"')
    import_lines.append(")")
    import_lines.append("")

    return "\n".join(import_lines + lines)


def parse_fields_arg(table_name: str, fields_str: str) -> Table:
    """--fields "id:bigint,name:varchar(100)" 简化模式"""
    table = Table(name=table_name)
    for item in fields_str.split(","):
        item = item.strip()
        if ":" not in item:
            continue
        col_name, sql_type = item.split(":", 1)
        col_name = col_name.strip()
        sql_type = sql_type.strip()
        is_pk = col_name == "id"
        nullable = not is_pk
        go_type = get_go_type(sql_type, nullable)
        table.columns.append(Column(
            name=col_name, sql_type=sql_type, go_type=go_type,
            nullable=nullable, is_pk=is_pk, is_auto=is_pk,
            has_default=False, default_val=None,
            comment="", unique=False,
            size=get_size(sql_type),
        ))
    return table


def main():
    parser = argparse.ArgumentParser(description="SQL -> GORM struct 生成器")
    parser.add_argument("file", nargs="?", default="-", help="SQL 文件路径，- 表示 stdin")
    parser.add_argument("--table", help="表名（配合 --fields 使用）")
    parser.add_argument("--fields", help="字段列表，格式: name:type,name:type")
    parser.add_argument("--dialect", choices=["mysql", "pg"], default="mysql",
                        help="SQL 方言: mysql（默认）或 pg（PostgreSQL）")
    args = parser.parse_args()

    # 切换方言
    global SQL_TO_GO
    if args.dialect == "pg":
        SQL_TO_GO = SQL_TO_GO_PG
        print("# [gen_model] 使用 PostgreSQL 类型映射", file=sys.stderr)
    else:
        SQL_TO_GO = SQL_TO_GO_MYSQL

    if args.table and args.fields:
        table = parse_fields_arg(args.table, args.fields)
        print(generate_struct(table))
        return

    if args.file == "-":
        sql = sys.stdin.read()
    else:
        with open(args.file, encoding="utf-8") as f:
            sql = f.read()

    tables = parse_create_table(sql)
    if not tables:
        print("❌ 未找到有效的 CREATE TABLE 语句", file=sys.stderr)
        print("  支持格式: CREATE TABLE `name` (...) ENGINE=...", file=sys.stderr)
        sys.exit(1)

    for table in tables:
        print(generate_struct(table))
        print("// " + "─" * 60)


if __name__ == "__main__":
    main()

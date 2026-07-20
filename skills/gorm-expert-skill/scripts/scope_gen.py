#!/usr/bin/env python3
"""
scope_gen.py — 根据 GORM struct 字段自动生成常用 Scope 函数模板
用法:
  python3 scope_gen.py model.go
  cat model.go | python3 scope_gen.py -
  python3 scope_gen.py model.go --tenant   # 额外生成多租户 Scope
  python3 scope_gen.py model.go --paginate # 额外生成分页 Scope
"""

import sys
import re
import argparse
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Field:
    name: str        # Go 字段名，如 Status
    go_type: str     # Go 类型，如 string / uint / time.Time
    col_name: str    # 数据库列名（snake_case），如 status

# ── snake_case 转换 ──────────────────────────────────────────────────────────
def to_snake(name: str) -> str:
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return s.lower()

# ── 从 Go struct 提取字段 ────────────────────────────────────────────────────
def parse_struct(code: str) -> List[tuple]:
    """返回 [(struct_name, [Field]), ...]"""
    results = []
    # 匹配 type XxxStruct struct { ... }
    struct_pat = re.compile(
        r'type\s+(\w+)\s+struct\s*\{([^}]+)\}', re.DOTALL)
    for m in struct_pat.finditer(code):
        struct_name = m.group(1)
        body = m.group(2)
        fields = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            # 跳过嵌入类型（gorm.Model 等）
            if re.match(r'^[a-z]', line) or re.match(r'^\w+\.\w+$', line.split()[0] if line.split() else ''):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            fname = parts[0]
            ftype = parts[1]
            # 从 gorm tag 提取 column 名
            col_match = re.search(r'gorm:"[^"]*column:(\w+)', line)
            col_name = col_match.group(1) if col_match else to_snake(fname)
            fields.append(Field(name=fname, go_type=ftype, col_name=col_name))
        if fields:
            results.append((struct_name, fields))
    return results

# ── 生成等值查询 Scope ────────────────────────────────────────────────────────
def gen_eq_scope(struct_name: str, f: Field) -> Optional[str]:
    """WHERE col = ? 类型的 Scope"""
    receiver = struct_name[0].lower()
    param = f.name[0].lower() + f.name[1:]
    return (
        f"// {struct_name}By{f.name} 按 {f.col_name} 精确匹配\n"
        f"func ({receiver} {struct_name}) By{f.name}(val {f.go_type}) func(*gorm.DB) *gorm.DB {{\n"
        f'\treturn func(db *gorm.DB) *gorm.DB {{\n'
        f'\t\treturn db.Where("{f.col_name} = ?", val)\n'
        f'\t}}\n'
        f'}}'
    )

# ── 生成范围查询 Scope（数字/时间字段）──────────────────────────────────────
def gen_range_scope(struct_name: str, f: Field) -> Optional[str]:
    receiver = struct_name[0].lower()
    numeric_types = {"int", "int8", "int16", "int32", "int64",
                     "uint", "uint8", "uint16", "uint32", "uint64",
                     "float32", "float64"}
    if f.go_type not in numeric_types and "time.Time" not in f.go_type:
        return None
    return (
        f"// {struct_name}{f.name}Between 按 {f.col_name} 范围查询\n"
        f"func ({receiver} {struct_name}) {f.name}Between(from, to {f.go_type}) func(*gorm.DB) *gorm.DB {{\n"
        f'\treturn func(db *gorm.DB) *gorm.DB {{\n'
        f'\t\treturn db.Where("{f.col_name} BETWEEN ? AND ?", from, to)\n'
        f'\t}}\n'
        f'}}'
    )

# ── 生成 IN 查询 Scope ────────────────────────────────────────────────────────
def gen_in_scope(struct_name: str, f: Field) -> str:
    receiver = struct_name[0].lower()
    return (
        f"// {struct_name}{f.name}In 按 {f.col_name} IN 批量查询\n"
        f"func ({receiver} {struct_name}) {f.name}In(vals ...{f.go_type}) func(*gorm.DB) *gorm.DB {{\n"
        f'\treturn func(db *gorm.DB) *gorm.DB {{\n'
        f'\t\treturn db.Where("{f.col_name} IN ?", vals)\n'
        f'\t}}\n'
        f'}}'
    )

# ── 生成分页 Scope ────────────────────────────────────────────────────────────
PAGINATE_SCOPE = '''\
// Paginate 通用分页 Scope（Page 从 1 开始）
type PageQuery struct {
\tPage     int
\tPageSize int
}

func Paginate(q PageQuery) func(*gorm.DB) *gorm.DB {
\treturn func(db *gorm.DB) *gorm.DB {
\t\tif q.PageSize <= 0 {
\t\t\tq.PageSize = 20
\t\t}
\t\tif q.PageSize > 200 {
\t\t\tq.PageSize = 200
\t\t}
\t\toffset := (q.Page - 1) * q.PageSize
\t\treturn db.Offset(offset).Limit(q.PageSize)
\t}
}'''

# ── 生成多租户 Scope ─────────────────────────────────────────────────────────
TENANT_SCOPE = '''\
// TenantScope 多租户行级隔离 Scope（从 context 中读取 tenant_id）
func TenantScope(ctx context.Context) func(*gorm.DB) *gorm.DB {
\treturn func(db *gorm.DB) *gorm.DB {
\t\ttenantID, ok := ctx.Value("tenant_id").(uint)
\t\tif !ok || tenantID == 0 {
\t\t\treturn db.Where("1 = 0") // 无租户信息时拒绝访问
\t\t}
\t\treturn db.Where("tenant_id = ?", tenantID)
\t}
}'''

# ── 决定哪些字段需要生成 Scope ───────────────────────────────────────────────
SKIP_FIELDS = {"ID", "CreatedAt", "UpdatedAt", "DeletedAt", "Password",
               "Salt", "Token", "Secret"}
ENUM_LIKE = {"Status", "Type", "State", "Role", "Kind", "Category"}

def should_generate(f: Field) -> bool:
    if f.name in SKIP_FIELDS:
        return False
    if f.go_type in ("[]byte", "datatypes.JSON"):
        return False
    return True

# ── 主函数 ────────────────────────────────────────────────────────────────────
def generate(code: str, with_tenant: bool, with_paginate: bool) -> str:
    structs = parse_struct(code)
    if not structs:
        return "// ⚠️ 未找到 Go struct 定义，请检查输入内容\n"

    lines = [
        "package model",
        "",
        'import "gorm.io/gorm"',
        "",
    ]
    if with_tenant:
        lines += ['import "context"', ""]
    lines += ["// ── 自动生成的 Scope 函数（scope_gen.py）─────────────────────", ""]

    if with_paginate:
        lines += [PAGINATE_SCOPE, ""]

    if with_tenant:
        lines += [TENANT_SCOPE, ""]

    for struct_name, fields in structs:
        lines.append(f"// ── {struct_name} Scopes ────────────────────────────────────")
        for f in fields:
            if not should_generate(f):
                continue
            # 等值查询
            lines.append(gen_eq_scope(struct_name, f))
            lines.append("")
            # IN 查询（枚举/ID 类字段）
            if f.name in ENUM_LIKE or f.go_type in ("uint", "uint64", "int64", "string"):
                lines.append(gen_in_scope(struct_name, f))
                lines.append("")
            # 范围查询（数字/时间）
            r = gen_range_scope(struct_name, f)
            if r:
                lines.append(r)
                lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GORM Scope 生成器")
    parser.add_argument("file", nargs="?", default="-",
                        help="Go 文件路径，- 表示 stdin")
    parser.add_argument("--tenant", action="store_true",
                        help="生成多租户 TenantScope")
    parser.add_argument("--paginate", action="store_true",
                        help="生成分页 Paginate Scope")
    args = parser.parse_args()

    if args.file == "-":
        code = sys.stdin.read()
    else:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()

    print(generate(code, with_tenant=args.tenant, with_paginate=args.paginate))


if __name__ == "__main__":
    main()

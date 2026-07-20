#!/usr/bin/env python3
"""
query_explain.py — SQL 查询静态分析，给出索引使用建议，无需连接数据库
用法:
  python3 query_explain.py "SELECT * FROM users WHERE name LIKE '%foo%'"
  python3 query_explain.py - <<< "SELECT ..."
  python3 query_explain.py query.sql
"""

import sys
import re
import argparse
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Finding:
    level: str       # ERROR / WARN / INFO / OK
    rule: str
    detail: str
    suggestion: str
    rewrite: Optional[str] = None  # 优化后的 SQL 示例

def normalize(sql: str) -> str:
    sql = re.sub(r'--[^\n]*', '', sql)          # 去注释
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    sql = re.sub(r'\s+', ' ', sql).strip().upper()
    return sql

def analyze_sql(raw_sql: str) -> List[Finding]:
    findings: List[Finding] = []
    sql = normalize(raw_sql)
    sql_orig = raw_sql.strip()

    # ── R1: SELECT * ─────────────────────────────────────────────────────────
    if re.search(r'SELECT\s+\*', sql):
        findings.append(Finding(
            level="WARN", rule="SELECT_STAR",
            detail="SELECT * 传输所有列，阻止覆盖索引优化",
            suggestion="明确列出需要的字段，如 SELECT id, name, status",
            rewrite=re.sub(r'SELECT\s+\*', 'SELECT id, <col1>, <col2>', sql_orig, count=1, flags=re.IGNORECASE)
        ))

    # ── R2: 前导通配符 LIKE '%...' ────────────────────────────────────────────
    if re.search(r"LIKE\s+['\"%]%", sql):
        findings.append(Finding(
            level="ERROR", rule="LEADING_WILDCARD",
            detail="LIKE '%keyword' 或 LIKE '%keyword%' 无法使用 B-Tree 索引，触发全表扫描",
            suggestion="① 改为前缀匹配 LIKE 'keyword%'  ② 或使用全文索引 MATCH(col) AGAINST('keyword')",
            rewrite=re.sub(r"LIKE\s+'%([^']+)%'", r"LIKE '\1%'", sql_orig, flags=re.IGNORECASE)
        ))

    # ── R3: 大 OFFSET ─────────────────────────────────────────────────────────
    m = re.search(r'\bOFFSET\s+(\d+)', sql)
    if m and int(m.group(1)) > 10000:
        val = m.group(1)
        findings.append(Finding(
            level="ERROR", rule="LARGE_OFFSET",
            detail=f"OFFSET {val} 需要扫描并丢弃前 {val} 行，性能随页数线性下降",
            suggestion="改用游标分页: WHERE id > :last_id ORDER BY id LIMIT n",
            rewrite=re.sub(r'LIMIT\s+\d+\s+OFFSET\s+\d+',
                           'WHERE id > :last_id ORDER BY id LIMIT <page_size>',
                           sql_orig, flags=re.IGNORECASE)
        ))

    # ── R4: 函数包裹索引列 ────────────────────────────────────────────────────
    func_patterns = [
        (r'\bDATE\s*\(\s*(\w+)\s*\)', "DATE({col})"),
        (r'\bYEAR\s*\(\s*(\w+)\s*\)', "YEAR({col})"),
        (r'\bLOWER\s*\(\s*(\w+)\s*\)', "LOWER({col})"),
        (r'\bUPPER\s*\(\s*(\w+)\s*\)', "UPPER({col})"),
        (r'\bDATEFORMAT\s*\(', "DATE_FORMAT(...)"),
        (r'\bSUBSTR\s*\(', "SUBSTR(col, ...)"),
        (r'\bCAST\s*\(', "CAST(col AS ...)"),
    ]
    for pattern, name in func_patterns:
        if re.search(pattern, sql):
            findings.append(Finding(
                level="WARN", rule="FUNC_ON_INDEXED_COL",
                detail=f"WHERE 子句中对列使用 {name}，会使该列索引失效",
                suggestion=(
                    f"① 改为范围查询，如 {name} 中 DATE(created_at)='2024-01-01' → "
                    "created_at >= '2024-01-01' AND created_at < '2024-01-02'\n"
                    "   ② 或创建函数索引（MySQL 8.0+）: CREATE INDEX ON t((LOWER(col)))"
                )
            ))
            break

    # ── R5: OR 条件跨列（可能导致全表） ──────────────────────────────────────
    if re.search(r'\bWHERE\b.*\bOR\b', sql):
        # 检测 OR 两侧是不同列
        findings.append(Finding(
            level="INFO", rule="OR_CONDITION",
            detail="OR 条件跨列时，MySQL 可能无法利用组合索引，退化为全表扫描",
            suggestion=(
                "① 确认 OR 的每个分支都有独立索引  "
                "② 或改用 UNION ALL:\n"
                "   SELECT ... WHERE col1 = ? UNION ALL SELECT ... WHERE col2 = ?"
            )
        ))

    # ── R6: NOT IN / NOT EXISTS（可能索引失效） ───────────────────────────────
    if re.search(r'\bNOT\s+IN\b', sql):
        findings.append(Finding(
            level="WARN", rule="NOT_IN",
            detail="NOT IN 在子查询返回 NULL 时结果集为空；大集合时性能差",
            suggestion="改用 LEFT JOIN ... WHERE right.id IS NULL，或 NOT EXISTS（更直观，优化器更好处理）"
        ))

    # ── R7: SELECT 中有子查询（相关子查询） ──────────────────────────────────
    if re.search(r'SELECT\s+.*\(SELECT\b', sql, re.DOTALL):
        findings.append(Finding(
            level="WARN", rule="CORRELATED_SUBQUERY",
            detail="SELECT 列表中的子查询是相关子查询，每行都执行一次，复杂度 O(N²)",
            suggestion="改写为 JOIN 或 LEFT JOIN，让优化器做 Hash/Merge Join"
        ))

    # ── R8: 无 WHERE 的 UPDATE / DELETE ──────────────────────────────────────
    if re.search(r'\b(UPDATE|DELETE)\b', sql) and not re.search(r'\bWHERE\b', sql):
        findings.append(Finding(
            level="ERROR", rule="UPDATE_DELETE_NO_WHERE",
            detail="UPDATE/DELETE 没有 WHERE 条件，将影响全表所有行！",
            suggestion="添加 WHERE 条件。如确实需要全表操作，用 WHERE 1=1 明确标注意图"
        ))

    # ── R9: ORDER BY + LIMIT 无索引支持 ──────────────────────────────────────
    if re.search(r'\bORDER\s+BY\b', sql) and re.search(r'\bLIMIT\b', sql):
        order_m = re.search(r'ORDER\s+BY\s+([\w\s,]+?)(?:\s+LIMIT|\s*$)', sql)
        if order_m:
            order_cols = [c.strip().rstrip('ASC').rstrip('DESC').strip()
                         for c in order_m.group(1).split(',')]
            findings.append(Finding(
                level="INFO", rule="ORDER_BY_LIMIT",
                detail=f"ORDER BY {', '.join(order_cols)} + LIMIT：需确认排序列有索引，否则触发 filesort",
                suggestion=f"确认索引包含排序列: CREATE INDEX idx ON table({', '.join(order_cols)})\n"
                           "用 EXPLAIN 验证 Extra 列是否出现 'Using filesort'"
            ))

    # ── R10: IN 子查询建议改 EXISTS ──────────────────────────────────────────
    if re.search(r'\bIN\s*\(SELECT\b', sql):
        findings.append(Finding(
            level="INFO", rule="IN_SUBQUERY",
            detail="IN (SELECT ...) 在旧版 MySQL 优化器处理较差，可能不走索引",
            suggestion="改用 EXISTS 或 JOIN:\n"
                       "  WHERE EXISTS (SELECT 1 FROM t2 WHERE t2.id = t1.id)"
        ))

    # ── R11: 隐式类型转换 ─────────────────────────────────────────────────────
    # 简单检测：WHERE string_col = 123（字符串列用数字）
    if re.search(r"WHERE\s+\w+\s*=\s*\d+(?!\s*\.\d)", sql):
        findings.append(Finding(
            level="INFO", rule="IMPLICIT_TYPE_CAST",
            detail="WHERE 条件右侧为数字字面量，若列类型为 VARCHAR，会导致隐式转换使索引失效",
            suggestion="确保参数类型与列类型一致: WHERE phone = '13812345678' (加引号)"
        ))

    return findings


def estimate_complexity(sql: str) -> str:
    """粗略估算查询复杂度"""
    s = normalize(sql)
    score = 0
    notes = []

    joins = len(re.findall(r'\bJOIN\b', s))
    if joins > 0:
        score += joins * 2
        notes.append(f"{joins} 个 JOIN")

    subqueries = len(re.findall(r'\(SELECT\b', s))
    if subqueries > 0:
        score += subqueries * 3
        notes.append(f"{subqueries} 个子查询")

    if re.search(r'\bGROUP\s+BY\b', s):
        score += 2
        notes.append("GROUP BY")

    if re.search(r'\bORDER\s+BY\b', s):
        score += 1
        notes.append("ORDER BY")

    if re.search(r'\bDISTINCT\b', s):
        score += 2
        notes.append("DISTINCT")

    if score == 0:
        return "🟢 简单查询"
    elif score <= 4:
        return f"🟡 中等复杂度（{', '.join(notes)}）"
    else:
        return f"🔴 高复杂度（{', '.join(notes)}）— 建议用 EXPLAIN ANALYZE 实测"


def format_output(sql: str, findings: List[Finding]) -> str:
    level_icon = {"ERROR": "🔴", "WARN": "🟡", "INFO": "🔵", "OK": "✅"}
    lines = []

    complexity = estimate_complexity(sql)
    lines.append(f"复杂度评估: {complexity}\n")

    if not findings:
        lines.append("✅ 未发现明显 SQL 反模式")
        return "\n".join(lines)

    lines.append(f"发现 {len(findings)} 个问题:\n")
    for f in findings:
        icon = level_icon.get(f.level, "⚪")
        lines.append(f"{icon} [{f.level}] {f.rule}")
        lines.append(f"   问题: {f.detail}")
        lines.append(f"   建议: {f.suggestion}")
        if f.rewrite and f.rewrite.upper() != sql.upper()[:len(f.rewrite)]:
            lines.append(f"   改写参考: {f.rewrite[:200]}")
        lines.append("")

    lines.append("💡 运行 EXPLAIN 验证:")
    lines.append(f"   EXPLAIN FORMAT=JSON {sql.strip()[:200]};")
    lines.append("   关注: type(全表=ALL), Extra(Using filesort / Using temporary)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SQL 查询静态分析器")
    parser.add_argument("input", nargs="?", default="-",
                        help="SQL 字符串、文件路径或 - 表示 stdin")
    args = parser.parse_args()

    if args.input == "-":
        sql = sys.stdin.read().strip()
    elif args.input.endswith(".sql"):
        with open(args.input, encoding="utf-8") as f:
            sql = f.read().strip()
    else:
        sql = args.input.strip()

    if not sql:
        print("❌ 请提供 SQL 语句", file=sys.stderr)
        sys.exit(1)

    findings = analyze_sql(sql)
    print(format_output(sql, findings))

    if any(f.level == "ERROR" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()

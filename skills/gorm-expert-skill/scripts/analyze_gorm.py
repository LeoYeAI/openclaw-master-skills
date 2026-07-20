#!/usr/bin/env python3
"""
analyze_gorm.py — 静态分析 Go 代码中的 GORM 反模式（R1–R27）
用法:
  python3 analyze_gorm.py <go_file>
  cat main.go | python3 analyze_gorm.py -

退出码: 有 ERROR 级别问题时返回 1，方便 CI 集成
"""

import sys
import re
import json
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Issue:
    level: str      # ERROR / WARN / INFO
    rule: str
    line: int       # 0 = 文件级别（非行级）
    snippet: str
    suggestion: str


# ═══════════════════════════════════════════════════════════════════════════════
# 逐行规则（R1–R10, R13, R14, R16, R17, R18a）
# ═══════════════════════════════════════════════════════════════════════════════

def check_per_line(lines: List[str]) -> List[Issue]:
    issues: List[Issue] = []
    in_tx_block = False
    tx_indent = 0

    for i, line in enumerate(lines, 1):
        s = line.strip()

        # ── R1: SELECT *（Find 未指定字段）─────────────────────────────────
        if re.search(r'\.(Find|First|Last|Take)\s*\(', s) and \
           not re.search(r'\.Select\s*\(', s) and \
           not re.search(r'\.Raw\s*\(', s):
            ctx = "\n".join(lines[max(0, i-4):i])
            if ".Select(" not in ctx:
                issues.append(Issue("WARN", "SELECT_STAR", i, s,
                    "添加 .Select(\"id\",\"name\",...) 只查需要字段，减少数据传输和内存分配"))

        # ── R2: OFFSET 大分页 ────────────────────────────────────────────────
        m = re.search(r'\.Offset\s*\(\s*(\w+)', s)
        if m:
            val = m.group(1)
            if val.isdigit() and int(val) > 1000:
                issues.append(Issue("ERROR", "LARGE_OFFSET", i, s,
                    f"Offset({val}) 导致全表扫描前 N 行，改用游标分页: WHERE id > lastID ORDER BY id LIMIT n"))
            elif not val.isdigit():
                issues.append(Issue("WARN", "DYNAMIC_OFFSET", i, s,
                    "动态 Offset 在大表上性能急剧下降，建议改为游标分页（WHERE id > lastID）"))

        # ── R3: 循环内 DB 操作（N+1）────────────────────────────────────────
        if re.search(r'for\s+.+range\s+', s):
            window = lines[i:min(i+8, len(lines))]
            for j, wl in enumerate(window):
                if re.search(r'\b(db|tx)\.(Find|First|Create|Save|Update|Delete)\b', wl):
                    issues.append(Issue("ERROR", "N_PLUS_1", i+j+1, wl.strip(),
                        "循环内 DB 操作 = N+1 查询。改用 Preload / Joins 批量加载，"
                        "或先收集 ID 再 WHERE id IN (?)"))
                    break

        # ── R4: struct Updates（零值丢失）───────────────────────────────────
        if re.search(r'\.Updates\s*\(\s*\w+\s*\{', s):
            issues.append(Issue("WARN", "STRUCT_UPDATES_ZERO_VALUE", i, s,
                "Updates(struct{}) 忽略零值字段（int=0, bool=false）。"
                "改用 Updates(map[string]any{\"field\": value})"))

        # ── R5: 未带 WithContext ─────────────────────────────────────────────
        if re.search(r'\b(db)\.(Find|First|Create|Update|Delete|Exec|Raw)\b', s) and \
           "WithContext" not in s and ".Session(" not in s:
            if not any(iss.rule == "NO_CONTEXT" for iss in issues):
                issues.append(Issue("INFO", "NO_CONTEXT", i, s,
                    "建议所有 DB 操作传入 ctx: db.WithContext(ctx).Find(...)，支持超时取消和链路追踪"))

        # ── R6: 未检查 Error ─────────────────────────────────────────────────
        if re.search(r'\b(db|tx)\.(Find|First|Create|Save|Update|Delete|Exec)\b.*\)', s):
            next_line = lines[i].strip() if i < len(lines) else ""
            if ".Error" not in s and "err" not in s.lower() \
               and ".Error" not in next_line and "err" not in next_line.lower():
                issues.append(Issue("WARN", "UNCHECKED_ERROR", i, s,
                    "未检查 DB 错误。应: if err := db.WithContext(ctx).Find(&u).Error; err != nil { ... }"))

        # ── R7: Find 全表（无 Where/Limit）──────────────────────────────────
        if re.search(r'\.(Find)\s*\(&\w+\)\s*$', s) and "Where" not in s:
            ctx = "\n".join(lines[max(0, i-5):i])
            if ".Where(" not in ctx and ".Limit(" not in ctx:
                issues.append(Issue("WARN", "FIND_ALL_NO_LIMIT", i, s,
                    "Find 无 Where/Limit 会全表扫描。大表请用 FindInBatches"))

        # ── R8: 事务内耗时 IO 操作 ───────────────────────────────────────────
        if re.search(r'db\.(Transaction|Begin)\(', s):
            block = "\n".join(lines[i:min(i+30, len(lines))])
            for pat, name in [
                (r'http\.(Get|Post|Do)\(', "HTTP 请求"),
                (r'time\.Sleep\(', "time.Sleep"),
                (r'grpc\.|\.Invoke\(', "gRPC 调用"),
            ]:
                if re.search(pat, block):
                    issues.append(Issue("ERROR", "SLOW_OP_IN_TX", i, s,
                        f"事务内发现 {name}，长时间持有 DB 连接/锁。IO 操作应移到事务外"))
                    break

        # ── R9: LIKE '%xxx%' 前导通配 ────────────────────────────────────────
        if re.search(r'LIKE\s+["\']%[^%]+%["\']', s, re.IGNORECASE):
            issues.append(Issue("WARN", "LEADING_WILDCARD_LIKE", i, s,
                "'%keyword%' 无法走索引，触发全表扫描。"
                "用前缀匹配 'keyword%' 或全文索引 MATCH AGAINST"))

        # ── R10: 循环内逐条 Create ────────────────────────────────────────────
        if re.search(r'for\s+.+range\s+', s):
            window = lines[i:min(i+5, len(lines))]
            for wl in window:
                if re.search(r'\.(Create)\s*\(', wl) and "Batches" not in wl:
                    issues.append(Issue("ERROR", "LOOP_CREATE", i, wl.strip(),
                        "循环内逐条 Create = N 次 INSERT。改用 db.CreateInBatches(&slice, 200)"))
                    break

        # ── R13: Raw/Exec 字符串拼接（SQL 注入）─────────────────────────────
        if re.search(r'\.(Raw|Exec)\s*\(', s):
            if re.search(r'["\']\s*\+\s*\w|fmt\.Sprintf', s):
                issues.append(Issue("ERROR", "SQL_INJECTION_RISK", i, s,
                    "Raw/Exec 字符串拼接存在 SQL 注入风险。"
                    "改用占位符: db.Raw(\"SELECT * FROM t WHERE id = ?\", id)"))

        # ── R14: Pluck 多列误用 ──────────────────────────────────────────────
        if re.search(r'\.Pluck\s*\(\s*["\']\w+,\s*\w+', s):
            issues.append(Issue("WARN", "PLUCK_MULTI_COLUMN", i, s,
                "Pluck 只支持单列。提取多列改用 .Select(\"col1,col2\").Scan(&result)"))

        # ── R16: 软删除 Delete 未用 Unscoped ────────────────────────────────
        if re.search(r'\.(Delete)\s*\(', s) and "Unscoped" not in s:
            if not any(iss.rule == "SOFT_DELETE_REMINDER" for iss in issues):
                issues.append(Issue("INFO", "SOFT_DELETE_REMINDER", i, s,
                    "含 DeletedAt 的 Model Delete 只做软删除。硬删除用 db.Unscoped().Delete(&model)"))

        # ── R17: 事务块内使用 db 而非 tx ─────────────────────────────────────
        if re.search(r'db\.(Transaction|Begin)\(', s):
            in_tx_block = True
            tx_indent = len(line) - len(line.lstrip())
        elif in_tx_block:
            cur_indent = len(line) - len(line.lstrip())
            if s and cur_indent <= tx_indent and re.search(r'^[})]', s):
                in_tx_block = False
            elif re.search(r'\bdb\.(Find|First|Create|Save|Update|Delete|Exec|Raw)\b', s):
                if not any(iss.rule == "DB_IN_TX_BLOCK" for iss in issues):
                    issues.append(Issue("ERROR", "DB_IN_TX_BLOCK", i, s,
                        "事务块内使用全局 db 而非 tx，该操作不在事务内！"
                        "改用 tx.Create(...) / tx.Find(...)"))

        # ── R18a: foreignKey tag 未加 constraint:false（逐行检测）────────────
        if re.search(r'gorm:"[^"]*foreignKey:', s, re.IGNORECASE):
            if "constraint:false" not in s.lower():
                issues.append(Issue("ERROR", "PHYSICAL_FOREIGN_KEY", i, s,
                    '禁止物理外键约束。改为: gorm:"foreignKey:UserID;constraint:false"\n'
                    "   并在 gorm.Config 设置 DisableForeignKeyConstraintWhenMigrating: true"))

        # ── R27: references tag 未加 constraint:false（物理外键变体）────────
        if re.search(r'gorm:"[^"]*references:', s, re.IGNORECASE):
            if "constraint:false" not in s.lower():
                issues.append(Issue("ERROR", "PHYSICAL_FK_REFERENCES", i, s,
                    '禁止物理外键约束。含 references: 的 tag 必须同时加 constraint:false\n'
                    '   改为: gorm:"foreignKey:UserID;references:ID;constraint:false"'))

        # ── R22: Where 字符串拼接（SQL 注入）──────────────────────────────────
        if re.search(r'\.Where\s*\(', s):
            if re.search(r'["\']\s*\+\s*\w|fmt\.Sprintf', s):
                issues.append(Issue("ERROR", "WHERE_SQL_INJECTION", i, s,
                    "Where 字符串拼接存在 SQL 注入风险。"
                    "改用占位符: db.Where(\"name = ?\", name)"))

        # ── R23: 未检查 RowsAffected ──────────────────────────────────────────
        if re.search(r'\b(db|tx)\.(Update|Delete)\s*\(', s) and \
           "Updates" not in s:
            next_lines = "\n".join(lines[i:min(i+3, len(lines))])
            if "RowsAffected" not in next_lines and "RowsAffected" not in s:
                if not any(iss.rule == "UNCHECKED_ROWS_AFFECTED" for iss in issues):
                    issues.append(Issue("INFO", "UNCHECKED_ROWS_AFFECTED", i, s,
                        "Update/Delete 后建议检查 RowsAffected 确认影响行数，"
                        "避免静默无效更新: result := db.Update(...); if result.RowsAffected == 0 { ... }"))

        # ── R24: Save 可能导致全量更新 ────────────────────────────────────────
        if re.search(r'\b(db|tx)\.Save\s*\(', s):
            if not any(iss.rule == "SAVE_FULL_UPDATE" for iss in issues):
                issues.append(Issue("INFO", "SAVE_FULL_UPDATE", i, s,
                    "Save 会更新所有字段（含零值），性能差且可能意外覆盖数据。"
                    "只更新特定字段用: db.Model(&v).Updates(map[string]any{\"field\": val})"))

        # ── R25: AutoMigrate 在非初始化代码中使用 ──────────────────────────────
        if re.search(r'\.AutoMigrate\s*\(', s):
            if not re.search(r'func\s+(init|main|setup|Init|Setup|Migrate)\b',
                             "\n".join(lines[max(0, i-20):i])):
                issues.append(Issue("WARN", "AUTO_MIGRATE_IN_BUSINESS", i, s,
                    "AutoMigrate 不应在业务代码中调用，仅在 init/main/setup 函数中使用。"
                    "生产环境推荐 golang-migrate 管理 DDL"))

        # ── R26: 大 IN 子句（超过 1000 个元素）──────────────────────────────────
        if re.search(r'\.Where\s*\([^)]*\bIN\b', s, re.IGNORECASE):
            # 检查紧邻的切片变量是否可能很大（无法静态确定大小，仅提醒）
            if not any(iss.rule == "LARGE_IN_CLAUSE" for iss in issues):
                # 检测显式大切片字面量或常见的 ids 变量
                ctx_block = "\n".join(lines[max(0, i-5):i])
                if re.search(r'(allIDs|allIds|ALL_IDS|ids\s*=\s*\w+\()', ctx_block):
                    issues.append(Issue("WARN", "LARGE_IN_CLAUSE", i, s,
                        "IN 子句元素过多会导致 SQL 过长或超过 max_allowed_packet。"
                        "建议限制 IN 子句大小（≤1000），超限时分批查询或改用 JOIN 临时表"))

    # ── R19: *gorm.DB 跨 goroutine 共享（goroutine 不安全）────────────────
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if re.search(r'\bgo\s+func\s*\(', s):
            block = "\n".join(lines[i:min(i+15, len(lines))])
            if re.search(r'\b(db|baseDB|queryDB)\.(Find|First|Create|Update|Delete|Where)\b', block):
                if "Session(" not in block and "NewDB" not in block:
                    issues.append(Issue("WARN", "GOROUTINE_DB_UNSAFE", i, s,
                        "goroutine 内使用外部 *gorm.DB 实例存在数据竞争风险。"
                        "应在 goroutine 内用 db.Session(&gorm.Session{NewDB:true}) 创建独立副本"))
                    break

    # ── R20: 复用 *gorm.DB 未 Session 隔离导致条件累积──────────────────
    db_ops_lines = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if re.search(r'\b(db|queryDB|baseDB)\.(Find|First|Take|Count)\b', s):
            db_ops_lines.append((i, s))
    for idx in range(len(db_ops_lines) - 1):
        line_a_no, _ = db_ops_lines[idx]
        line_b_no, line_b = db_ops_lines[idx + 1]
        if line_b_no - line_a_no <= 10:
            between = "\n".join(lines[line_a_no:line_b_no-1])
            if "Session(" not in between and "NewDB" not in between:
                if not any(iss.rule == "DB_CONDITION_ACCUMULATION" for iss in issues):
                    issues.append(Issue("INFO", "DB_CONDITION_ACCUMULATION", line_b_no, line_b,
                        "多次复用同一 *gorm.DB 实例查询，可能导致 WHERE 条件累积。"
                        "两次查询之间应用 db.Session(&gorm.Session{NewDB:true}) 隔离"))

    # ── R21: 使用 v1 的 gorm.IsRecordNotFoundError（v2 已移除）──────────
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if "gorm.IsRecordNotFoundError" in s:
            issues.append(Issue("ERROR", "V1_NOT_FOUND_API", i, s,
                "gorm.IsRecordNotFoundError 是 GORM v1 API，v2 已移除。"
                "请改用: errors.Is(err, gorm.ErrRecordNotFound)"))

    return issues


# ═══════════════════════════════════════════════════════════════════════════════
# 全文件级规则（R11, R12, R15, R18b）
# ═══════════════════════════════════════════════════════════════════════════════

def check_full_file(code: str) -> List[Issue]:
    issues: List[Issue] = []
    has_open = "gorm.Open(" in code

    # ── R11: 缺少 PrepareStmt ────────────────────────────────────────────────
    if has_open and "PrepareStmt" not in code:
        issues.append(Issue("INFO", "MISSING_PREPARE_STMT", 0, "gorm.Config{}",
            "建议开启 PrepareStmt: true，SQL 编译结果可复用，高并发场景性能提升明显"))

    # ── R12: 缺少 SkipDefaultTransaction ────────────────────────────────────
    if has_open and "SkipDefaultTransaction" not in code:
        issues.append(Issue("INFO", "MISSING_SKIP_DEFAULT_TX", 0, "gorm.Config{}",
            "写操作无需隐式事务时，设置 SkipDefaultTransaction: true 可提升写性能约 30%"))

    # ── R15: 未设置连接池 ────────────────────────────────────────────────────
    if has_open and "SetMaxOpenConns" not in code:
        issues.append(Issue("WARN", "MISSING_POOL_CONFIG", 0, "sqlDB.SetMaxOpenConns(...)",
            "生产环境必须设置 SetMaxOpenConns / SetMaxIdleConns / SetConnMaxLifetime，"
            "否则默认无上限可能耗尽 DB 连接"))

    # ── R18b: AutoMigrate 未禁用物理 FK（全文件检测）────────────────────────
    if has_open and "DisableForeignKeyConstraintWhenMigrating" not in code:
        issues.append(Issue("WARN", "FK_MIGRATION_NOT_DISABLED", 0, "gorm.Config{}",
            "建议设置 DisableForeignKeyConstraintWhenMigrating: true，"
            "防止 AutoMigrate 自动创建物理外键约束"))

    return issues


# ═══════════════════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════════════════

def analyze(code: str) -> List[Issue]:
    lines = code.splitlines()
    all_issues = check_per_line(lines) + check_full_file(code)

    # 去重：同 rule 只保留行号最小的那条
    seen: set = set()
    deduped: List[Issue] = []
    for iss in sorted(all_issues, key=lambda x: x.line):
        if iss.rule not in seen:
            seen.add(iss.rule)
            deduped.append(iss)
    return deduped


def format_output(issues: List[Issue]) -> str:
    if not issues:
        return "✅ 未发现明显 GORM 反模式\n"

    icon = {"ERROR": "🔴", "WARN": "🟡", "INFO": "🔵"}
    out = [f"发现 {len(issues)} 个问题：\n"]
    for iss in issues:
        loc = f"第 {iss.line} 行" if iss.line > 0 else "文件级"
        out.append(f"{icon.get(iss.level, '⚪')} [{iss.level}] {iss.rule}  ({loc})")
        out.append(f"   代码: {iss.snippet[:120]}")
        out.append(f"   建议: {iss.suggestion}")
        out.append("")
    return "\n".join(out)


def format_json(issues: List[Issue]) -> str:
    return json.dumps([asdict(i) for i in issues], ensure_ascii=False, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GORM 静态分析器")
    parser.add_argument("file", nargs="?", default="-", help="Go 文件路径，- 表示 stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="输出格式: text（默认）或 json（CI 集成用）")
    args = parser.parse_args()

    if args.file != "-":
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    issues = analyze(code)

    if args.format == "json":
        print(format_json(issues))
    else:
        print(format_output(issues))

    sys.exit(1 if any(i.level == "ERROR" for i in issues) else 0)


if __name__ == "__main__":
    main()

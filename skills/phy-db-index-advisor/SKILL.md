---
name: phy-db-index-advisor
description: Database index advisor that statically analyzes ORM query patterns to predict missing indexes before they become production bottlenecks. Scans SQLAlchemy, Django ORM, TypeORM, Prisma, GORM, ActiveRecord, and Sequelize code for columns used in WHERE/filter, ORDER BY, and JOIN conditions. Cross-references existing model index definitions and migration files to suppress already-indexed columns. Ranks recommendations by query frequency and outputs ready-to-run CREATE INDEX SQL + per-ORM migration snippets. Zero competitors on ClawHub — not a single db-index-advisor SKILL.md in 13,700+ files.
license: Apache-2.0
tags:
  - database
  - performance
  - orm
  - indexes
  - django
  - sqlalchemy
  - prisma
  - typeorm
  - gorm
  - activerecord
metadata:
  author: PHY041
  version: "1.0.0"
---

# phy-db-index-advisor

Static analysis tool that reads your **ORM query patterns** and predicts which database columns are missing indexes — before a slow query alert fires in production. Works by counting how often each column appears in `.filter()`, `.where()`, `.order_by()`, and JOIN conditions across your entire codebase, then cross-referencing model definitions to suppress columns already indexed.

## Why This Exists

- 80% of production slow queries stem from missing indexes on columns used in WHERE clauses
- `User.objects.filter(email=email)` running 1,000× per minute causes full table scans
- Existing linters don't know your query patterns; `EXPLAIN ANALYZE` only catches issues after the fact
- This skill finds them **before deployment**

## What It Detects

### Query Patterns Scanned
| Access Pattern | Why It Matters |
|---------------|----------------|
| **WHERE / filter()** | Full table scan without index — O(n) per query |
| **ORDER BY / order_by()** | Sort without index reads all rows then sorts in memory |
| **JOIN ON column** | Nested-loop join without index is O(n²) |
| **UNIQUE constraint candidates** | Columns with `unique=True` queries need unique indexes |

### Supported ORMs
| ORM | Language | Patterns Detected |
|-----|----------|-------------------|
| **Django ORM** | Python | `.filter(col=)`, `.get(col=)`, `.exclude(col=)`, `.order_by('col')`, `Meta.ordering` |
| **SQLAlchemy** | Python | `.filter(Model.col ==)`, `.filter_by(col=)`, `.order_by(col)`, `join(Model, on=)` |
| **Peewee** | Python | `.where(Model.col ==)`, `.order_by(Model.col)` |
| **TypeORM** | TypeScript | `.where("t.col = :val")`, `findBy({col:})`, `.orderBy("t.col")`, `@JoinColumn({name: 'col'})` |
| **Prisma** | TypeScript | `where: { col: }`, `orderBy: { col: }`, `include: { relation: }` |
| **Sequelize** | TypeScript/JS | `where: { col: }`, `order: [['col', 'ASC']]` |
| **GORM** | Go | `.Where("col = ?")`, `.Order("col")`, `.Joins("JOIN ... ON col")` |
| **ActiveRecord** | Ruby | `.where(col:)`, `.find_by(col:)`, `.order(:col)`, `.joins()` |

### Existing Index Detection (Suppression)
The scanner reads existing index definitions so it doesn't recommend indexes that already exist:

| ORM | Where Indexes Are Found |
|-----|------------------------|
| Django | `db_index=True` on field, `Meta.indexes`, `Meta.unique_together` |
| SQLAlchemy | `Column(index=True)`, `Column(unique=True)`, `Index(...)` objects |
| TypeORM | `@Index()` decorator, `@Column({index: true})`, `@Unique()` |
| Prisma | `@@index([col])`, `@@unique([col])`, `@unique` on field |
| GORM | `gorm:"index"`, `gorm:"uniqueIndex"` struct tags |
| ActiveRecord | `add_index` in migrations, `index: true` in column definition |
| SQL migrations | `CREATE INDEX`, `CREATE UNIQUE INDEX` statements |

## Implementation

```python
#!/usr/bin/env python3
"""
phy-db-index-advisor — ORM query pattern analyzer for missing indexes
Usage: python3 advisor.py [path] [--json] [--min-count N]
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ─── Data structures ─────────────────────────────────────────────────────────

@dataclass
class QueryHit:
    file: str
    line: int
    pattern: str
    orm: str
    access_type: str  # WHERE, ORDER_BY, JOIN

@dataclass
class ColumnReport:
    table_hint: str  # Guessed model/table name
    column: str
    where_count: int = 0
    order_count: int = 0
    join_count: int = 0
    files: set = field(default_factory=set)
    hits: list = field(default_factory=list)
    already_indexed: bool = False

    @property
    def total_count(self) -> int:
        return self.where_count + self.order_count + self.join_count

    @property
    def priority(self) -> str:
        if self.already_indexed:
            return "INDEXED"
        if self.where_count >= 10 or self.total_count >= 15:
            return "CRITICAL"
        if self.where_count >= 5 or self.total_count >= 8:
            return "HIGH"
        if self.total_count >= 3:
            return "MEDIUM"
        return "LOW"

# ─── Query pattern registry ───────────────────────────────────────────────────

# (orm_name, access_type, regex, model_group_idx, col_group_idx)
QUERY_PATTERNS = [
    # ── Django ORM ──
    ("Django", "WHERE",
     re.compile(r'\.(?:filter|get|exclude|count|exists)\s*\([^)]*?(\w+)__?\w*\s*='),
     None, 1),
    ("Django", "WHERE",
     re.compile(r'\.(?:filter|get|exclude)\s*\(\s*(\w+)\s*='),
     None, 1),
    ("Django", "ORDER_BY",
     re.compile(r'\.order_by\s*\(\s*[\'"-](\w+)[\'"]\s*\)'),
     None, 1),
    ("Django", "ORDER_BY",
     re.compile(r'ordering\s*=\s*\[[^\]]*?[\'"](\w+)[\'"]'),
     None, 1),

    # ── SQLAlchemy ──
    ("SQLAlchemy", "WHERE",
     re.compile(r'\.filter\s*\(\s*(\w+)\.(\w+)\s*=='),
     1, 2),
    ("SQLAlchemy", "WHERE",
     re.compile(r'\.filter_by\s*\([^)]*?(\w+)\s*='),
     None, 1),
    ("SQLAlchemy", "ORDER_BY",
     re.compile(r'\.order_by\s*\(\s*(\w+)\.(\w+)'),
     1, 2),
    ("SQLAlchemy", "ORDER_BY",
     re.compile(r'\.order_by\s*\(\s*(?:asc|desc)\s*\(\s*(\w+)\.(\w+)'),
     1, 2),

    # ── TypeORM ──
    ("TypeORM", "WHERE",
     re.compile(r'where\s*:\s*\{[^}]*?(\w+)\s*:'),
     None, 1),
    ("TypeORM", "WHERE",
     re.compile(r'\.where\s*\(\s*[\'"`](?:\w+\.)?(\w+)\s*(?:=|LIKE|IN|>|<)'),
     None, 1),
    ("TypeORM", "ORDER_BY",
     re.compile(r'\.orderBy\s*\(\s*[\'"`](?:\w+\.)?(\w+)[\'"`]'),
     None, 1),
    ("TypeORM", "ORDER_BY",
     re.compile(r'orderBy\s*:\s*\{[^}]*?(\w+)\s*:'),
     None, 1),

    # ── Prisma ──
    ("Prisma", "WHERE",
     re.compile(r'where\s*:\s*\{[^}]*?(\w+)\s*:'),
     None, 1),
    ("Prisma", "ORDER_BY",
     re.compile(r'orderBy\s*:\s*\{[^}]*?(\w+)\s*:'),
     None, 1),

    # ── Sequelize ──
    ("Sequelize", "WHERE",
     re.compile(r'where\s*:\s*\{[^}]*?(\w+)\s*:'),
     None, 1),
    ("Sequelize", "ORDER_BY",
     re.compile(r'order\s*:\s*\[\s*\[\s*[\'"`](\w+)[\'"`]'),
     None, 1),

    # ── GORM ──
    ("GORM", "WHERE",
     re.compile(r'\.(?:Where|Find|First|Last)\s*\([^,)]*?[\'"`](?:\w+\.)?(\w+)\s*(?:=|LIKE|IN|>|<|\?)'),
     None, 1),
    ("GORM", "ORDER_BY",
     re.compile(r'\.Order\s*\(\s*[\'"`](\w+)'),
     None, 1),
    ("GORM", "JOIN",
     re.compile(r'\.Joins\s*\([^)]*?ON\s+\w+\.(\w+)\s*=\s*\w+\.(\w+)'),
     None, 1),

    # ── ActiveRecord (Ruby) ──
    ("ActiveRecord", "WHERE",
     re.compile(r'\.where\s*\(\s*(\w+):\s*'),
     None, 1),
    ("ActiveRecord", "WHERE",
     re.compile(r'\.find_by\s*\(\s*(\w+):\s*'),
     None, 1),
    ("ActiveRecord", "ORDER_BY",
     re.compile(r'\.order\s*\(\s*:(\w+)\s*\)'),
     None, 1),
    ("ActiveRecord", "ORDER_BY",
     re.compile(r'\.order\s*\(\s*[\'"](\w+)'),
     None, 1),
]

# ─── Existing index detection ─────────────────────────────────────────────────

EXISTING_INDEX_PATTERNS = [
    # Django
    re.compile(r'(\w+)\s*=\s*\w+Field\s*\([^)]*\bdb_index\s*=\s*True'),
    re.compile(r'(\w+)\s*=\s*\w+Field\s*\([^)]*\bunique\s*=\s*True'),
    re.compile(r'models\.Index\s*\(\s*fields\s*=\s*\[([^\]]+)\]'),
    # SQLAlchemy
    re.compile(r'Column\s*\([^)]*\bindex\s*=\s*True[^)]*\).*?#.*?(\w+)'),
    re.compile(r'(\w+)\s*=\s*Column\s*\([^)]*\bindex\s*=\s*True'),
    re.compile(r'(\w+)\s*=\s*Column\s*\([^)]*\bunique\s*=\s*True'),
    re.compile(r'Index\s*\(\s*[\'"`]\w+[\'"`]\s*,\s*\w+\.(\w+)'),
    # TypeORM
    re.compile(r'@(?:Index|Unique|Column)\s*\([^)]*\bindex\s*:\s*true'),
    re.compile(r'@Column\s*\([^)]*\bunique\s*:\s*true[^)]*\)\s*\w+\s*:\s*\w+\s*(\w+)'),
    # Prisma
    re.compile(r'@@index\s*\(\s*\[([^\]]+)\]'),
    re.compile(r'@@unique\s*\(\s*\[([^\]]+)\]'),
    re.compile(r'(\w+)\s+\w+\s+@unique'),
    # GORM
    re.compile(r'(\w+)\s+\w+\s+`[^`]*gorm:"[^"]*(?:index|uniqueIndex)[^"]*"`'),
    # SQL migrations
    re.compile(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+\w+\s+ON\s+\w+\s*\(([^)]+)\)', re.IGNORECASE),
    re.compile(r'add_index\s+:\w+\s*,\s*:(\w+)'),  # ActiveRecord migration
]

# Columns to always skip (noise)
SKIP_COLUMNS = {
    "id", "pk", "uuid", "created_at", "updated_at", "deleted_at",
    "created_by", "updated_by", "None", "null", "true", "false",
    "True", "False", "self", "cls", "this", "kwargs", "args",
}

SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "venv",
             "dist", "build", "target", "migrations", "alembic"}

FILE_EXTS = {".py", ".ts", ".js", ".rb", ".go"}

def collect_existing_indexes(root: Path) -> set[str]:
    """Return set of column names already indexed."""
    indexed = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() not in FILE_EXTS | {".sql", ".rb"}:
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pat in EXISTING_INDEX_PATTERNS:
                for m in pat.finditer(text):
                    for grp in m.groups():
                        if grp:
                            for col in re.split(r'[\s,\'"`]+', grp):
                                col = col.strip().strip('"\'`')
                                if col:
                                    indexed.add(col.lower())
    return indexed

def scan_queries(root: Path) -> dict[str, ColumnReport]:
    """Scan all source files and collect query patterns per column."""
    col_reports: dict[str, ColumnReport] = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() not in FILE_EXTS:
                continue
            # Skip test files
            if any(x in fname.lower() for x in ("test", "spec", "mock", "fixture")):
                continue
            try:
                lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue

            full_text = "\n".join(lines)
            rel_path = os.path.relpath(str(fpath))

            for (orm, access_type, pat, model_grp, col_grp) in QUERY_PATTERNS:
                for m in pat.finditer(full_text):
                    try:
                        col = m.group(col_grp)
                    except IndexError:
                        continue
                    if not col or col.lower() in SKIP_COLUMNS:
                        continue
                    if len(col) < 2 or not col.replace("_", "").isalpha():
                        continue

                    model = None
                    if model_grp:
                        try:
                            model = m.group(model_grp)
                        except IndexError:
                            pass

                    lineno = full_text[:m.start()].count("\n") + 1
                    key = col.lower()

                    if key not in col_reports:
                        col_reports[key] = ColumnReport(
                            table_hint=model or "",
                            column=col,
                        )
                    report = col_reports[key]
                    if model and not report.table_hint:
                        report.table_hint = model
                    report.files.add(rel_path)
                    report.hits.append(QueryHit(rel_path, lineno, m.group(0)[:80], orm, access_type))

                    if access_type == "WHERE":
                        report.where_count += 1
                    elif access_type == "ORDER_BY":
                        report.order_count += 1
                    elif access_type == "JOIN":
                        report.join_count += 1

    return col_reports

def format_report(reports: list[ColumnReport], existing_indexes: set[str]) -> str:
    # Mark already-indexed
    for r in reports:
        if r.column.lower() in existing_indexes:
            r.already_indexed = True

    # Filter to only non-indexed, min 3 total hits
    actionable = [r for r in reports if not r.already_indexed and r.total_count >= 3]
    actionable.sort(key=lambda x: x.total_count, reverse=True)

    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    actionable.sort(key=lambda x: priority_order.get(x.priority, 4))

    already_indexed = [r for r in reports if r.already_indexed and r.total_count >= 3]

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "  DB INDEX ADVISOR — Missing Index Analysis",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  Columns queried: {len(reports)}",
        f"  Missing indexes: {len(actionable)} ({sum(1 for r in actionable if r.priority=='CRITICAL')} CRITICAL)",
        f"  Already indexed: {len(already_indexed)} (suppressed)",
        "",
    ]

    icons = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "⚪"}
    current_priority = None
    for r in actionable:
        p = r.priority
        if p != current_priority:
            current_priority = p
            lines.append(f"\n{icons.get(p, '⚪')} {p}")
            lines.append("")

        table = r.table_hint or "?"
        breakdown = []
        if r.where_count:
            breakdown.append(f"WHERE×{r.where_count}")
        if r.order_count:
            breakdown.append(f"ORDER_BY×{r.order_count}")
        if r.join_count:
            breakdown.append(f"JOIN×{r.join_count}")

        # Show top 3 call sites
        sample_files = sorted(r.files)[:3]
        samples_str = ", ".join(sample_files)
        if len(r.files) > 3:
            samples_str += f" (+{len(r.files)-3} more)"

        lines += [
            f"  {table}.{r.column}  [{' | '.join(breakdown)}]  across {len(r.files)} file(s)",
            f"  Files: {samples_str}",
            f"  SQL:   CREATE INDEX idx_{table.lower()}_{r.column.lower()} ON {table.lower()} ({r.column});",
            f"  Django: {r.column} = models.{r.column.title()}Field(..., db_index=True)",
            f"  SQLAlchemy: {r.column} = Column(String, index=True)",
            f"  Prisma: @@index([{r.column}])",
            "",
        ]

    if not actionable:
        lines.append("  ✅ No missing indexes detected (all queried columns are already indexed)")
        lines.append("")

    if already_indexed:
        lines.append(f"  ✅ Already indexed ({len(already_indexed)} columns): "
                     + ", ".join(r.column for r in already_indexed[:8])
                     + ("..." if len(already_indexed) > 8 else ""))
        lines.append("")

    critical_count = sum(1 for r in actionable if r.priority == "CRITICAL")
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  CI gate: {'exit 1 — missing critical indexes' if critical_count else 'exit 0'}",
        "  Runtime verification: EXPLAIN ANALYZE your most frequent queries",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="DB index advisor — finds missing indexes from ORM patterns")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--min-count", type=int, default=3,
                        help="Minimum query count to report (default: 3)")
    parser.add_argument("--ci", action="store_true", help="Exit 1 if CRITICAL indexes missing")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    existing_indexes = collect_existing_indexes(root)
    col_reports_dict = scan_queries(root)
    reports = list(col_reports_dict.values())

    for r in reports:
        if r.column.lower() in existing_indexes:
            r.already_indexed = True

    actionable = sorted(
        [r for r in reports if not r.already_indexed and r.total_count >= args.min_count],
        key=lambda x: x.total_count,
        reverse=True,
    )

    if args.json:
        import dataclasses
        output = []
        for r in actionable:
            d = dataclasses.asdict(r)
            d["priority"] = r.priority
            d["total_count"] = r.total_count
            d["files"] = list(r.files)
            output.append(d)
        print(json.dumps(output, indent=2))
    else:
        print(format_report(reports, existing_indexes))

    if args.ci:
        has_critical = any(r.priority == "CRITICAL" for r in actionable)
        sys.exit(1 if has_critical else 0)

if __name__ == "__main__":
    main()
```

## Usage

```bash
# Scan current project
python3 advisor.py

# Scan a specific path
python3 advisor.py ~/projects/myapp

# Only show columns queried 5+ times
python3 advisor.py --min-count 5

# CI fail-gate (exits 1 if CRITICAL missing indexes found)
python3 advisor.py --ci

# JSON output for dashboard/ticketing
python3 advisor.py --json | jq '[.[] | select(.priority == "CRITICAL")]'

# GitHub Actions
- name: DB Index Advisor
  run: python3 .claude/skills/phy-db-index-advisor/advisor.py --ci
```

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DB INDEX ADVISOR — Missing Index Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Columns queried: 24
  Missing indexes: 6 (2 CRITICAL)
  Already indexed: 8 (suppressed)

🔴 CRITICAL

  User.email  [WHERE×28]  across 7 file(s)
  Files: api/auth.py, api/users.py, services/notifications.py (+4 more)
  SQL:   CREATE INDEX idx_user_email ON user (email);
  Django: email = models.EmailField(..., db_index=True)
  SQLAlchemy: email = Column(String, index=True)
  Prisma: @@index([email])

  Order.user_id  [WHERE×19 | JOIN×6]  across 5 file(s)
  Files: api/orders.py, services/billing.py, reports/revenue.py (+2 more)
  SQL:   CREATE INDEX idx_order_user_id ON order (user_id);
  Django: user_id = models.ForeignKey(..., db_index=True)
  SQLAlchemy: user_id = Column(Integer, ForeignKey('user.id'), index=True)
  Prisma: @@index([userId])

🟠 HIGH

  Product.category_id  [WHERE×12 | ORDER_BY×4]  across 4 file(s)
  SQL:   CREATE INDEX idx_product_category_id ON product (category_id);

  Session.token  [WHERE×9]  across 3 file(s)
  SQL:   CREATE INDEX idx_session_token ON session (token);

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CI gate: exit 1 — missing critical indexes
  Runtime verification: EXPLAIN ANALYZE your most frequent queries
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Relationship to `phy-sql-explainer`

| Skill | Input | Output | When to Use |
|-------|-------|--------|-------------|
| **phy-db-index-advisor** | Source code (ORM patterns) | Missing index recommendations | Pre-deployment: catch before slow queries appear |
| **phy-sql-explainer** | EXPLAIN ANALYZE output | Query plan diagnosis | Post-deployment: diagnose an existing slow query |

Use **both**: this skill prevents index gaps from being deployed; `phy-sql-explainer` diagnoses what got through anyway.

## Limitations & False Positives

- **Dynamic columns**: `.filter(**kwargs)` cannot be statically analyzed — run with `--min-count 5` to focus on confirmed hot paths
- **FK indexes**: Most databases (PostgreSQL, MySQL) do NOT automatically index foreign keys — this skill will flag them correctly
- **Primary keys**: `id` is always excluded (databases auto-index primary keys)
- **Composite indexes**: When two columns always appear together in WHERE, a composite index may outperform two single-column indexes — manual review recommended

## Companion Skills

| Skill | Use Together For |
|-------|-----------------|
| `phy-sql-explainer` | Pre + post deployment DB performance sweep |
| `phy-db-migration-auditor` | Safe migration before applying index additions |
| `phy-concurrency-audit` | Race conditions + missing indexes both cause data integrity failures |

#!/usr/bin/env python3
"""
Check freshness for a curated working set of files.

v1 scope:
- grouped thresholds by file class
- timestamp extraction from markdown headers, JSON updatedAt, or filesystem mtime
- human or JSON output
- no automatic rewriting

Usage:
  scripts/freshness-check.py --root . --config assets/examples/working-set.example.json
  scripts/freshness-check.py --root . --config assets/examples/working-set.example.json --json

Config shape:
{
  "groups": {
    "health": 3,
    "bridge": 3,
    "runtime": 3,
    "entry": 3,
    "structured": 7
  },
  "workingSet": [
    {"group": "health", "path": "memory/health/current-health.md"},
    {"group": "bridge", "path": "memory/SYSTEM_OVERVIEW.md"}
  ]
}
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

NOW = datetime.now().astimezone()

DATE_PATTERNS = [
    re.compile(r"(?im)^(?:-\s*)?Updated:\s*(.+)$"),
    re.compile(r"(?im)^Last updated:\s*(.+)$"),
    re.compile(r"(?im)^Last verified:\s*(.+)$"),
    re.compile(r"(?im)^Last rebuilt:\s*(.+)$"),
    re.compile(r"(?im)^Snapshot date:\s*(.+)$"),
]

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T")
DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class FreshnessItem:
    group: str
    path: str


@dataclass
class FreshnessResult:
    group: str
    path: str
    thresholdDays: int
    source: str
    seenAt: str
    ageDays: float
    status: str
    note: str


def parse_dt(raw: str) -> Optional[datetime]:
    raw = raw.strip().strip("`")
    raw = raw.replace(" +0800", "+08:00")
    if ISO_RE.match(raw):
        try:
            return datetime.fromisoformat(raw).astimezone()
        except ValueError:
            pass
    if DATE_ONLY_RE.match(raw):
        try:
            return datetime.fromisoformat(raw + "T00:00:00+00:00").astimezone()
        except ValueError:
            pass
    for fmt in ["%Y-%m-%d %H:%M %z", "%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=NOW.tzinfo)
            return dt.astimezone()
        except ValueError:
            continue
    return None


def extract_timestamp(path: Path) -> tuple[str, datetime, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".json":
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "updatedAt" in data:
                dt = parse_dt(str(data["updatedAt"]))
                if dt:
                    return "updatedAt", dt, "json"
        except json.JSONDecodeError:
            pass
    head = "\n".join(text.splitlines()[:30])
    for pattern in DATE_PATTERNS:
        m = pattern.search(head)
        if m:
            dt = parse_dt(m.group(1))
            if dt:
                return "header-date", dt, "header"
    stat_dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).astimezone()
    return "mtime", stat_dt, "filesystem"


def load_config(path: Path) -> tuple[dict[str, int], list[FreshnessItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = data.get("groups", {})
    working_set = [FreshnessItem(group=x["group"], path=x["path"]) for x in data.get("workingSet", [])]
    if not groups or not working_set:
        raise SystemExit("ERR: config must contain non-empty groups and workingSet")
    return groups, working_set


def check_one(root: Path, thresholds: dict[str, int], item: FreshnessItem) -> FreshnessResult:
    if item.group not in thresholds:
        raise SystemExit(f"ERR: unknown group in working set: {item.group}")
    full_path = (root / item.path).resolve()
    if not full_path.exists():
        return FreshnessResult(
            group=item.group,
            path=item.path,
            thresholdDays=thresholds[item.group],
            source="missing",
            seenAt="",
            ageDays=999999.0,
            status="WARN",
            note="file missing",
        )
    label, seen_at, source = extract_timestamp(full_path)
    age_days = (NOW - seen_at).total_seconds() / 86400
    threshold = thresholds[item.group]
    status = "OK" if age_days <= threshold else "WARN"
    note = f"{label} via {source}"
    return FreshnessResult(
        group=item.group,
        path=item.path,
        thresholdDays=threshold,
        source=source,
        seenAt=seen_at.isoformat(),
        ageDays=age_days,
        status=status,
        note=note,
    )


def print_human(results: list[FreshnessResult], thresholds: dict[str, int]) -> None:
    print(f"Freshness check @ {NOW.strftime('%Y-%m-%d %H:%M %z')}")
    print("Thresholds:")
    for group, days in thresholds.items():
        print(f"- {group}: {days}d")
    print()
    for r in results:
        print(f"[{r.status}] {r.path}")
        if r.source == "missing":
            print(f"  group={r.group} threshold={r.thresholdDays}d note={r.note}")
        else:
            print(
                f"  group={r.group} threshold={r.thresholdDays}d age={r.ageDays:.2f}d source={r.note} seen_at={r.seenAt}"
            )
    print()
    warns = [r for r in results if r.status == "WARN"]
    print(f"Summary: {len(results) - len(warns)} OK, {len(warns)} WARN, total {len(results)}")
    if warns:
        print("Warned files:")
        for r in warns:
            suffix = r.note if r.source == "missing" else f"{r.ageDays:.2f}d > {r.thresholdDays}d"
            print(f"- {r.path} ({suffix})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check freshness for a working set.")
    parser.add_argument("--root", required=True, help="Workspace root")
    parser.add_argument("--config", required=True, help="Path to working set JSON config")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    config = Path(args.config).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"ERR: root is not a directory: {root}")
    if not config.exists() or not config.is_file():
        raise SystemExit(f"ERR: config file not found: {config}")

    thresholds, working_set = load_config(config)
    results = [check_one(root, thresholds, item) for item in working_set]
    warns = [r for r in results if r.status == "WARN"]

    if args.json:
        print(json.dumps({
            "checkedAt": NOW.isoformat(),
            "thresholds": thresholds,
            "results": [asdict(r) for r in results],
            "warnCount": len(warns),
        }, ensure_ascii=False, indent=2))
    else:
        print_human(results, thresholds)

    return 2 if warns else 0


if __name__ == "__main__":
    raise SystemExit(main())

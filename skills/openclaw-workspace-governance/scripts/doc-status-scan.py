#!/usr/bin/env python3
"""
Scan a docs tree and summarize status labels relevant to live-vs-historical governance.

v1 scope:
- scan markdown files for recognized status labels
- count and group files by label
- optionally emit JSON
- do not rewrite files automatically

Recognized labels:
- historical-reference
- needs-refresh
- special-case active safety restriction

Usage:
  scripts/doc-status-scan.py --root docs
  scripts/doc-status-scan.py --root docs --json
  scripts/doc-status-scan.py --root docs --include-unlabeled
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

STATUS_PATTERNS = {
    "historical-reference": re.compile(r"\bhistorical-reference\b", re.IGNORECASE),
    "needs-refresh": re.compile(r"\bneeds-refresh\b", re.IGNORECASE),
    "special-case active safety restriction": re.compile(
        r"\bspecial-case active safety restriction\b", re.IGNORECASE
    ),
}

STATUS_ORDER = [
    "historical-reference",
    "needs-refresh",
    "special-case active safety restriction",
    "unlabeled",
]


@dataclass
class FileStatus:
    path: str
    status: str
    evidence: Optional[str] = None


def read_prefix(path: Path, max_lines: int = 12) -> str:
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = []
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
            return "".join(lines)
    except Exception:
        return ""


def detect_status(text: str) -> tuple[str, Optional[str]]:
    lowered = text.lower()
    matches = []
    for label, pattern in STATUS_PATTERNS.items():
        m = pattern.search(lowered)
        if m:
            matches.append((m.start(), label))

    if not matches:
        return "unlabeled", None

    matches.sort(key=lambda x: x[0])
    label = matches[0][1]
    return label, label


def scan_docs(root: Path, include_unlabeled: bool = False) -> list[FileStatus]:
    results: list[FileStatus] = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file():
            continue
        prefix = read_prefix(path)
        status, evidence = detect_status(prefix)
        if status == "unlabeled" and not include_unlabeled:
            continue
        results.append(FileStatus(path=str(path), status=status, evidence=evidence))
    return results


def build_summary(items: list[FileStatus]) -> dict:
    grouped: dict[str, list[str]] = {key: [] for key in STATUS_ORDER}
    for item in items:
        grouped.setdefault(item.status, []).append(item.path)

    summary = {
        "total": len(items),
        "counts": {k: len(v) for k, v in grouped.items() if v},
        "files": {k: v for k, v in grouped.items() if v},
    }
    return summary


def print_human(summary: dict) -> None:
    print("== Doc Status Scan ==")
    print(f"Total matched files: {summary['total']}")
    print()
    for status in STATUS_ORDER:
        files = summary["files"].get(status, [])
        if not files:
            continue
        print(f"[{status}] {len(files)}")
        for path in files[:20]:
            print(f"- {path}")
        if len(files) > 20:
            print(f"- ... {len(files) - 20} more")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan docs for governance status labels.")
    parser.add_argument("--root", required=True, help="Docs root to scan")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument(
        "--include-unlabeled",
        action="store_true",
        help="Include unlabeled markdown files in the scan output",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"ERR: root is not a directory: {root}")

    items = scan_docs(root, include_unlabeled=args.include_unlabeled)
    summary = build_summary(items)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

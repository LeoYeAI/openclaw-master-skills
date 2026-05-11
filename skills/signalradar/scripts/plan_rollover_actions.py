#!/usr/bin/env python3
"""Parse rollover markdown and produce confirmation-ready action plan."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r"^## 关闭/移除:\s*(.+)$")
CAND_RE = re.compile(r"^\s*-\s*\((\d+\.\d+)\)\s*(.+?)\s+\|\s+end=([^|]+)\s+\|\s+slug=(.+)$")


def parse_rollover(md: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_closed = ""
    for line in md.read_text(encoding="utf-8").splitlines():
        m = SECTION_RE.match(line.strip())
        if m:
            current_closed = m.group(1).strip()
            continue
        c = CAND_RE.match(line)
        if not c or not current_closed:
            continue
        rows.append(
            {
                "closed_question": current_closed,
                "score": float(c.group(1)),
                "candidate_question": c.group(2).strip(),
                "candidate_end_date": c.group(3).strip(),
                "candidate_slug": c.group(4).strip(),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Build rollover confirmation plan")
    parser.add_argument("--rollover-md", required=True)
    parser.add_argument("--auto-threshold", type=float, default=0.85)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args()

    rows = parse_rollover(Path(args.rollover_md))
    actions: list[dict[str, Any]] = []
    for r in rows:
        action = "suggest_confirm"
        if r["score"] >= args.auto_threshold:
            action = "suggest_auto"
        actions.append({**r, "action": action})

    payload = {
        "source": str(args.rollover_md),
        "auto_threshold": args.auto_threshold,
        "actions": actions,
        "next_step": "对 suggest_auto/suggest_confirm 做人工确认后再写入 SignalRadar_Manual_Entries",
    }
    if args.out_json:
        Path(args.out_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


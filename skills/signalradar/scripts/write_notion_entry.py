#!/usr/bin/env python3
"""Write monitoring entries to the Notion SignalRadar_Watchlist Database.

Usage:
  python3 scripts/write_notion_entry.py \
      --parent-page-id <NOTION_PAGE_ID> \
      --entry "AI Releases | Will GPT-6 be released? | 2026-06-30 | important | 4.0" \
      --entry "Crypto | Will BTC reach 200k?"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

from error_utils import emit_error

# Reuse existing Notion helpers
from notion_watchlist_db import (
    notion_headers,
    find_child_page_id,
    find_or_create_watchlist_db,
    add_manual_entry_to_db,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_ROOT_TITLE_CANDIDATES = ["SignalRadar", "signalradar"]
DEFAULT_CATEGORY = "AI Releases"


# ---------------------------------------------------------------------------
# Entry parsing
# ---------------------------------------------------------------------------

def parse_entry_string(entry: str) -> dict[str, Any] | None:
    """Parse a pipe-delimited entry string.

    Supports:
      Category | Question | EndDate | WatchLevel | ThresholdPP
      Category | Question
      Question (defaults to AI Releases category)
    """
    parts = [p.strip() for p in re.split(r"\s*[|｜]\s*", entry.strip())]
    parts = [p for p in parts if p]
    if not parts:
        return None

    if len(parts) == 1:
        return {
            "category": DEFAULT_CATEGORY,
            "question": parts[0],
        }

    result: dict[str, Any] = {
        "category": parts[0],
        "question": parts[1],
    }
    if len(parts) >= 3 and parts[2]:
        result["end_date"] = parts[2]
    if len(parts) >= 4 and parts[3]:
        result["watch_level"] = parts[3].lower()
    if len(parts) >= 5 and parts[4]:
        try:
            result["threshold_pp"] = float(parts[4])
        except ValueError:
            pass
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Write entries to Notion Database")
    parser.add_argument("--parent-page-id", required=True, help="Notion parent page ID")
    parser.add_argument(
        "--root-page-title",
        default="SignalRadar",
        help="Root directory page title (default: SignalRadar)",
    )
    parser.add_argument(
        "--entry",
        action="append",
        default=[],
        help="Pipe-delimited entry: 'Category | Question | EndDate | WatchLevel | ThresholdPP'",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Optional Polymarket URL to attach to the entry",
    )
    args = parser.parse_args()

    if not args.entry:
        print("No entries provided. Use --entry to add entries.")
        return 0

    if not os.environ.get("NOTION_API_KEY"):
        return emit_error(
            "SR_AUTH_MISSING",
            "NOTION_API_KEY not set",
            retryable=False,
            details={"script": "write_notion_entry.py"},
        )
    headers = notion_headers()

    # Parse entries
    parsed: list[dict[str, Any]] = []
    for raw in args.entry:
        entry = parse_entry_string(raw)
        if entry:
            parsed.append(entry)
    if not parsed:
        print("No valid entries parsed.")
        return 0

    try:
        # Find root page
        root_titles = [args.root_page_title] + DEFAULT_ROOT_TITLE_CANDIDATES
        root_id = find_child_page_id(args.parent_page_id, headers, list(set(root_titles)))
        if not root_id:
            return emit_error(
                "SR_NOTION_PAGE_NOT_FOUND",
                f"root page not found under {args.parent_page_id}",
                retryable=False,
                details={"tried_titles": root_titles},
            )

        # Find or create Database
        db_id = find_or_create_watchlist_db(root_id, headers)

        # Write to Database
        db_wrote = 0
        db_skipped = 0
        for entry in parsed:
            page_id = add_manual_entry_to_db(
                db_id,
                headers,
                question=entry["question"],
                category=entry.get("category", ""),
                url=args.url,
            )
            if page_id:
                db_wrote += 1
            else:
                db_skipped += 1

        print(f"WROTE={db_wrote} SKIPPED={db_skipped} DB_ID={db_id}")
        return 0

    except Exception as exc:
        return emit_error(
            "SR_NOTION_WRITE_FAILURE",
            f"write failed: {exc}",
            retryable=True,
            details={"script": "write_notion_entry.py"},
        )


if __name__ == "__main__":
    raise SystemExit(main())

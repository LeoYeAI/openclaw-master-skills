#!/usr/bin/env python3
"""Detect newly-pasted Polymarket URLs in the Notion Database and auto-fill.

Run manually or via user-configured cron when needed (not auto-scheduled).

Workflow:
  1. Query the SignalRadar_Watchlist Database for all rows.
  2. Find rows where "链接" has a URL but "问题" is empty → user just pasted a URL.
  3. Resolve each URL via Polymarket API (slug → market metadata).
  4. Update the Database row with question, category, probability, Source=manual.
  5. Merge the new entry into the local watchlist markdown.
  6. Print confirmation message for Bot delivery (or "NO_REPLY" if nothing new).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from error_utils import emit_error

# Reuse existing helpers
from notion_watchlist_db import (
    notion_headers,
    query_all_rows,
    update_row_properties,
    find_or_create_watchlist_db,
    _extract_title,
    _extract_url,
    _build_row_properties,
)
from pull_notion_watchlist_entries import (
    parse_slug_from_url,
    fetch_market_by_slug,
    merge_entries_to_watchlist,
    infer_category_from_question,
    find_child_page_id,
)

DEFAULT_ROOT_TITLE_CANDIDATES = ["SignalRadar", "signalradar"]


def default_workspace_root() -> str:
    env_root = os.environ.get("SIGNALRADAR_WORKSPACE_ROOT", "").strip()
    if env_root:
        return env_root
    try:
        script_root = Path(__file__).resolve().parent.parent.parent.parent
        if (script_root / "skills" / "signalradar" / "scripts").exists():
            return str(script_root)
    except Exception:
        pass
    return str(Path.cwd())


def _is_polymarket_url(url: str) -> bool:
    """Check if a URL looks like a Polymarket link."""
    return "polymarket.com" in url.lower()


def _row_needs_fill(row: dict[str, Any]) -> bool:
    """Return True if the row has a URL but no question (user just pasted a link)."""
    url = _extract_url(row)
    title = _extract_title(row).strip()
    if not url:
        return False
    if not _is_polymarket_url(url):
        return False
    # Consider "needs fill" if title is empty or is just whitespace/placeholder
    if not title or title.lower() in ("new", "新", "untitled", ""):
        return True
    return False


def resolve_and_fill(
    row: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any] | None:
    """Resolve a Polymarket URL and fill the Database row.

    Returns the resolved entry dict on success, None on failure.
    """
    url = _extract_url(row)
    page_id = row["id"]

    slug = parse_slug_from_url(url)
    if not slug:
        return None

    market = fetch_market_by_slug(slug)
    if not market:
        return None

    question = market["question"]
    category = market["category"]
    end_date = market.get("end_date", "")

    # Fetch current probability from the market data
    # fetch_market_by_slug doesn't return probability, so fetch it separately
    probability = _fetch_current_probability(slug)

    # Build properties to update
    props = _build_row_properties(
        question=question,
        category=category,
        probability=probability,
        url=url,
        source="manual",
    )

    # Update the Database row
    update_row_properties(page_id, headers, props)

    return {
        "question": question,
        "category": category,
        "end_date": end_date,
        "probability": probability,
        "url": url,
        "watch_level": "normal",
        "threshold_abs_pp": None,
    }


def _fetch_current_probability(slug: str) -> float | None:
    """Fetch the current Yes probability for a market by slug."""
    from pull_notion_watchlist_entries import fetch_public_json

    try:
        url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
        payload = fetch_public_json(url)
        if isinstance(payload, list) and payload:
            row = payload[0]
            # outcomePrices is a JSON string like "[0.45, 0.55]"
            prices_raw = row.get("outcomePrices", "")
            if isinstance(prices_raw, str) and prices_raw.startswith("["):
                import json
                prices = json.loads(prices_raw)
                if isinstance(prices, list) and len(prices) >= 1:
                    return round(float(prices[0]) * 100, 2)
            # Fallback: try bestBid or lastTradePrice
            best_bid = row.get("bestBid")
            if best_bid is not None:
                return round(float(best_bid) * 100, 2)
    except Exception:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect new Polymarket URLs in Notion Database")
    parser.add_argument("--parent-page-id", required=True, help="Notion parent page ID")
    parser.add_argument(
        "--root-page-title",
        default="SignalRadar",
        help="Root directory page title",
    )
    parser.add_argument(
        "--workspace-root",
        default=default_workspace_root(),
        help="Workspace root directory",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without writing")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    watchlist_path = workspace_root / "memory" / "polymarket_watchlist_2026.md"

    # --- Auth ---
    if not os.environ.get("NOTION_API_KEY"):
        return emit_error(
            "SR_AUTH_MISSING",
            "NOTION_API_KEY not set",
            retryable=False,
            details={"script": "check_new_urls.py"},
        )
    headers = notion_headers()

    try:
        # --- Find Database ---
        root_titles = [args.root_page_title] + DEFAULT_ROOT_TITLE_CANDIDATES
        root_id = find_child_page_id(args.parent_page_id, headers, list(set(root_titles)))
        if not root_id:
            root_id = args.parent_page_id

        db_id = find_or_create_watchlist_db(root_id, headers)
        if not db_id:
            return emit_error(
                "SR_NOTION_PAGE_NOT_FOUND",
                "watchlist Database not found and could not be created",
                retryable=True,
                details={"script": "check_new_urls.py"},
            )

        # --- Query rows ---
        rows = query_all_rows(db_id, headers)

        # --- Find rows needing fill ---
        to_fill = [r for r in rows if _row_needs_fill(r)]

        if not to_fill:
            print("NO_REPLY")
            return 0

        if args.dry_run:
            for row in to_fill:
                url = _extract_url(row)
                print(f"DRY_RUN: would resolve {url}")
            return 0

        # --- Resolve and fill each new URL ---
        filled: list[dict[str, Any]] = []
        failed_urls: list[str] = []

        for row in to_fill:
            url = _extract_url(row)
            result = resolve_and_fill(row, headers)
            if result:
                filled.append(result)
            else:
                failed_urls.append(url)

        # --- Merge into local watchlist markdown ---
        merged_count = 0
        if filled and watchlist_path.exists():
            entries_for_merge = [
                {
                    "category": f["category"],
                    "question": f["question"],
                    "end_date": f.get("end_date", ""),
                    "watch_level": "normal",
                    "threshold_abs_pp": None,
                }
                for f in filled
            ]
            try:
                merge_result = merge_entries_to_watchlist(watchlist_path, entries_for_merge)
                merged_count = merge_result["merged_count"]
            except Exception:
                pass  # Non-fatal: DB is updated even if local merge fails

        # --- Output confirmation for Bot ---
        if not filled:
            # All URLs failed to resolve
            print("NO_REPLY")
            return 0

        lines = ["✅ 检测到你添加了新的监测条目："]
        for i, entry in enumerate(filled, 1):
            prob_str = f"{entry['probability']:.0f}%" if entry.get("probability") is not None else "N/A"
            lines.append(f"{i}. {entry['question']} (当前 Yes 概率 {prob_str})")
            detail_parts = [f"分类: {entry['category']}"]
            if entry.get("end_date"):
                detail_parts.append(f"截止: {entry['end_date']}")
            lines.append(f"   {'  |  '.join(detail_parts)}")

        lines.append("")
        lines.append("已自动加入监测列表，后续概率变化超过阈值时会推送提醒。")

        if failed_urls:
            lines.append(f"\n⚠️ {len(failed_urls)} 个链接无法解析，请检查URL是否正确。")

        print("\n".join(lines))
        return 0

    except Exception as exc:
        return emit_error(
            "SR_NOTION_READ_FAILURE",
            f"check_new_urls failed: {exc}",
            retryable=True,
            details={"script": "check_new_urls.py"},
        )


if __name__ == "__main__":
    raise SystemExit(main())

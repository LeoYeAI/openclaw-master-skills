#!/usr/bin/env python3
"""Manage a Notion Database for SignalRadar watchlist display.

Provides functions to create, sync, and query a Notion Database that
mirrors the local watchlist markdown — but with proper table UI
(sortable, filterable) for users.
"""

from __future__ import annotations

import json
import urllib.request
import os
from typing import Any

from error_utils import emit_error


# ---------------------------------------------------------------------------
# Notion API helpers (aligned with pull_notion_watchlist_entries.py patterns)
# ---------------------------------------------------------------------------

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_API_VERSION = "2022-06-28"

DB_TITLE = "SignalRadar_Watchlist"
DB_ID_CACHE_NAME = ".notion_db_id"

# Select option colours
CATEGORY_COLORS: dict[str, str] = {
    "AI Releases": "blue",
    "AI Leaders": "purple",
    "OpenAI IPO": "green",
    "SpaceX IPO": "orange",
    "SpaceX Missions": "red",
    "Crypto": "yellow",
    "Geopolitics": "gray",
}


def notion_headers() -> dict[str, str]:
    key = os.environ.get("NOTION_API_KEY", "")
    return {
        "Authorization": f"Bearer {key}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }


def api_request(method: str, url: str, headers: dict[str, str], body: dict | None = None) -> dict[str, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_get(url: str, headers: dict[str, str]) -> dict[str, Any]:
    return api_request("GET", url, headers)


# ---------------------------------------------------------------------------
# Database schema definition
# ---------------------------------------------------------------------------

def _database_properties() -> dict[str, Any]:
    cat_options = [{"name": k, "color": v} for k, v in CATEGORY_COLORS.items()]
    return {
        "问题": {"title": {}},
        "分类": {
            "select": {"options": cat_options},
        },
        "Yes概率": {
            "number": {"format": "percent"},
        },
        "链接": {"url": {}},
        "Source": {
            "select": {
                "options": [
                    {"name": "auto", "color": "green"},
                    {"name": "manual", "color": "orange"},
                ],
            },
        },
    }


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def find_child_page_id(
    parent_page_id: str,
    headers: dict[str, str],
    title_candidates: list[str],
) -> str | None:
    """Return the id of the first child page whose title is in *title_candidates*."""
    url = f"{NOTION_API_BASE}/blocks/{parent_page_id}/children?page_size=100"
    data = api_get(url, headers)
    for block in data.get("results", []):
        if block.get("type") == "child_page":
            t = block.get("child_page", {}).get("title", "")
            if t in title_candidates:
                return block["id"]
    return None


def find_database_under_page(
    parent_page_id: str,
    headers: dict[str, str],
    db_title: str = DB_TITLE,
) -> str | None:
    """Find an existing inline database under a page by title."""
    url = f"{NOTION_API_BASE}/blocks/{parent_page_id}/children?page_size=100"
    data = api_get(url, headers)
    for block in data.get("results", []):
        if block.get("type") == "child_database":
            t = block.get("child_database", {}).get("title", "")
            if t == db_title:
                return block["id"]
    return None


def create_watchlist_database(
    parent_page_id: str,
    headers: dict[str, str],
    title: str = DB_TITLE,
) -> str:
    """Create a new Notion Database under the given parent page."""
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "is_inline": True,
        "properties": _database_properties(),
    }
    result = api_request("POST", f"{NOTION_API_BASE}/databases", headers, payload)
    return str(result.get("id", "")).strip()


def find_or_create_watchlist_db(
    root_page_id: str,
    headers: dict[str, str],
    title: str = DB_TITLE,
) -> str:
    """Find existing database or create a new one. Returns database_id."""
    db_id = find_database_under_page(root_page_id, headers, title)
    if db_id:
        return db_id
    return create_watchlist_database(root_page_id, headers, title)


def _build_row_properties(
    question: str,
    category: str = "",
    probability: float | None = None,
    url: str | None = None,
    source: str = "auto",
) -> dict[str, Any]:
    """Build Notion page properties dict for a database row."""
    props: dict[str, Any] = {
        "问题": {
            "title": [{"type": "text", "text": {"content": question}}],
        },
    }
    if category:
        props["分类"] = {"select": {"name": category}}
    if probability is not None:
        # Notion percent format expects 0-1 range.
        # Polymarket returns 0-100 (e.g. 45.5 means 45.5%).
        # Values >= 1.0 are treated as percentage and divided by 100.
        props["Yes概率"] = {"number": probability / 100.0 if probability >= 1.0 else probability}
    if url:
        props["链接"] = {"url": url}
    if source:
        props["Source"] = {"select": {"name": source}}
    return props


def query_all_rows(
    database_id: str,
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    """Query all rows from the database with pagination."""
    all_rows: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = api_request("POST", f"{NOTION_API_BASE}/databases/{database_id}/query", headers, payload)
        all_rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
        if not cursor:
            break
    return all_rows


def _extract_title(row: dict[str, Any]) -> str:
    """Extract the title text from a database row."""
    title_prop = row.get("properties", {}).get("问题", {})
    for rt in title_prop.get("title", []):
        return rt.get("text", {}).get("content", "")
    return ""


def _extract_url(row: dict[str, Any]) -> str:
    """Extract the URL from a database row."""
    return row.get("properties", {}).get("链接", {}).get("url", "") or ""


def _extract_select(row: dict[str, Any], prop: str) -> str:
    """Extract a select value from a database row."""
    sel = row.get("properties", {}).get(prop, {}).get("select")
    return sel.get("name", "") if sel else ""


def update_row_properties(
    page_id: str,
    headers: dict[str, str],
    props: dict[str, Any],
) -> None:
    """Update properties of an existing database row."""
    api_request("PATCH", f"{NOTION_API_BASE}/pages/{page_id}", headers, {"properties": props})


def sync_watchlist_to_db(
    database_id: str,
    headers: dict[str, str],
    items: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync watchlist items to database. Creates new rows, updates existing.

    Returns {"created": N, "updated": M, "skipped": K}.
    """
    existing_rows = query_all_rows(database_id, headers)
    existing_map: dict[str, str] = {}  # question -> page_id
    for row in existing_rows:
        q = _extract_title(row).strip().lower()
        if q:
            existing_map[q] = row["id"]

    created = 0
    updated = 0
    skipped = 0

    for item in items:
        question = str(item.get("question", "")).strip()
        if not question:
            skipped += 1
            continue

        props = _build_row_properties(
            question=question,
            category=str(item.get("category", "")),
            probability=float(item.get("yes", 0)) if item.get("yes") is not None else None,
            source="auto",
        )

        key = question.lower()
        if key in existing_map:
            # Update existing row
            page_id = existing_map[key]
            try:
                api_request(
                    "PATCH",
                    f"{NOTION_API_BASE}/pages/{page_id}",
                    headers,
                    {"properties": props},
                )
                updated += 1
            except Exception:
                skipped += 1
        else:
            # Create new row
            try:
                api_request(
                    "POST",
                    f"{NOTION_API_BASE}/pages",
                    headers,
                    {
                        "parent": {"type": "database_id", "database_id": database_id},
                        "properties": props,
                    },
                )
                created += 1
            except Exception:
                skipped += 1

    return {"created": created, "updated": updated, "skipped": skipped}


def add_manual_entry_to_db(
    database_id: str,
    headers: dict[str, str],
    question: str,
    category: str = "",
    url: str | None = None,
) -> str | None:
    """Add a single manual entry to the database. Returns page_id or None."""
    # Check for duplicates
    existing = query_all_rows(database_id, headers)
    key = question.strip().lower()
    for row in existing:
        if _extract_title(row).strip().lower() == key:
            return None  # already exists

    props = _build_row_properties(
        question=question,
        category=category,
        url=url,
        source="manual",
    )
    result = api_request(
        "POST",
        f"{NOTION_API_BASE}/pages",
        headers,
        {
            "parent": {"type": "database_id", "database_id": database_id},
            "properties": props,
        },
    )
    return str(result.get("id", "")).strip()

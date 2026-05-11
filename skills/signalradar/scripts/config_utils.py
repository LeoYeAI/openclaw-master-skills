#!/usr/bin/env python3
"""Configuration and watchlist helpers for SignalRadar runtime."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "profile": {
        "timezone": "Asia/Shanghai",
        "language": "",
    },
    "check_interval_minutes": 10,
    "threshold": {
        "abs_pp": 5.0,
        "per_category_abs_pp": {},
        "per_entry_abs_pp": {},
    },
    "delivery": {
        "primary": {"channel": "webhook", "target": ""},
        "fallback": [],
    },
    "source": {
        "retries": 2,
    },
    "digest": {
        "frequency": "weekly",
        "day_of_week": "monday",
        "time_local": "09:00",
        "top_n": 10,
    },
    "baseline": {
        "cleanup_after_expiry_days": 90,
    },
}

_EMPTY_WATCHLIST: dict[str, list] = {"entries": [], "archived": []}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_json_config(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(obj, dict):
        return {}
    return obj


def save_json_config(path: Path, data: dict[str, Any]) -> None:
    """Atomically write a generic JSON config file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=".config_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.rename(tmp_path, str(path))
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def get_nested_value(data: dict[str, Any], key_path: str) -> tuple[bool, Any]:
    """Resolve a dotted config path like 'threshold.abs_pp'."""
    current: Any = data
    for part in key_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def set_nested_value(data: dict[str, Any], key_path: str, value: Any) -> None:
    """Set a dotted config path, creating intermediate dicts as needed."""
    parts = key_path.split(".")
    current: dict[str, Any] = data
    for part in parts[:-1]:
        next_value = current.get(part)
        if not isinstance(next_value, dict):
            next_value = {}
            current[part] = next_value
        current = next_value
    current[parts[-1]] = value


# ---------------------------------------------------------------------------
# Watchlist CRUD
# ---------------------------------------------------------------------------

def load_watchlist(path: Path) -> dict[str, Any]:
    """Load watchlist.json with graceful fallback on corruption or missing keys."""
    if not path.exists():
        return {"entries": [], "archived": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"entries": [], "archived": []}
    if not isinstance(raw, dict):
        return {"entries": [], "archived": []}
    # Ensure both keys exist and are lists
    if not isinstance(raw.get("entries"), list):
        raw["entries"] = []
    if not isinstance(raw.get("archived"), list):
        raw["archived"] = []
    return raw


def save_watchlist(path: Path, data: dict[str, Any]) -> None:
    """Atomic write: write to .tmp then rename to prevent corruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=".watchlist_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.rename(tmp_path, str(path))
    except BaseException:
        # Clean up temp file on any failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def add_entries(
    path: Path, new_entries: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Idempotent add: skip entries whose entry_id already exists.

    Returns (added, skipped) lists.
    """
    data = load_watchlist(path)
    existing_ids = {e.get("entry_id") for e in data["entries"]}
    # Also check archived — don't re-add an archived entry silently
    archived_ids = {e.get("entry_id") for e in data["archived"]}

    added: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for entry in new_entries:
        eid = entry.get("entry_id")
        if eid in existing_ids:
            skipped.append(entry)
        elif eid in archived_ids:
            # Previously archived — revive: remove from archived, add fresh
            data["archived"] = [a for a in data["archived"] if a.get("entry_id") != eid]
            data["entries"].append(entry)
            existing_ids.add(eid)
            archived_ids.discard(eid)
            added.append(entry)
        else:
            data["entries"].append(entry)
            existing_ids.add(eid)
            added.append(entry)

    if added:
        save_watchlist(path, data)

    return added, skipped


def archive_entry(
    path: Path,
    entry_id: str,
    reason: str,
    baseline_history: list[dict[str, Any]] | None = None,
    final_result: str | None = None,
) -> dict[str, Any] | None:
    """Move entry from entries to archived. Returns archived entry or None if not found."""
    data = load_watchlist(path)
    found_idx = None
    for i, entry in enumerate(data["entries"]):
        if entry.get("entry_id") == entry_id:
            found_idx = i
            break

    if found_idx is None:
        return None

    entry = data["entries"].pop(found_idx)
    entry["archived_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry["archive_reason"] = reason
    if baseline_history is not None:
        entry["baseline_history"] = baseline_history
    if final_result is not None:
        entry["final_result"] = final_result

    data["archived"].append(entry)
    save_watchlist(path, data)
    return entry


def get_entry_by_number(data: dict[str, Any], number: int) -> dict[str, Any] | None:
    """Get entry by 1-based global number (list order). Returns None if out of range."""
    entries = data.get("entries", [])
    if number < 1 or number > len(entries):
        return None
    return entries[number - 1]

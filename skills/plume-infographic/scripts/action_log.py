#!/usr/bin/env python3
"""
Action log read/write module

Maintains ~/.openclaw/media/plume/action_log_{channel}.json,
recording complete parameters and results for each create/retry operation,
used by retry and circuit breaker mechanisms.

Two-step write:
  1. create_infographic.py appends entry after task creation (status=pending)
  2. create_infographic.py updates entry at task terminal state (status=success/failed/...)
"""

import json
import time
from pathlib import Path

MEDIA_DIR = Path.home() / ".openclaw" / "media" / "plume"
MAX_LOG_SIZE = 10


def _log_path(channel: str) -> Path:
    filename = f"action_log_{channel}.json" if channel else "action_log.json"
    return MEDIA_DIR / filename


def read_log(channel: str) -> list[dict]:
    """Read action log for the specified channel"""
    path = _log_path(channel)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_log(channel: str, log: list[dict]):
    """Write log, FIFO eviction when exceeding limit"""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    if len(log) > MAX_LOG_SIZE:
        log = log[-MAX_LOG_SIZE:]
    _log_path(channel).write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def append_entry(channel: str, entry: dict):
    """Called on task creation: append a pending record"""
    log = read_log(channel)
    entry.setdefault("status", "pending")
    entry.setdefault("created_at", time.time())
    log.append(entry)
    _write_log(channel, log)


def update_entry(channel: str, task_id: str, updates: dict):
    """Called at task terminal state: update status/result fields of the corresponding record"""
    log = read_log(channel)
    for entry in reversed(log):
        if entry.get("task_id") == task_id:
            entry.update(updates)
            entry.setdefault("completed_at", time.time())
            break
    _write_log(channel, log)

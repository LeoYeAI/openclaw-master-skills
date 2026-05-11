#!/usr/bin/env python3
"""
Session registry for OpenAI Codex tasks.
Stores metadata about completed/running sessions for resumption and tracking.

Registry format: ~/.openclaw/codex_sessions.json
{
  "sessions": {
    "<session-id>": {
      "session_id": "...",
      "label": "Research on topic X",
      "task_summary": "first 200 chars of task...",
      "project_dir": "/absolute/path",
      "created_at": "ISO timestamp",
      "last_accessed": "ISO timestamp",
      "status": "completed|failed|timeout",
      "openclaw_session": "agent:main:whatsapp:group:...",
      "output_file": "/tmp/codex-YYYYMMDD-HHMMSS.txt",
      "cost_estimate": null
    }
  }
}
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List


REGISTRY_FILE = Path.home() / ".openclaw" / "codex_sessions.json"


def _ensure_registry() -> Dict:
    """Ensure registry file exists and return its contents."""
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {"sessions": {}}
        REGISTRY_FILE.write_text(json.dumps(data, indent=2))
        os.chmod(REGISTRY_FILE, 0o600)
        return data

    try:
        return json.loads(REGISTRY_FILE.read_text())
    except (json.JSONDecodeError, KeyError):
        # Corrupted registry, reset it
        data = {"sessions": {}}
        REGISTRY_FILE.write_text(json.dumps(data, indent=2))
        os.chmod(REGISTRY_FILE, 0o600)
        return data


def _save_registry(data: Dict):
    """Save registry data to file."""
    REGISTRY_FILE.write_text(json.dumps(data, indent=2))
    os.chmod(REGISTRY_FILE, 0o600)


def register_session(
    session_id: str,
    label: Optional[str],
    task: str,
    project_dir: str,
    openclaw_session: Optional[str],
    output_file: str,
    status: str = "running"
) -> Dict:
    """
    Register a new session in the registry.

    Args:
        session_id: Codex session ID
        label: Human-readable label for the session
        task: Full task description (will be truncated to 200 chars)
        project_dir: Absolute path to project directory
        openclaw_session: OpenClaw session key that launched this task
        output_file: Path to output file
        status: Session status (running|completed|failed|timeout)

    Returns:
        The created session entry
    """
    data = _ensure_registry()

    now = datetime.now().isoformat()
    entry = {
        "session_id": session_id,
        "label": label,
        "task_summary": task[:200],
        "project_dir": str(Path(project_dir).absolute()),
        "created_at": now,
        "last_accessed": now,
        "status": status,
        "openclaw_session": openclaw_session,
        "output_file": output_file,
        "cost_estimate": None
    }

    data["sessions"][session_id] = entry
    _save_registry(data)
    return entry


def get_session(session_id: str) -> Optional[Dict]:
    """
    Get session entry by ID.

    Returns:
        Session entry dict or None if not found
    """
    data = _ensure_registry()
    entry = data["sessions"].get(session_id)

    if entry:
        # Update last_accessed
        entry["last_accessed"] = datetime.now().isoformat()
        data["sessions"][session_id] = entry
        _save_registry(data)

    return entry


def list_recent_sessions(hours: int = 72) -> List[Dict]:
    """
    List sessions accessed within the last N hours.

    Args:
        hours: Time window in hours (default: 72 = 3 days)

    Returns:
        List of session entries, sorted by last_accessed (newest first)
    """
    data = _ensure_registry()
    cutoff = datetime.now() - timedelta(hours=hours)

    recent = []
    for session_id, entry in data["sessions"].items():
        try:
            last_access = datetime.fromisoformat(entry["last_accessed"])
            if last_access >= cutoff:
                recent.append(entry)
        except (ValueError, KeyError):
            continue

    # Sort by last_accessed, newest first
    recent.sort(key=lambda x: x.get("last_accessed", ""), reverse=True)
    return recent


def find_session_by_label(label: str) -> Optional[Dict]:
    """
    Find session by label (case-insensitive substring match).

    Args:
        label: Label to search for

    Returns:
        First matching session entry or None
    """
    data = _ensure_registry()
    label_lower = label.lower()

    # First try exact match
    for session_id, entry in data["sessions"].items():
        entry_label = (entry.get("label") or "")
        if entry_label.lower() == label_lower:
            return entry

    # Then try substring match
    for session_id, entry in data["sessions"].items():
        entry_label = (entry.get("label") or "")
        if label_lower in entry_label.lower():
            return entry

    return None


def update_session(session_id: str, **kwargs) -> bool:
    """
    Update session entry fields.

    Args:
        session_id: Session ID to update
        **kwargs: Fields to update (status, label, output_file, etc.)

    Returns:
        True if session was found and updated, False otherwise
    """
    data = _ensure_registry()

    if session_id not in data["sessions"]:
        return False

    entry = data["sessions"][session_id]
    entry["last_accessed"] = datetime.now().isoformat()

    # Update provided fields
    for key, value in kwargs.items():
        if key in entry:
            entry[key] = value

    data["sessions"][session_id] = entry
    _save_registry(data)
    return True


def cleanup_old_sessions(days: int = 30) -> int:
    """
    Remove sessions older than N days.

    Args:
        days: Age threshold in days (default: 30)

    Returns:
        Number of sessions removed
    """
    data = _ensure_registry()
    cutoff = datetime.now() - timedelta(days=days)

    to_remove = []
    for session_id, entry in data["sessions"].items():
        try:
            last_access = datetime.fromisoformat(entry["last_accessed"])
            if last_access < cutoff:
                to_remove.append(session_id)
        except (ValueError, KeyError):
            # Invalid timestamp, remove it
            to_remove.append(session_id)

    for session_id in to_remove:
        del data["sessions"][session_id]

    if to_remove:
        _save_registry(data)

    return len(to_remove)

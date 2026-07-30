#!/usr/bin/env python3
"""
Undo operations for email-to-calendar skill.

Provides helper functions for undo functionality.
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from json_store import load_json, save_json
from common import format_timestamp, time_ago

CHANGELOG_FILE = os.path.expanduser(
    "~/.openclaw/workspace/memory/email-to-calendar/changelog.json"
)
UNDO_WINDOW_HOURS = 24


def find_last_undoable() -> None:
    """Find and print the most recent undoable change ID."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})
    undo_window = timedelta(hours=UNDO_WINDOW_HOURS)
    now = datetime.now()

    changes = list(reversed(changelog.get("changes", [])))

    for change in changes:
        if not change.get("can_undo", False):
            continue
        try:
            change_time = datetime.fromisoformat(change.get("timestamp", ""))
            if (now - change_time) < undo_window:
                print(change.get("id"))
                return
        except (ValueError, TypeError):
            continue

    sys.exit(1)


def list_undoable() -> None:
    """Print all undoable changes."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})
    undo_window = timedelta(hours=UNDO_WINDOW_HOURS)
    now = datetime.now()

    changes = list(reversed(changelog.get("changes", [])))
    undoable = []

    for change in changes:
        if not change.get("can_undo", False):
            continue
        try:
            change_time = datetime.fromisoformat(change.get("timestamp", ""))
            if (now - change_time) < undo_window:
                undoable.append(change)
        except (ValueError, TypeError):
            continue

    if not undoable:
        print("No undoable changes (all changes are older than 24 hours or already undone).")
        return

    print(f"Undoable changes ({len(undoable)}):\n")

    for i, change in enumerate(undoable, 1):
        change_id = change.get("id")
        action = change.get("action")
        ts = change.get("timestamp", "")

        ts_str = format_timestamp(ts)
        ago_str = time_ago(ts)

        if action == "create":
            summary = change.get("after", {}).get("summary", "Unknown")
            desc = f'Created "{summary}"'
        elif action == "update":
            summary = (
                change.get("after", {}).get("summary") or
                change.get("before", {}).get("summary", "Unknown")
            )
            desc = f'Updated "{summary}"'
        else:
            summary = change.get("before", {}).get("summary", "Unknown")
            desc = f'Deleted "{summary}"'

        print(f"{i}. {change_id}")
        print(f"   {desc}")
        print(f"   {ago_str}")
        print()

    print("Use 'undo.sh --change-id <id>' to undo a specific change")
    print("or 'undo.sh last' to undo the most recent change.")


def mark_undone(change_id: str) -> None:
    """Mark a change as undone."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})

    for change in changelog.get("changes", []):
        if change.get("id") == change_id:
            change["can_undo"] = False
            change["undone_at"] = datetime.now().isoformat()
            break

    save_json(CHANGELOG_FILE, changelog)


def main():
    if len(sys.argv) < 2:
        print("Usage: undo_ops.py <action> [options]", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    # Parse keyword arguments
    args = {}
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:].replace("-", "_")
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
                args[key] = sys.argv[i + 1]
                i += 2
            else:
                args[key] = True
                i += 1
        else:
            i += 1

    if action == "find-last":
        find_last_undoable()
    elif action == "list":
        list_undoable()
    elif action == "mark-undone":
        mark_undone(args.get("change_id", ""))
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

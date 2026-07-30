#!/usr/bin/env python3
"""
Changelog operations for email-to-calendar skill.

Manages the audit trail of calendar changes for undo support.
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from json_store import load_json, save_json
from common import generate_indexed_id, format_timestamp, time_ago

CHANGELOG_FILE = os.path.expanduser(
    "~/.openclaw/workspace/memory/email-to-calendar/changelog.json"
)
UNDO_WINDOW_HOURS = 24
MAX_CHANGES = 100


def log_create(
    event_id: str,
    calendar_id: str,
    summary: str,
    start_time: str = "",
    end_time: str = "",
    email_id: str = ""
) -> str:
    """Log a create action. Returns the change ID."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})

    change_id = generate_indexed_id("chg", len(changelog["changes"]) + 1)

    change = {
        "id": change_id,
        "timestamp": datetime.now().isoformat(),
        "action": "create",
        "event_id": event_id,
        "calendar_id": calendar_id or "primary",
        "before": None,
        "after": {
            "summary": summary,
            "start": start_time,
            "end": end_time
        },
        "source_email_id": email_id if email_id else None,
        "can_undo": True
    }

    changelog["changes"].append(change)
    changelog["changes"] = changelog["changes"][-MAX_CHANGES:]
    save_json(CHANGELOG_FILE, changelog)

    return change_id


def log_update(
    event_id: str,
    calendar_id: str,
    before_json: str = "",
    after_json: str = "",
    email_id: str = ""
) -> str:
    """Log an update action. Returns the change ID."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})

    # Parse before/after JSON
    try:
        before = json.loads(before_json) if before_json else None
    except json.JSONDecodeError:
        before = None

    try:
        after = json.loads(after_json) if after_json else None
    except json.JSONDecodeError:
        after = None

    change_id = generate_indexed_id("chg", len(changelog["changes"]) + 1)

    change = {
        "id": change_id,
        "timestamp": datetime.now().isoformat(),
        "action": "update",
        "event_id": event_id,
        "calendar_id": calendar_id or "primary",
        "before": before,
        "after": after,
        "source_email_id": email_id if email_id else None,
        "can_undo": True
    }

    changelog["changes"].append(change)
    changelog["changes"] = changelog["changes"][-MAX_CHANGES:]
    save_json(CHANGELOG_FILE, changelog)

    return change_id


def log_delete(
    event_id: str,
    calendar_id: str,
    before_json: str = ""
) -> str:
    """Log a delete action. Returns the change ID."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})

    try:
        before = json.loads(before_json) if before_json else None
    except json.JSONDecodeError:
        before = None

    change_id = generate_indexed_id("chg", len(changelog["changes"]) + 1)

    change = {
        "id": change_id,
        "timestamp": datetime.now().isoformat(),
        "action": "delete",
        "event_id": event_id,
        "calendar_id": calendar_id or "primary",
        "before": before,
        "after": None,
        "source_email_id": None,
        "can_undo": True
    }

    changelog["changes"].append(change)
    changelog["changes"] = changelog["changes"][-MAX_CHANGES:]
    save_json(CHANGELOG_FILE, changelog)

    return change_id


def list_changes(last_n: int = 10) -> None:
    """Print recent changes to stdout."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})
    changes = changelog.get("changes", [])

    if not changes:
        print("No changes recorded yet.")
        return

    undo_window = timedelta(hours=UNDO_WINDOW_HOURS)
    recent = list(reversed(changes[-last_n:]))
    now = datetime.now()

    print(f"Recent changes (last {len(recent)}):\n")

    for change in recent:
        change_id = change.get("id", "unknown")
        ts = change.get("timestamp", "")
        action = change.get("action", "unknown")
        event_id = change.get("event_id", "")

        # Check if still within undo window
        try:
            change_time = datetime.fromisoformat(ts)
            can_undo = (now - change_time) < undo_window and change.get("can_undo", False)
        except (ValueError, TypeError):
            can_undo = False

        undo_marker = " [can undo]" if can_undo else ""
        ts_str = format_timestamp(ts)

        # Get summary from before or after
        if action == "create":
            summary = change.get("after", {}).get("summary", "Unknown")
        elif action == "update":
            summary = (
                change.get("after", {}).get("summary") or
                change.get("before", {}).get("summary", "Unknown")
            )
        else:  # delete
            summary = change.get("before", {}).get("summary", "Unknown")

        print(f'{change_id}: {action.upper()} "{summary}"{undo_marker}')
        print(f"  Time: {ts_str}")
        print(f"  Event ID: {event_id}")

        if action == "update":
            before = change.get("before", {})
            after = change.get("after", {})
            changes_made = []
            if before.get("summary") != after.get("summary"):
                changes_made.append(
                    f'title: "{before.get("summary")}" -> "{after.get("summary")}"'
                )
            if before.get("start") != after.get("start"):
                changes_made.append(
                    f"start: {before.get('start')} -> {after.get('start')}"
                )
            if changes_made:
                print(f"  Changes: {'; '.join(changes_made)}")

        print()


def get_change(change_id: str) -> None:
    """Print a specific change as JSON."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})

    for change in changelog.get("changes", []):
        if change.get("id") == change_id:
            print(json.dumps(change, indent=2))
            return

    print(f"Change {change_id} not found", file=sys.stderr)
    sys.exit(1)


def can_undo(change_id: str) -> None:
    """Check if a change can be undone. Prints 'true' or 'false'."""
    changelog = load_json(CHANGELOG_FILE, {"changes": []})
    undo_window = timedelta(hours=UNDO_WINDOW_HOURS)
    now = datetime.now()

    for change in changelog.get("changes", []):
        if change.get("id") == change_id:
            if not change.get("can_undo", False):
                print("false")
                return

            try:
                change_time = datetime.fromisoformat(change.get("timestamp", ""))
                if (now - change_time) < undo_window:
                    print("true")
                    return
            except (ValueError, TypeError):
                pass

            print("false")
            return

    print("false")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: changelog_ops.py <action> [options]", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    # Parse keyword arguments from command line
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

    if action == "log-create":
        change_id = log_create(
            event_id=args.get("event_id", ""),
            calendar_id=args.get("calendar_id", "primary"),
            summary=args.get("summary", ""),
            start_time=args.get("start", ""),
            end_time=args.get("end", ""),
            email_id=args.get("email_id", "")
        )
        print(change_id)

    elif action == "log-update":
        change_id = log_update(
            event_id=args.get("event_id", ""),
            calendar_id=args.get("calendar_id", "primary"),
            before_json=args.get("before_json", ""),
            after_json=args.get("after_json", ""),
            email_id=args.get("email_id", "")
        )
        print(change_id)

    elif action == "log-delete":
        change_id = log_delete(
            event_id=args.get("event_id", ""),
            calendar_id=args.get("calendar_id", "primary"),
            before_json=args.get("before_json", "")
        )
        print(change_id)

    elif action == "list":
        last_n = int(args.get("last", 10))
        list_changes(last_n)

    elif action == "get":
        get_change(args.get("change_id", ""))

    elif action == "can-undo":
        can_undo(args.get("change_id", ""))

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

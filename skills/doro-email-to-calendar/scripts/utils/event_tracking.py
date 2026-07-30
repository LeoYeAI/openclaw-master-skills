#!/usr/bin/env python3
"""
Event tracking operations for email-to-calendar skill.

Manages tracking of calendar events for duplicate detection and updates.
"""

import json
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from json_store import load_json, save_json

EVENTS_FILE = os.path.expanduser(
    "~/.openclaw/workspace/memory/email-to-calendar/events.json"
)


def track_event(
    event_id: str,
    calendar_id: str = "primary",
    email_id: str = "",
    summary: str = "",
    start: str = ""
) -> None:
    """Track a new or updated event."""
    data = load_json(EVENTS_FILE, {"events": []})
    created_at = datetime.now().isoformat()

    # Check if event already tracked
    existing = next(
        (e for e in data["events"] if e["event_id"] == event_id),
        None
    )

    if existing:
        # Update existing entry
        existing["summary"] = summary
        existing["start"] = start
        existing["updated_at"] = created_at
        if email_id:
            existing["email_id"] = email_id
    else:
        # Add new entry
        new_event = {
            "event_id": event_id,
            "calendar_id": calendar_id,
            "email_id": email_id if email_id else None,
            "summary": summary,
            "start": start,
            "created_at": created_at,
            "updated_at": None
        }
        data["events"].append(new_event)

    save_json(EVENTS_FILE, data)
    print(f"Tracked event: {event_id}")


def update_tracked_event(
    event_id: str,
    summary: str = "",
    start: str = ""
) -> None:
    """Update a tracked event's metadata."""
    data = load_json(EVENTS_FILE, {"events": []})

    found = False
    for event in data.get("events", []):
        if event.get("event_id") == event_id:
            if summary:
                event["summary"] = summary
            if start:
                event["start"] = start
            event["updated_at"] = datetime.now().isoformat()
            found = True
            break

    if not found:
        print(f"Warning: Event {event_id} not found in tracking", file=sys.stderr)
        sys.exit(1)

    save_json(EVENTS_FILE, data)
    print(f"Updated tracked event: {event_id}")


def delete_tracked_event(event_id: str) -> None:
    """Delete an event from tracking."""
    data = load_json(EVENTS_FILE, {"events": []})

    original_count = len(data.get("events", []))
    data["events"] = [
        e for e in data.get("events", [])
        if e.get("event_id") != event_id
    ]
    new_count = len(data["events"])

    if original_count == new_count:
        print(f"Warning: Event {event_id} not found in tracking", file=sys.stderr)
    else:
        save_json(EVENTS_FILE, data)
        print(f"Deleted tracked event: {event_id}")


def lookup_events(
    search_type: str,
    search_value: str = "",
    validate: bool = False,
    script_dir: str = "",
    provider: str = ""
) -> None:
    """Look up tracked events and print as JSON."""
    import subprocess

    # Import calendar_ops for validation
    from calendar_ops import search_events

    data = load_json(EVENTS_FILE, {"events": []})
    events = data.get("events", [])

    if search_type == "list":
        results = events
    elif search_type == "email_id":
        results = [e for e in events if e.get("email_id") == search_value]
    elif search_type == "event_id":
        results = [e for e in events if e.get("event_id") == search_value]
    elif search_type == "summary":
        search_lower = search_value.lower()
        results = [
            e for e in events
            if search_lower in e.get("summary", "").lower()
        ]
    else:
        results = []

    # If validation requested, check each result and remove orphans
    if validate and results:
        valid_results = []
        for event in results:
            event_id = event.get("event_id")
            calendar_id = event.get("calendar_id", "primary")

            try:
                start = event.get("start", "")
                if start:
                    date_part = start.split("T")[0]
                    from_dt = f"{date_part}T00:00:00"
                    to_dt = f"{date_part}T23:59:59"

                    # Use calendar_ops.search_events instead of direct gog call
                    search_result = search_events(
                        calendar_id=calendar_id,
                        from_dt=from_dt,
                        to_dt=to_dt,
                        provider=provider if provider else None
                    )

                    if search_result.get("success"):
                        cal_events = search_result.get("data", []) or []
                        found = any(e.get("id") == event_id for e in cal_events)
                        if found:
                            valid_results.append(event)
                        else:
                            print(f"Orphaned event detected: {event_id} - removing from tracking", file=sys.stderr)
                            if script_dir:
                                subprocess.run(
                                    f'{script_dir}/delete_tracked_event.sh --event-id "{event_id}"',
                                    shell=True, capture_output=True
                                )
                    else:
                        # On error, assume event still exists
                        valid_results.append(event)
                else:
                    valid_results.append(event)
            except Exception:
                valid_results.append(event)

        results = valid_results

    print(json.dumps(results, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: event_tracking.py <action> [options]", file=sys.stderr)
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

    if action == "track":
        track_event(
            event_id=args.get("event_id", ""),
            calendar_id=args.get("calendar_id", "primary"),
            email_id=args.get("email_id", ""),
            summary=args.get("summary", ""),
            start=args.get("start", "")
        )

    elif action == "update":
        update_tracked_event(
            event_id=args.get("event_id", ""),
            summary=args.get("summary", ""),
            start=args.get("start", "")
        )

    elif action == "delete":
        delete_tracked_event(args.get("event_id", ""))

    elif action == "lookup":
        lookup_events(
            search_type=args.get("type", "list"),
            search_value=args.get("value", ""),
            validate=args.get("validate", False) == True or args.get("validate", "") == "true",
            script_dir=args.get("script_dir", ""),
            provider=args.get("provider", "")
        )

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

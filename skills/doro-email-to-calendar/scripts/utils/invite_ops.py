#!/usr/bin/env python3
"""
Invite status operations for email-to-calendar skill.

Manages updating the status of pending calendar invites.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from json_store import load_json, save_json

PENDING_FILE = os.path.expanduser(
    "~/.openclaw/workspace/memory/email-to-calendar/pending_invites.json"
)


def update_invite_status(
    invite_id: str = "",
    email_id: str = "",
    event_title: str = "",
    new_status: str = "",
    calendar_event_id: str = ""
) -> None:
    """Update the status of a pending invite event."""
    data = load_json(PENDING_FILE, {"invites": []})

    updated = False
    for invite in data.get("invites", []):
        # Match by invite_id or email_id
        if invite_id and invite.get("id") != invite_id:
            continue
        if email_id and invite.get("email_id") != email_id:
            continue

        # Find and update the event
        for event in invite.get("events", []):
            # Match by exact title or partial match
            event_name = event.get("title", "")
            if event_name == event_title or event_title.lower() in event_name.lower():
                event["status"] = new_status
                if calendar_event_id:
                    event["event_id"] = calendar_event_id
                event["updated_at"] = datetime.now().isoformat()
                updated = True
                print(f"Updated '{event_name}' to status: {new_status}")
                break

        if updated:
            break

    if not updated:
        print(f"Warning: No matching event found for '{event_title}'", file=sys.stderr)
        sys.exit(1)

    save_json(PENDING_FILE, data)


def main():
    # Parse arguments
    args = {}
    i = 1
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

    # Validate required arguments
    if not args.get("event_title") or not args.get("status"):
        print("Error: --event-title and --status are required", file=sys.stderr)
        sys.exit(1)

    if not args.get("invite_id") and not args.get("email_id"):
        print("Error: Either --invite-id or --email-id is required", file=sys.stderr)
        sys.exit(1)

    # Validate status
    valid_statuses = ["pending", "created", "dismissed", "expired"]
    if args.get("status") not in valid_statuses:
        print(f"Error: Invalid status. Must be: {', '.join(valid_statuses)}", file=sys.stderr)
        sys.exit(1)

    update_invite_status(
        invite_id=args.get("invite_id", ""),
        email_id=args.get("email_id", ""),
        event_title=args.get("event_title", ""),
        new_status=args.get("status", ""),
        calendar_event_id=args.get("event_id", "")
    )


if __name__ == "__main__":
    main()

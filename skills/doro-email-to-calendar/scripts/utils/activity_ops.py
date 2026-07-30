#!/usr/bin/env python3
"""
Activity log operations for email-to-calendar skill.

Manages the silent audit trail for email processing sessions.
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from json_store import load_json, save_json
from common import format_timestamp

ACTIVITY_FILE = os.path.expanduser(
    "~/.openclaw/workspace/memory/email-to-calendar/activity.json"
)
SESSION_FILE = os.path.expanduser(
    "~/.openclaw/workspace/memory/email-to-calendar/.current_session.json"
)
MAX_SESSIONS = 50


def start_session() -> None:
    """Start a new processing session."""
    session = {
        "timestamp": datetime.now().isoformat(),
        "emails_scanned": 0,
        "emails_with_events": 0,
        "skipped": [],
        "events_extracted": []
    }
    save_json(SESSION_FILE, session)
    print("Session started")


def log_skip(email_id: str, subject: str, reason: str) -> None:
    """Log a skipped email."""
    session = load_json(SESSION_FILE, None)
    if session is None:
        print("No active session. Call start-session first.", file=sys.stderr)
        sys.exit(1)

    session["emails_scanned"] = session.get("emails_scanned", 0) + 1
    session["skipped"].append({
        "email_id": email_id,
        "subject": subject,
        "reason": reason
    })
    save_json(SESSION_FILE, session)


def log_event(
    email_id: str,
    title: str,
    action: str = "pending",
    reason: str = ""
) -> None:
    """Log an extracted event."""
    session = load_json(SESSION_FILE, None)
    if session is None:
        print("No active session. Call start-session first.", file=sys.stderr)
        sys.exit(1)

    # Only increment emails_with_events once per email
    existing_emails = set(
        e.get("email_id") for e in session.get("events_extracted", [])
    )
    if email_id not in existing_emails:
        session["emails_with_events"] = session.get("emails_with_events", 0) + 1

    entry = {
        "email_id": email_id,
        "title": title,
        "action": action
    }
    if reason:
        entry["reason"] = reason

    session["events_extracted"].append(entry)
    save_json(SESSION_FILE, session)


def end_session() -> None:
    """Finalize the current session and append to activity log."""
    session = load_json(SESSION_FILE, None)
    if session is None:
        print("No active session to end.")
        return

    # Load existing activity log
    activity = load_json(ACTIVITY_FILE, {"sessions": []})

    # Add session to log
    activity["sessions"].append(session)

    # Keep only last N sessions
    activity["sessions"] = activity["sessions"][-MAX_SESSIONS:]

    # Save activity log
    save_json(ACTIVITY_FILE, activity)

    # Remove current session file
    try:
        os.remove(os.path.expanduser(SESSION_FILE))
    except OSError:
        pass

    emails_scanned = session.get("emails_scanned", 0)
    emails_with_events = session.get("emails_with_events", 0)
    skipped = len(session.get("skipped", []))
    print(f"Session ended: {emails_scanned} scanned, {emails_with_events} with events, {skipped} skipped")


def show_activity(last_n: int = 1) -> None:
    """Show recent activity sessions."""
    activity = load_json(ACTIVITY_FILE, {"sessions": []})
    sessions = activity.get("sessions", [])

    if not sessions:
        print("No activity recorded yet.")
        return

    # Get last N sessions
    recent = sessions[-last_n:]

    for session in recent:
        ts = session.get("timestamp", "Unknown time")
        ts_formatted = format_timestamp(ts)

        print(f"\n=== Session: {ts_formatted} ===")
        print(f"Emails scanned: {session.get('emails_scanned', 0)}")
        print(f"Emails with events: {session.get('emails_with_events', 0)}")

        skipped = session.get("skipped", [])
        if skipped:
            print(f"\nSkipped ({len(skipped)}):")
            for s in skipped:
                subj = s.get("subject", "Unknown")[:50]
                reason = s.get("reason", "Unknown reason")
                print(f"  - {subj}")
                print(f"    Reason: {reason}")

        events = session.get("events_extracted", [])
        if events:
            print(f"\nEvents ({len(events)}):")
            for e in events:
                title = e.get("title", "Untitled")
                action = e.get("action", "unknown")
                reason = e.get("reason", "")
                print(f"  - {title}")
                reason_str = f" ({reason})" if reason else ""
                print(f"    Action: {action}{reason_str}")


def main():
    if len(sys.argv) < 2:
        print("Usage: activity_ops.py <action> [options]", file=sys.stderr)
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

    if action == "start-session":
        start_session()

    elif action == "log-skip":
        if not args.get("email_id") or not args.get("reason"):
            print("Error: --email-id and --reason are required", file=sys.stderr)
            sys.exit(1)
        log_skip(
            email_id=args["email_id"],
            subject=args.get("subject", ""),
            reason=args["reason"]
        )

    elif action == "log-event":
        if not args.get("email_id") or not args.get("title"):
            print("Error: --email-id and --title are required", file=sys.stderr)
            sys.exit(1)
        log_event(
            email_id=args["email_id"],
            title=args["title"],
            action=args.get("action", "pending"),
            reason=args.get("reason", "")
        )

    elif action == "end-session":
        end_session()

    elif action == "show":
        last_n = int(args.get("last", 1))
        show_activity(last_n)

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Provider-agnostic calendar operations for email-to-calendar skill.

Provides a consistent interface for calendar operations across different providers.
Currently supports: gog (Google Calendar via gog CLI)
"""

import json
import os
import subprocess
import sys
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from json_store import load_json

CONFIG_FILE = os.path.expanduser("~/.config/email-to-calendar/config.json")


def get_provider(provider: Optional[str] = None) -> str:
    """Get the provider to use, from parameter or config."""
    if provider:
        return provider
    config = load_json(CONFIG_FILE, {})
    return config.get("provider", "gog")


def get_calendar_id() -> str:
    """Get the default calendar ID from config."""
    config = load_json(CONFIG_FILE, {})
    return config.get("calendar_id", "primary")


def _check_send_updates_support() -> bool:
    """Check if gog supports --send-updates flag (tonimelisma fork)."""
    try:
        result = subprocess.run(
            ["gog", "calendar", "create", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return "--send-updates" in result.stdout or "--send-updates" in result.stderr
    except Exception:
        return False


def _run_gog_command(args: List[str]) -> Dict[str, Any]:
    """Run a gog command and return structured result."""
    try:
        result = subprocess.run(
            ["gog"] + args,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            # Try to parse as JSON
            try:
                data = json.loads(result.stdout) if result.stdout.strip() else None
                return {"success": True, "data": data, "raw": result.stdout}
            except json.JSONDecodeError:
                return {"success": True, "data": None, "raw": result.stdout}
        else:
            error_text = result.stderr or result.stdout
            # Check for 404/410 (event deleted externally)
            if any(x in error_text.lower() for x in ["404", "not found", "410", "gone", "does not exist", "deleted"]):
                return {
                    "success": False,
                    "error": error_text,
                    "error_type": "not_found",
                    "returncode": result.returncode
                }
            return {
                "success": False,
                "error": error_text,
                "returncode": result.returncode
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "gog command not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_events(
    calendar_id: Optional[str] = None,
    from_dt: Optional[str] = None,
    to_dt: Optional[str] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for calendar events in a date range.

    Args:
        calendar_id: Calendar ID (default: from config)
        from_dt: Start datetime (ISO format)
        to_dt: End datetime (ISO format)
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status and list of events or error
    """
    provider = get_provider(provider)
    calendar_id = calendar_id or get_calendar_id()

    if provider == "gog":
        args = ["calendar", "events", calendar_id, "--json"]
        if from_dt:
            args.extend(["--from", from_dt])
        if to_dt:
            args.extend(["--to", to_dt])
        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def create_event(
    summary: str,
    from_dt: str,
    to_dt: str,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    calendar_id: Optional[str] = None,
    reminders: Optional[List[str]] = None,
    rrule: Optional[str] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new calendar event.

    Args:
        summary: Event title
        from_dt: Start datetime (ISO format)
        to_dt: End datetime (ISO format)
        description: Event description
        attendees: List of attendee email addresses
        calendar_id: Calendar ID (default: from config)
        reminders: List of reminders (e.g., ["email:1d", "popup:1h"])
        rrule: Recurrence rule (e.g., "RRULE:FREQ=DAILY;COUNT=5")
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status and event data (including id) or error
    """
    provider = get_provider(provider)
    calendar_id = calendar_id or get_calendar_id()

    if provider == "gog":
        args = ["calendar", "create", calendar_id,
                "--summary", summary,
                "--from", from_dt,
                "--to", to_dt,
                "--json"]

        if description:
            args.extend(["--description", description])

        if attendees:
            args.extend(["--attendees", ",".join(attendees)])
            # Add send-updates if supported
            if _check_send_updates_support():
                args.extend(["--send-updates", "all"])

        if reminders:
            for reminder in reminders:
                args.extend(["--reminder", reminder])

        if rrule:
            args.extend(["--rrule", rrule])

        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def update_event(
    event_id: str,
    summary: Optional[str] = None,
    from_dt: Optional[str] = None,
    to_dt: Optional[str] = None,
    description: Optional[str] = None,
    add_attendees: Optional[List[str]] = None,
    calendar_id: Optional[str] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing calendar event.

    Args:
        event_id: The event ID to update
        summary: New event title
        from_dt: New start datetime (ISO format)
        to_dt: New end datetime (ISO format)
        description: New event description
        add_attendees: Attendee emails to add
        calendar_id: Calendar ID (default: from config)
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status and updated event data or error
    """
    provider = get_provider(provider)
    calendar_id = calendar_id or get_calendar_id()

    if provider == "gog":
        args = ["calendar", "update", calendar_id, event_id]

        if summary:
            args.extend(["--summary", summary])
        if from_dt:
            args.extend(["--from", from_dt])
        if to_dt:
            args.extend(["--to", to_dt])
        if description:
            args.extend(["--description", description])
        if add_attendees:
            args.extend(["--add-attendee", ",".join(add_attendees)])
            if _check_send_updates_support():
                args.extend(["--send-updates", "all"])

        args.append("--json")
        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def delete_event(
    event_id: str,
    calendar_id: Optional[str] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a calendar event.

    Args:
        event_id: The event ID to delete
        calendar_id: Calendar ID (default: from config)
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status or error
    """
    provider = get_provider(provider)
    calendar_id = calendar_id or get_calendar_id()

    if provider == "gog":
        args = ["calendar", "delete", calendar_id, event_id]
        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def main():
    """CLI interface for calendar operations."""
    if len(sys.argv) < 2:
        print("Usage: calendar_ops.py <action> [options]", file=sys.stderr)
        print("Actions: search, create, update, delete", file=sys.stderr)
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

    provider = args.get("provider")
    calendar_id = args.get("calendar_id")

    if action == "search":
        from_dt = args.get("from")
        to_dt = args.get("to")
        result = search_events(calendar_id, from_dt, to_dt, provider)

    elif action == "create":
        summary = args.get("summary", "")
        from_dt = args.get("from", "")
        to_dt = args.get("to", "")
        if not summary or not from_dt or not to_dt:
            print("Error: --summary, --from, and --to required", file=sys.stderr)
            sys.exit(1)
        description = args.get("description")
        attendees = args.get("attendees", "").split(",") if args.get("attendees") else None
        reminders = args.get("reminders", "").split(",") if args.get("reminders") else None
        rrule = args.get("rrule")
        result = create_event(summary, from_dt, to_dt, description, attendees,
                             calendar_id, reminders, rrule, provider)

    elif action == "update":
        event_id = args.get("event_id", "")
        if not event_id:
            print("Error: --event-id required", file=sys.stderr)
            sys.exit(1)
        summary = args.get("summary")
        from_dt = args.get("from")
        to_dt = args.get("to")
        description = args.get("description")
        add_attendees = args.get("add_attendees", "").split(",") if args.get("add_attendees") else None
        result = update_event(event_id, summary, from_dt, to_dt, description,
                             add_attendees, calendar_id, provider)

    elif action == "delete":
        event_id = args.get("event_id", "")
        if not event_id:
            print("Error: --event-id required", file=sys.stderr)
            sys.exit(1)
        result = delete_event(event_id, calendar_id, provider)

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

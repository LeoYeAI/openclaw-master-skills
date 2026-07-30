#!/usr/bin/env python3
"""
Email disposition operations for email-to-calendar skill.

Provides functions to mark emails as read and archive them based on config settings.
"""

import json
import os
import sys
from typing import Dict, Any, Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from json_store import load_json
from email_ops import modify_email, get_provider

CONFIG_FILE = os.path.expanduser("~/.config/email-to-calendar/config.json")


def get_disposition_settings(config_file: Optional[str] = None) -> Dict[str, bool]:
    """
    Get email disposition settings from config.

    Args:
        config_file: Optional path to config file (for testing)

    Returns:
        Dict with keys: mark_read, archive, auto_dispose_calendar_replies
        All default to True if not specified
    """
    config_path = config_file or CONFIG_FILE
    config = load_json(config_path, {})
    email_handling = config.get("email_handling", {})

    return {
        "mark_read": email_handling.get("mark_read", True),
        "archive": email_handling.get("archive", True),
        "auto_dispose_calendar_replies": email_handling.get("auto_dispose_calendar_replies", True)
    }


def disposition_email(
    email_id: str,
    settings: Optional[Dict[str, bool]] = None,
    mark_read: Optional[bool] = None,
    archive: Optional[bool] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply disposition (mark read/archive) to an email based on config.

    Args:
        email_id: The email message ID
        settings: Optional settings dict to override config
        mark_read: Optional override for mark_read setting
        archive: Optional override for archive setting
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status, actions taken, and any error
    """
    if not email_id:
        return {"success": False, "error": "email_id is required", "actions": []}

    # Get settings from config if not provided
    if settings is None:
        settings = get_disposition_settings()

    # Allow explicit overrides
    should_mark_read = mark_read if mark_read is not None else settings.get("mark_read", True)
    should_archive = archive if archive is not None else settings.get("archive", True)

    actions = []
    remove_labels: List[str] = []

    # Build list of labels to remove
    if should_mark_read:
        remove_labels.append("UNREAD")
        actions.append("mark_read")

    if should_archive:
        remove_labels.append("INBOX")
        actions.append("archive")

    # If no actions needed, return success
    if not remove_labels:
        return {"success": True, "actions": [], "message": "No disposition actions configured"}

    # Perform the modification
    result = modify_email(email_id, remove_labels=remove_labels, provider=provider)

    if result.get("success"):
        return {
            "success": True,
            "actions": actions,
            "email_id": email_id,
            "labels_removed": remove_labels
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Unknown error"),
            "actions": [],
            "email_id": email_id
        }


def is_calendar_reply(subject: str) -> bool:
    """
    Check if an email subject indicates it's a calendar reply.

    Args:
        subject: Email subject line

    Returns:
        True if it matches calendar reply patterns
    """
    if not subject:
        return False

    subject_lower = subject.lower()
    patterns = [
        "accepted:",
        "declined:",
        "tentative:",
        "updated invitation:",
        "cancelled:",
        "canceled:",  # US spelling
    ]

    return any(subject_lower.startswith(p) for p in patterns)


def main():
    """CLI interface for disposition operations."""
    if len(sys.argv) < 2:
        print("Usage: disposition_ops.py <action> [options]", file=sys.stderr)
        print("Actions: disposition, settings", file=sys.stderr)
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

    if action == "disposition":
        email_id = args.get("email_id", "")
        if not email_id:
            print("Error: --email-id required", file=sys.stderr)
            sys.exit(1)

        # Parse optional overrides
        mark_read = None
        archive = None

        if args.get("mark_read") is not None:
            mark_read = str(args.get("mark_read")).lower() == "true"
        if args.get("no_mark_read"):
            mark_read = False
        if args.get("archive") is not None:
            archive = str(args.get("archive")).lower() == "true"
        if args.get("no_archive"):
            archive = False

        result = disposition_email(
            email_id,
            mark_read=mark_read,
            archive=archive,
            provider=args.get("provider")
        )

    elif action == "settings":
        result = get_disposition_settings()

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success", True) else 1)


if __name__ == "__main__":
    main()

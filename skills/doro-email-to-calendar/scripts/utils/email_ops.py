#!/usr/bin/env python3
"""
Provider-agnostic email operations for email-to-calendar skill.

Provides a consistent interface for email operations across different providers.
Currently supports: gog (Gmail via gog CLI)
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


def get_gmail_account() -> str:
    """Get the Gmail account from config."""
    config = load_json(CONFIG_FILE, {})
    return config.get("gmail_account", "")


def _run_gog_command(args: List[str]) -> Dict[str, Any]:
    """Run a gog command and return structured result."""
    try:
        result = subprocess.run(
            ["gog"] + args,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            # Try to parse as JSON
            try:
                data = json.loads(result.stdout) if result.stdout.strip() else None
                return {"success": True, "data": data, "raw": result.stdout}
            except json.JSONDecodeError:
                return {"success": True, "data": None, "raw": result.stdout}
        else:
            return {
                "success": False,
                "error": result.stderr or result.stdout,
                "returncode": result.returncode
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "gog command not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_email(email_id: str, provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Read a single email by ID.

    Args:
        email_id: The email message ID
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status and email data or error
    """
    provider = get_provider(provider)

    if provider == "gog":
        account = get_gmail_account()
        args = ["gmail", "get", email_id]
        if account:
            args.extend(["--account", account])
        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def search_emails(
    query: str,
    max_results: int = 20,
    include_body: bool = False,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for emails matching a query.

    Args:
        query: Search query (e.g., "in:inbox is:unread")
        max_results: Maximum number of results
        include_body: Whether to include email body content
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status and list of emails or error
    """
    provider = get_provider(provider)

    if provider == "gog":
        account = get_gmail_account()
        args = ["gmail", "messages", "search", query, "--max", str(max_results)]
        if include_body:
            args.append("--include-body")
        if account:
            args.extend(["--account", account])
        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def modify_email(
    email_id: str,
    remove_labels: Optional[List[str]] = None,
    add_labels: Optional[List[str]] = None,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Modify an email (add/remove labels).

    Args:
        email_id: The email message ID
        remove_labels: Labels to remove (e.g., ["UNREAD"])
        add_labels: Labels to add
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status or error
    """
    provider = get_provider(provider)

    if provider == "gog":
        account = get_gmail_account()
        args = ["gmail", "modify", email_id]

        if remove_labels:
            args.extend(["--remove-labels", ",".join(remove_labels)])
        if add_labels:
            args.extend(["--add-labels", ",".join(add_labels)])
        if account:
            args.extend(["--account", account])

        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def send_email(
    to: str,
    subject: str,
    body: str,
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        provider: Provider to use (default: from config)

    Returns:
        Dict with success status or error
    """
    provider = get_provider(provider)

    if provider == "gog":
        account = get_gmail_account()
        args = ["gmail", "send", "--to", to, "--subject", subject, "--body", body]
        if account:
            args.extend(["--account", account])
        return _run_gog_command(args)
    else:
        return {"success": False, "error": f"Unknown provider: {provider}"}


def main():
    """CLI interface for email operations."""
    if len(sys.argv) < 2:
        print("Usage: email_ops.py <action> [options]", file=sys.stderr)
        print("Actions: read, search, modify, send", file=sys.stderr)
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

    if action == "read":
        email_id = args.get("email_id", "")
        if not email_id:
            print("Error: --email-id required", file=sys.stderr)
            sys.exit(1)
        result = read_email(email_id, provider)

    elif action == "search":
        query = args.get("query", "")
        if not query:
            print("Error: --query required", file=sys.stderr)
            sys.exit(1)
        max_results = int(args.get("max", 20))
        include_body = args.get("include_body", False) == True or args.get("include_body", "") == "true"
        result = search_emails(query, max_results, include_body, provider)

    elif action == "modify":
        email_id = args.get("email_id", "")
        if not email_id:
            print("Error: --email-id required", file=sys.stderr)
            sys.exit(1)
        remove_labels = args.get("remove_labels", "").split(",") if args.get("remove_labels") else None
        add_labels = args.get("add_labels", "").split(",") if args.get("add_labels") else None
        result = modify_email(email_id, remove_labels, add_labels, provider)

    elif action == "send":
        to = args.get("to", "")
        subject = args.get("subject", "")
        body = args.get("body", "")
        if not to or not subject:
            print("Error: --to and --subject required", file=sys.stderr)
            sys.exit(1)
        result = send_email(to, subject, body, provider)

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Didit Sessions - Create verification sessions and retrieve decisions.

Usage:
    python scripts/create_session.py create --workflow-id UUID [--vendor-data ID] [--callback URL]
    python scripts/create_session.py get <session_id>
    python scripts/create_session.py list [--status STATUS] [--vendor-data ID]

Environment:
    DIDIT_API_KEY - Required. Your Didit API key.

Examples:
    python scripts/create_session.py create --workflow-id d8d2fa2d-... --vendor-data user-123
    python scripts/create_session.py get 11111111-2222-3333-4444-555555555555
    python scripts/create_session.py list --status Approved --vendor-data user-123
"""
import argparse
import json
import os
import sys

import requests

BASE_URL = "https://verification.didit.me/v3"


def get_headers(content_type=False) -> dict:
    api_key = os.environ.get("DIDIT_API_KEY")
    if not api_key:
        print("Error: DIDIT_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    h = {"x-api-key": api_key}
    if content_type:
        h["Content-Type"] = "application/json"
    return h


def create_session(workflow_id: str, vendor_data: str = None, callback: str = None,
                   language: str = None, metadata: str = None) -> dict:
    payload = {"workflow_id": workflow_id}
    if vendor_data:
        payload["vendor_data"] = vendor_data
    if callback:
        payload["callback"] = callback
    if language:
        payload["language"] = language
    if metadata:
        payload["metadata"] = metadata
    r = requests.post(f"{BASE_URL}/session/", headers=get_headers(content_type=True),
                      json=payload, timeout=30)
    if r.status_code not in (200, 201):
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def get_decision(session_id: str) -> dict:
    r = requests.get(f"{BASE_URL}/session/{session_id}/decision/",
                     headers=get_headers(), timeout=30)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def list_sessions(status: str = None, vendor_data: str = None, page: int = 1) -> dict:
    params = {"page": page}
    if status:
        params["status"] = status
    if vendor_data:
        params["vendor_data"] = vendor_data
    r = requests.get(f"{BASE_URL}/sessions/", headers=get_headers(),
                     params=params, timeout=30)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Manage Didit verification sessions")
    sub = parser.add_subparsers(dest="command", required=True)

    create_p = sub.add_parser("create", help="Create a new verification session")
    create_p.add_argument("--workflow-id", required=True, help="Workflow UUID")
    create_p.add_argument("--vendor-data", help="Your user identifier")
    create_p.add_argument("--callback", help="Redirect URL after verification")
    create_p.add_argument("--language", help="UI language (ISO 639-1)")
    create_p.add_argument("--metadata", help="Custom JSON metadata string")

    get_p = sub.add_parser("get", help="Get session decision")
    get_p.add_argument("session_id", help="Session UUID")

    list_p = sub.add_parser("list", help="List sessions")
    list_p.add_argument("--status", help="Filter by status")
    list_p.add_argument("--vendor-data", help="Filter by vendor_data")
    list_p.add_argument("--page", type=int, default=1, help="Page number")

    args = parser.parse_args()

    if args.command == "create":
        result = create_session(args.workflow_id, args.vendor_data, args.callback,
                                args.language, args.metadata)
        print(json.dumps(result, indent=2))
        print(f"\n--- Session created ---")
        print(f"Session ID: {result.get('session_id')}")
        print(f"URL: {result.get('url')}")
        print(f"Status: {result.get('status')}")

    elif args.command == "get":
        result = get_decision(args.session_id)
        print(json.dumps(result, indent=2))
        print(f"\n--- Status: {result.get('status')} ---")

    elif args.command == "list":
        result = list_sessions(args.status, args.vendor_data, args.page)
        print(json.dumps(result, indent=2))
        print(f"\n--- {result.get('count', 0)} session(s) total ---")


if __name__ == "__main__":
    main()

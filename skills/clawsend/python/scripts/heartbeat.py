#!/usr/bin/env python3
"""
Heartbeat check for ClawSend messages.

Lightweight script for agents to check if new messages exist during
their heartbeat cycle. Does NOT fetch or mark messages as delivered.

Usage:
    python heartbeat.py              # Check for unread messages
    python heartbeat.py --json       # JSON output
    python heartbeat.py --notify     # Also check local notification file

Exit codes:
    0 - Has unread messages
    1 - No unread messages
    2 - Error
"""

import argparse
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.vault import Vault, VaultNotFoundError
from lib.client import RelayClient, output_json, output_error, ClientError
from lib.auto_setup import ensure_ready, DEFAULT_RELAY


def check_notifications_file(vault_dir=None):
    """Check local notifications file for unread entries."""
    if vault_dir:
        notif_path = os.path.join(vault_dir, 'notifications.jsonl')
    else:
        notif_path = os.path.expanduser('~/.openclaw/vault/notifications.jsonl')

    if not os.path.exists(notif_path):
        return {'exists': False, 'count': 0, 'latest': None}

    try:
        with open(notif_path, 'r') as f:
            lines = f.readlines()

        count = len(lines)
        latest = None
        if lines:
            try:
                latest = json.loads(lines[-1].strip())
            except json.JSONDecodeError:
                pass

        return {'exists': True, 'count': count, 'latest': latest}
    except Exception as e:
        return {'exists': True, 'count': 0, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='Check for unread ClawSend messages (heartbeat)'
    )
    parser.add_argument(
        '--server',
        default=DEFAULT_RELAY,
        help=f'Relay server URL (default: {DEFAULT_RELAY})'
    )
    parser.add_argument(
        '--vault-dir',
        help='Custom vault directory'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--notify',
        action='store_true',
        help='Also check local notification file'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only output if there are messages'
    )
    args = parser.parse_args()

    # Load vault
    try:
        vault = ensure_ready(
            vault_dir=args.vault_dir,
            server=args.server,
            json_mode=args.json,
        )
    except Exception as e:
        if args.json:
            output_error(f'Setup failed: {e}', code='setup_error')
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Check server for unread messages
    try:
        client = RelayClient(vault, args.server)
        response = client._request('GET', f'/unread/{vault.vault_id}')

        unread_count = response.get('unread_count', 0)
        has_messages = response.get('has_messages', False)

    except ClientError as e:
        if args.json:
            output_error(str(e), code='server_error')
        else:
            print(f"Error checking server: {e}", file=sys.stderr)
        sys.exit(2)

    # Check local notifications if requested
    local_notifications = None
    if args.notify:
        local_notifications = check_notifications_file(args.vault_dir)

    # Build result
    result = {
        'vault_id': vault.vault_id,
        'unread_count': unread_count,
        'has_messages': has_messages,
        'server': args.server,
    }

    if local_notifications:
        result['local_notifications'] = local_notifications

    # Output
    if args.json:
        output_json(result)
    else:
        if has_messages or not args.quiet:
            if has_messages:
                print(f"📬 {unread_count} unread message(s) waiting", file=sys.stderr)
            else:
                print("📭 No unread messages", file=sys.stderr)

            if local_notifications and local_notifications.get('count', 0) > 0:
                print(f"📋 {local_notifications['count']} local notification(s)", file=sys.stderr)

    # Exit code: 0 if has messages, 1 if no messages
    sys.exit(0 if has_messages else 1)


if __name__ == '__main__':
    main()

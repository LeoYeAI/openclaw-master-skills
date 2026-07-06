#!/usr/bin/env python3
"""
Acknowledge receipt of a message.

Tells the relay (and therefore the sender) that the message was received.

Usage:
    python ack.py MESSAGE_ID [--server URL] [--json]
"""

import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.vault import Vault, VaultNotFoundError
from lib.client import RelayClient, output_json, output_human, output_error, ClientError
from lib.auto_setup import ensure_ready, DEFAULT_RELAY


def main():
    parser = argparse.ArgumentParser(
        description='Acknowledge receipt of a message'
    )
    parser.add_argument(
        'message_id',
        help='ID of the message to acknowledge'
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
        help='Output as JSON to stdout'
    )
    args = parser.parse_args()

    # Auto-setup: create vault and register if needed
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
            print(f"Error: Setup failed: {e}", file=sys.stderr)
        sys.exit(1)

    client = RelayClient(vault, args.server)

    try:
        if not args.json:
            output_human(f"Acknowledging message {args.message_id}...")

        result = client.acknowledge(args.message_id)

        if args.json:
            output_json(result)
        else:
            print(f"Message acknowledged", file=sys.stderr)
            print(f"Message ID: {result['message_id']}", file=sys.stderr)
            print(f"Acknowledged at: {result['acknowledged_at']}", file=sys.stderr)

    except ClientError as e:
        if args.json:
            output_error(str(e), code=e.response.get('code') if e.response else 'error')
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if args.json:
            output_error(str(e))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

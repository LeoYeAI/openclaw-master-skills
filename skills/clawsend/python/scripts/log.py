#!/usr/bin/env python3
"""
View conversation logs and message history.

Shows conversations stored on the relay server or in local vault.

Usage:
    python log.py [--conversations] [--conversation-id ID] [--local] [--json]
"""

import argparse
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.vault import Vault, VaultNotFoundError
from lib.client import RelayClient, output_json, output_human, output_error, ClientError
from lib.auto_setup import ensure_ready, DEFAULT_RELAY


def main():
    parser = argparse.ArgumentParser(
        description='View conversation logs and message history'
    )
    parser.add_argument(
        '--conversations', '-c',
        action='store_true',
        help='List all conversations'
    )
    parser.add_argument(
        '--conversation-id', '-i',
        metavar='ID',
        help='View specific conversation'
    )
    parser.add_argument(
        '--local', '-l',
        action='store_true',
        help='View local message history instead of server logs'
    )
    parser.add_argument(
        '--quarantine', '-q',
        action='store_true',
        help='View quarantined messages'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum entries to show (default: 50)'
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

    try:
        # Local history
        if args.local:
            if not args.json:
                output_human("Loading local message history...")

            history = vault.get_history(limit=args.limit)

            if args.json:
                output_json({
                    'history': history,
                    'count': len(history),
                })
            else:
                if not history:
                    print("\nNo local message history.", file=sys.stderr)
                else:
                    print(f"\n{len(history)} message(s) in local history:", file=sys.stderr)
                    print("-" * 60, file=sys.stderr)

                    for entry in history:
                        direction = entry.get('direction', 'unknown')
                        saved_at = entry.get('saved_at', 'unknown')
                        message = entry.get('message', {})
                        envelope = message.get('envelope', {})
                        payload = message.get('payload', {})

                        print(f"\n[{direction.upper()}] {saved_at}", file=sys.stderr)
                        print(f"  ID: {envelope.get('id')}", file=sys.stderr)
                        print(f"  From: {envelope.get('sender')}", file=sys.stderr)
                        print(f"  To: {envelope.get('recipient')}", file=sys.stderr)
                        print(f"  Intent: {payload.get('intent')}", file=sys.stderr)
                        body = payload.get('body', {})
                        if body:
                            print(f"  Body: {json.dumps(body)[:100]}...", file=sys.stderr)

        # Quarantine
        elif args.quarantine:
            if not args.json:
                output_human("Loading quarantined messages...")

            quarantine = vault.get_quarantine(limit=args.limit)

            if args.json:
                output_json({
                    'quarantine': quarantine,
                    'count': len(quarantine),
                })
            else:
                if not quarantine:
                    print("\nNo quarantined messages.", file=sys.stderr)
                else:
                    print(f"\n{len(quarantine)} quarantined message(s):", file=sys.stderr)
                    print("-" * 60, file=sys.stderr)

                    for entry in quarantine:
                        reason = entry.get('reason', 'unknown')
                        quarantined_at = entry.get('quarantined_at', 'unknown')
                        message = entry.get('message', {})
                        envelope = message.get('envelope', {})

                        print(f"\n[QUARANTINED] {quarantined_at}", file=sys.stderr)
                        print(f"  Reason: {reason}", file=sys.stderr)
                        print(f"  ID: {envelope.get('id')}", file=sys.stderr)
                        print(f"  From: {envelope.get('sender')}", file=sys.stderr)

        # Server conversations
        elif args.conversation_id:
            client = RelayClient(vault, args.server)

            if not args.json:
                output_human(f"Loading conversation {args.conversation_id}...")

            result = client.get_conversation_log(args.conversation_id)

            if args.json:
                output_json(result)
            else:
                conv = result.get('conversation', {})
                messages = result.get('messages', [])

                print(f"\nConversation: {conv.get('id')}", file=sys.stderr)
                print(f"Participants: {conv.get('participant_a')} <-> {conv.get('participant_b')}", file=sys.stderr)
                print(f"Started: {conv.get('started_at')}", file=sys.stderr)
                print(f"Messages: {conv.get('message_count')}", file=sys.stderr)
                print("-" * 60, file=sys.stderr)

                for msg in messages:
                    direction = msg.get('direction', '')
                    arrow = '->' if direction == 'a_to_b' else '<-'
                    status = msg.get('status', 'unknown')

                    print(f"\n  {arrow} [{msg.get('intent')}] {msg.get('created_at')}", file=sys.stderr)
                    print(f"     ID: {msg.get('id')}", file=sys.stderr)
                    print(f"     Status: {status}", file=sys.stderr)
                    if msg.get('correlation_id'):
                        print(f"     Correlation: {msg.get('correlation_id')}", file=sys.stderr)

        # List conversations
        elif args.conversations:
            client = RelayClient(vault, args.server)

            if not args.json:
                output_human(f"Loading conversations from {args.server}...")

            result = client.get_agent_logs(limit=args.limit)
            conversations = result.get('conversations', [])

            if args.json:
                output_json(result)
            else:
                if not conversations:
                    print("\nNo conversations found.", file=sys.stderr)
                else:
                    print(f"\n{len(conversations)} conversation(s):", file=sys.stderr)
                    print("-" * 60, file=sys.stderr)

                    for conv in conversations:
                        other = conv.get('participant_a') if conv.get('participant_b') == vault.vault_id else conv.get('participant_b')
                        print(f"\n  [{conv.get('id')}]", file=sys.stderr)
                        print(f"    With: {other}", file=sys.stderr)
                        print(f"    Messages: {conv.get('message_count')}", file=sys.stderr)
                        print(f"    Last: {conv.get('last_message_at')}", file=sys.stderr)

        else:
            parser.print_help()

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

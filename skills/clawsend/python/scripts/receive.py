#!/usr/bin/env python3
"""
Receive messages from the ClawHub relay.

Fetches unread messages, verifies signatures, and optionally decrypts payloads.

Usage:
    python receive.py [--server URL] [--limit N] [--json]
    python receive.py --poll --interval 10  # Poll every 10 seconds
"""

import argparse
import json
import os
import sys
import time
import signal

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess

from lib.vault import Vault, VaultNotFoundError
from lib.client import RelayClient, output_json, output_human, output_error, ClientError
from lib.auto_setup import ensure_ready, DEFAULT_RELAY
from lib import crypto
from lib import envelope as env


def execute_callback(command: str, message: dict, quiet: bool = False):
    """
    Execute callback command with message data.

    The message JSON is passed via stdin to the command.

    Args:
        command: Shell command to execute
        message: Message data dict
        quiet: Suppress output if True
    """
    try:
        message_json = json.dumps(message, ensure_ascii=False)
        result = subprocess.run(
            command,
            shell=True,
            input=message_json,
            text=True,
            capture_output=True,
            timeout=30,  # 30 second timeout
        )
        if not quiet:
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, file=sys.stderr, end='')
        if result.returncode != 0:
            print(f"Callback exited with code {result.returncode}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"Callback timed out after 30 seconds", file=sys.stderr)
    except Exception as e:
        print(f"Callback error: {e}", file=sys.stderr)


def verify_message(message: dict, signature: str, sender_public_key: str) -> bool:
    """Verify message signature."""
    try:
        public_key = crypto.b64_to_public_signing_key(sender_public_key)
        signable = env.get_signable_content(message)
        return crypto.verify_json(public_key, signable, signature)
    except crypto.SignatureError:
        return False


# Track seen message IDs to avoid duplicates in polling mode
_seen_message_ids = set()

# Flag for graceful shutdown
_running = True


def signal_handler(signum, frame):
    """Handle interrupt signal for graceful shutdown."""
    global _running
    _running = False
    print("\nStopping message polling...", file=sys.stderr)


def fetch_and_process_messages(client, vault, args, sender_info_cache):
    """
    Fetch and process messages from the relay.

    Returns:
        List of processed messages (only new ones in polling mode)
    """
    global _seen_message_ids

    def get_sender_info(sender_id: str) -> dict:
        """Get sender's signing key and alias."""
        if sender_id in sender_info_cache:
            return sender_info_cache[sender_id]
        try:
            agents = client.list_agents(limit=500)
            for agent in agents.get('agents', []):
                sender_info_cache[agent['vault_id']] = {
                    'signing_public_key': agent['signing_public_key'],
                    'alias': agent.get('alias'),
                }
        except Exception:
            pass
        return sender_info_cache.get(sender_id, {})

    def get_sender_key(sender_id: str) -> str:
        return get_sender_info(sender_id).get('signing_public_key')

    def get_sender_alias(sender_id: str) -> str:
        """Get sender's alias, or vault_id if no alias."""
        info = get_sender_info(sender_id)
        return info.get('alias') or sender_id

    result = client.receive(limit=args.limit)
    messages = result.get('messages', [])

    processed = []

    for msg_data in messages:
        message_id = msg_data['message_id']

        # Skip already seen messages in polling mode
        if args.poll and message_id in _seen_message_ids:
            continue

        _seen_message_ids.add(message_id)

        message = msg_data['message']
        signature = msg_data['signature']
        sender = msg_data['sender']
        encrypted_payload = msg_data.get('encrypted_payload')

        # Resolve sender alias
        sender_alias = get_sender_alias(sender)

        msg_result = {
            'message_id': message_id,
            'sender': sender,
            'sender_alias': sender_alias,
            'received_at': msg_data['received_at'],
            'envelope': message['envelope'],
            'payload': message['payload'],
            'verified': False,
            'decrypted': False,
        }

        # Verify signature
        if not args.no_verify:
            sender_key = get_sender_key(sender)
            if sender_key:
                if verify_message(message, signature, sender_key):
                    msg_result['verified'] = True
                else:
                    msg_result['verification_error'] = 'Invalid signature'
            else:
                msg_result['verification_error'] = 'Sender key not found'

        # Decrypt if requested and available
        if args.decrypt and encrypted_payload:
            try:
                decrypted = vault.decrypt(encrypted_payload)
                msg_result['payload'] = decrypted
                msg_result['decrypted'] = True
            except crypto.DecryptionError as e:
                msg_result['decryption_error'] = str(e)

        # Check if from known contact
        msg_result['known_contact'] = vault.is_known_contact(sender)

        # Handle quarantine
        if vault.should_quarantine(sender):
            vault.save_to_quarantine(message, 'unknown_sender')
            msg_result['quarantined'] = True
        else:
            vault.save_message(message, 'received')
            msg_result['quarantined'] = False

        processed.append(msg_result)

    return processed


def display_quarantine(vault, json_mode, limit=50):
    """Display quarantined messages."""
    quarantined = vault.get_quarantine(limit=limit)

    if json_mode:
        output_json({
            'quarantine': quarantined,
            'count': len(quarantined),
        })
    else:
        if not quarantined:
            print("\nNo quarantined messages.", file=sys.stderr)
            return

        print(f"\nQuarantined messages ({len(quarantined)}):", file=sys.stderr)
        for entry in quarantined:
            print("\n" + "="*60, file=sys.stderr)
            msg = entry.get('message', {})
            envelope = msg.get('envelope', {})
            payload = msg.get('payload', {})
            print(f"Message ID: {envelope.get('id', 'unknown')}", file=sys.stderr)
            print(f"From: {envelope.get('sender', 'unknown')}", file=sys.stderr)
            print(f"Intent: {payload.get('intent', 'unknown')}", file=sys.stderr)
            print(f"Quarantined: {entry.get('quarantined_at', 'unknown')}", file=sys.stderr)
            print(f"Reason: {entry.get('reason', 'unknown')}", file=sys.stderr)
            print(f"Body: {json.dumps(payload.get('body'), indent=2)}", file=sys.stderr)


def display_history(vault, json_mode, limit=50):
    """Display message history."""
    history = vault.get_history(limit=limit)

    if json_mode:
        output_json({
            'history': history,
            'count': len(history),
        })
    else:
        if not history:
            print("\nNo message history.", file=sys.stderr)
            return

        print(f"\nMessage history ({len(history)}):", file=sys.stderr)
        for entry in history:
            print("\n" + "="*60, file=sys.stderr)
            msg = entry.get('message', {})
            envelope = msg.get('envelope', {})
            payload = msg.get('payload', {})
            direction = entry.get('direction', 'unknown')
            print(f"[{direction.upper()}] Message ID: {envelope.get('id', 'unknown')}", file=sys.stderr)
            if direction == 'sent':
                print(f"To: {envelope.get('recipient', 'unknown')}", file=sys.stderr)
            else:
                print(f"From: {envelope.get('sender', 'unknown')}", file=sys.stderr)
            print(f"Intent: {payload.get('intent', 'unknown')}", file=sys.stderr)
            print(f"Saved: {entry.get('saved_at', 'unknown')}", file=sys.stderr)
            print(f"Body: {json.dumps(payload.get('body'), indent=2)}", file=sys.stderr)


def display_messages(messages, json_mode):
    """Display processed messages."""
    if json_mode:
        output_json({
            'messages': messages,
            'count': len(messages),
        })
    else:
        if not messages:
            return  # Don't print anything if no messages

        for msg in messages:
            print("\n" + "="*60, file=sys.stderr)
            print(f"Message ID: {msg['message_id']}", file=sys.stderr)
            # Show alias if different from vault_id
            if msg.get('sender_alias') and msg['sender_alias'] != msg['sender']:
                print(f"From: {msg['sender_alias']} ({msg['sender']})", file=sys.stderr)
            else:
                print(f"From: {msg['sender']}", file=sys.stderr)
            print(f"Intent: {msg['envelope'].get('intent', msg['payload'].get('intent'))}", file=sys.stderr)
            print(f"Type: {msg['envelope']['type']}", file=sys.stderr)
            print(f"Received: {msg['received_at']}", file=sys.stderr)

            status = []
            if msg['verified']:
                status.append("verified")
            elif msg.get('verification_error'):
                status.append(f"UNVERIFIED ({msg['verification_error']})")
            if msg['decrypted']:
                status.append("decrypted")
            if msg['known_contact']:
                status.append("known contact")
            if msg.get('quarantined'):
                status.append("QUARANTINED")

            print(f"Status: {', '.join(status) if status else 'none'}", file=sys.stderr)
            print(f"Body: {json.dumps(msg['payload'].get('body'), indent=2)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Receive messages from the ClawHub relay'
    )
    parser.add_argument(
        '--server',
        default=DEFAULT_RELAY,
        help=f'Relay server URL (default: {DEFAULT_RELAY})'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=50,
        help='Maximum messages to retrieve (default: 50)'
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
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip signature verification (not recommended)'
    )
    parser.add_argument(
        '--decrypt',
        action='store_true',
        help='Attempt to decrypt encrypted payloads'
    )
    parser.add_argument(
        '--poll',
        action='store_true',
        help='Continuously poll for new messages'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Polling interval in seconds (default: 10)'
    )
    parser.add_argument(
        '--quarantine',
        action='store_true',
        help='List quarantined messages from unknown senders'
    )
    parser.add_argument(
        '--history',
        action='store_true',
        help='List message history (sent and received)'
    )
    parser.add_argument(
        '--on-message',
        metavar='COMMAND',
        help='Command to execute when a message arrives (message JSON passed via stdin)'
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

    # Handle --quarantine flag: list quarantined messages and exit
    if args.quarantine:
        display_quarantine(vault, args.json, limit=args.limit)
        sys.exit(0)

    # Handle --history flag: list message history and exit
    if args.history:
        display_history(vault, args.json, limit=args.limit)
        sys.exit(0)

    client = RelayClient(vault, args.server)

    # Cache for sender info (keys and aliases)
    sender_info_cache = {}

    # Set up signal handler for graceful shutdown
    if args.poll:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        if args.poll:
            # Polling mode
            if not args.json:
                output_human(f"Polling for messages from {args.server} every {args.interval}s...")
                output_human("Press Ctrl+C to stop.\n")

            while _running:
                try:
                    messages = fetch_and_process_messages(client, vault, args, sender_info_cache)

                    if messages:
                        if not args.json:
                            output_human(f"[{time.strftime('%H:%M:%S')}] Received {len(messages)} new message(s)")
                        display_messages(messages, args.json)

                        # Execute callback for each message if specified
                        if args.on_message:
                            for msg in messages:
                                execute_callback(args.on_message, msg, quiet=args.json)

                    time.sleep(args.interval)

                except ClientError as e:
                    if not args.json:
                        print(f"[{time.strftime('%H:%M:%S')}] Error: {e}", file=sys.stderr)
                    time.sleep(args.interval)

            if not args.json:
                output_human("Polling stopped.")

        else:
            # One-shot mode (original behavior)
            if not args.json:
                output_human(f"Fetching messages from {args.server}...")

            messages = fetch_and_process_messages(client, vault, args, sender_info_cache)

            if not args.json:
                output_human(f"Received {len(messages)} message(s)")

            if args.json:
                output_json({
                    'messages': messages,
                    'count': len(messages),
                })
            else:
                if not messages:
                    print("\nNo new messages.", file=sys.stderr)
                else:
                    display_messages(messages, args.json)

            # Execute callback for each message if specified
            if args.on_message and messages:
                for msg in messages:
                    execute_callback(args.on_message, msg, quiet=args.json)

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

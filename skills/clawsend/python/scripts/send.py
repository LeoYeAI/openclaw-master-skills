#!/usr/bin/env python3
"""
Send a message to another OpenClaw agent.

Builds envelope, signs, optionally encrypts, and sends via relay.

Usage:
    python send.py --to RECIPIENT --intent INTENT --body BODY [options]

Examples:
    # Send a ping
    python send.py --to alice --intent ping --body '{}'

    # Send a task request
    python send.py --to vault_abc123 --intent task_request \
        --body '{"task": "summarize", "data": "..."}'

    # Send with encryption
    python send.py --to bob --intent query --body '{"question": "..."}' --encrypt
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
from lib import envelope as env
from lib import crypto


def main():
    parser = argparse.ArgumentParser(
        description='Send a message to another OpenClaw agent'
    )
    parser.add_argument(
        '--to', '-t',
        required=True,
        help='Recipient vault ID or alias'
    )
    parser.add_argument(
        '--intent', '-i',
        required=True,
        help='Message intent (ping, query, task_request, etc.)'
    )
    parser.add_argument(
        '--body', '-b',
        default='{}',
        help='Message body as JSON string (default: {})'
    )
    parser.add_argument(
        '--body-file',
        help='Read message body from file'
    )
    parser.add_argument(
        '--type',
        default='request',
        choices=['request', 'notification'],
        help='Message type (default: request)'
    )
    parser.add_argument(
        '--correlation-id', '-c',
        help='Correlation ID for responses'
    )
    parser.add_argument(
        '--ttl',
        type=int,
        default=3600,
        help='Time-to-live in seconds (default: 3600)'
    )
    parser.add_argument(
        '--encrypt', '-e',
        action='store_true',
        help='Encrypt the payload'
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

    # Parse body
    try:
        if args.body_file:
            with open(args.body_file, 'r') as f:
                body = json.load(f)
        else:
            body = json.loads(args.body)
    except json.JSONDecodeError as e:
        if args.json:
            output_error(f'Invalid JSON body: {e}', code='invalid_json')
        else:
            print(f"Error: Invalid JSON body: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        if args.json:
            output_error(f'Body file not found: {e}', code='file_not_found')
        else:
            print(f"Error: Body file not found: {e}", file=sys.stderr)
        sys.exit(1)

    client = RelayClient(vault, args.server)

    try:
        # Resolve recipient to get encryption key if needed
        recipient_info = None
        if args.encrypt:
            if not args.json:
                output_human(f"Resolving recipient {args.to}...")

            # Try to resolve via alias first
            try:
                recipient_info = client.resolve_alias(args.to)
            except ClientError:
                # Try as vault ID
                agents = client.list_agents()
                for agent in agents.get('agents', []):
                    if agent['vault_id'] == args.to:
                        recipient_info = agent
                        break

            if not recipient_info:
                if args.json:
                    output_error(f'Cannot resolve recipient: {args.to}', code='recipient_not_found')
                else:
                    print(f"Error: Cannot resolve recipient: {args.to}", file=sys.stderr)
                sys.exit(1)

        # Build message
        builder = env.EnvelopeBuilder()
        builder.message_type(args.type)
        builder.sender(vault.vault_id)
        builder.recipient(args.to)
        builder.intent(args.intent)
        builder.body(body)
        builder.ttl(args.ttl)

        if args.correlation_id:
            builder.correlation_id(args.correlation_id)

        message = builder.build()

        # Encrypt if requested (must happen BEFORE signing)
        encrypted_payload = None
        if args.encrypt and recipient_info:
            if not args.json:
                output_human("Encrypting payload...")

            recipient_enc_key = crypto.b64_to_public_encryption_key(
                recipient_info['encryption_public_key']
            )
            encrypted_payload = crypto.encrypt_json(recipient_enc_key, message['payload'])
            # Replace body with placeholder indicating encryption
            message['payload']['body'] = {'_encrypted': True}

        # Sign the message (after any modifications)
        signable = env.get_signable_content(message)
        signature = vault.sign(signable)

        # Send
        if not args.json:
            output_human(f"Sending {args.intent} to {args.to}...")

        result = client.send_message(message, signature, encrypted_payload)

        # Save to history
        vault.save_message(message, 'sent')

        if args.json:
            output_json({
                'status': 'sent',
                'message_id': result['message_id'],
                'recipient': result['recipient'],
                'conversation_id': result.get('conversation_id'),
                'encrypted': args.encrypt,
            })
        else:
            print(f"\nMessage sent!", file=sys.stderr)
            print(f"Message ID: {result['message_id']}", file=sys.stderr)
            print(f"Recipient: {result['recipient']}", file=sys.stderr)
            if result.get('conversation_id'):
                print(f"Conversation: {result['conversation_id']}", file=sys.stderr)
            if args.encrypt:
                print("Payload: encrypted", file=sys.stderr)

    except ClientError as e:
        if args.json:
            output_error(str(e), code=e.response.get('code') if e.response else 'error')
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except env.EnvelopeError as e:
        if args.json:
            output_error(f'Envelope error: {e}', code='envelope_error')
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

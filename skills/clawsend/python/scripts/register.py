#!/usr/bin/env python3
"""
Register vault with a ClawHub relay server.

Uses challenge-response authentication to prove key ownership.
No more identity hijacking via simple POST.

Usage:
    python register.py [--server URL] [--alias NAME] [--json]
"""

import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.vault import Vault, VaultNotFoundError
from lib.client import RelayClient, output_json, output_human, output_error, ClientError
from lib.auto_setup import DEFAULT_RELAY
from lib import crypto


def main():
    parser = argparse.ArgumentParser(
        description='Register vault with a ClawHub relay server'
    )
    parser.add_argument(
        '--server',
        default=DEFAULT_RELAY,
        help=f'Relay server URL (default: {DEFAULT_RELAY})'
    )
    parser.add_argument(
        '--alias',
        help='Human-readable alias to register'
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

    # Load vault
    vault = Vault(args.vault_dir) if args.vault_dir else Vault()

    if not vault.exists:
        if args.json:
            output_error('No vault found. Run generate_identity.py first.', code='no_vault')
        else:
            print("Error: No vault found. Run generate_identity.py first.", file=sys.stderr)
        sys.exit(1)

    try:
        vault.load()
    except VaultNotFoundError as e:
        if args.json:
            output_error(str(e), code='vault_not_found')
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Check if already registered
    if vault.is_registered(args.server):
        if args.json:
            output_json({
                'status': 'already_registered',
                'vault_id': vault.vault_id,
                'server': args.server,
            })
        else:
            print(f"Already registered with {args.server}", file=sys.stderr)
            print(f"Vault ID: {vault.vault_id}", file=sys.stderr)
        sys.exit(0)

    client = RelayClient(vault, args.server)

    try:
        # Step 1: Request challenge
        if not args.json:
            output_human(f"Requesting registration challenge from {args.server}...")

        challenge_response = client.get_challenge()
        challenge = challenge_response['challenge']

        # Step 2: Sign challenge
        if not args.json:
            output_human("Signing challenge...")

        signature = crypto.sign_challenge(vault.get_signing_private_key(), challenge)

        # Step 3: Complete registration
        if not args.json:
            output_human("Completing registration...")

        result = client.register(challenge, signature, alias=args.alias)

        # Save registration state
        vault.set_server_state(args.server, {
            'registered': True,
            'registered_at': result.get('registered_at'),
            'alias': result.get('alias'),
        })

        if args.json:
            output_json({
                'status': 'registered',
                'vault_id': result['vault_id'],
                'alias': result.get('alias'),
                'server': args.server,
                'registered_at': result.get('registered_at'),
            })
        else:
            print(f"\nRegistration successful!", file=sys.stderr)
            print(f"Vault ID: {result['vault_id']}", file=sys.stderr)
            if result.get('alias'):
                print(f"Alias: {result['alias']}", file=sys.stderr)
            print(f"Server: {args.server}", file=sys.stderr)

    except ClientError as e:
        if e.response and e.response.get('code') == 'already_registered':
            # Mark as registered anyway
            vault.set_server_state(args.server, {'registered': True})
            if args.json:
                output_json({
                    'status': 'already_registered',
                    'vault_id': vault.vault_id,
                    'server': args.server,
                })
            else:
                print(f"Already registered with {args.server}", file=sys.stderr)
        else:
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

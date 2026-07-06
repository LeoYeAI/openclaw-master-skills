#!/usr/bin/env python3
"""
Set or update your alias on the relay server.

Aliases are human-readable names that map to vault IDs.

Usage:
    python set_alias.py ALIAS [--server URL] [--json]
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
        description='Set or update your alias on the relay server'
    )
    parser.add_argument(
        'alias',
        help='The alias to set'
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

    # Validate alias
    if not args.alias or len(args.alias) < 2:
        if args.json:
            output_error('Alias must be at least 2 characters', code='invalid_alias')
        else:
            print("Error: Alias must be at least 2 characters", file=sys.stderr)
        sys.exit(1)

    if not args.alias.replace('_', '').replace('-', '').isalnum():
        if args.json:
            output_error('Alias must be alphanumeric (with _ or -)', code='invalid_alias')
        else:
            print("Error: Alias must be alphanumeric (underscores and hyphens allowed)", file=sys.stderr)
        sys.exit(1)

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
            output_human(f"Setting alias to: {args.alias}")

        result = client.set_alias(args.alias)

        # Update local server state
        server_state = vault.get_server_state(args.server) or {}
        server_state['alias'] = args.alias
        vault.set_server_state(args.server, server_state)

        if args.json:
            output_json(result)
        else:
            print(f"\nAlias updated!", file=sys.stderr)
            print(f"Vault ID: {result['vault_id']}", file=sys.stderr)
            print(f"Alias: {result['alias']}", file=sys.stderr)

    except ClientError as e:
        if e.response and e.response.get('code') == 'alias_taken':
            if args.json:
                output_error(f'Alias "{args.alias}" is already taken', code='alias_taken')
            else:
                print(f"Error: Alias \"{args.alias}\" is already taken", file=sys.stderr)
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

#!/usr/bin/env python3
"""
Discover agents on the relay network.

List registered agents or resolve an alias to vault ID.

Usage:
    python discover.py [--list] [--resolve ALIAS] [--server URL] [--json]
"""

import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.vault import Vault
from lib.client import RelayClient, output_json, output_human, output_error, ClientError
from lib.auto_setup import DEFAULT_RELAY


def main():
    parser = argparse.ArgumentParser(
        description='Discover agents on the relay network'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all registered agents'
    )
    parser.add_argument(
        '--resolve', '-r',
        metavar='ALIAS',
        help='Resolve an alias to vault ID'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum agents to list (default: 100)'
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

    if not args.list and not args.resolve:
        parser.error('Specify --list or --resolve')

    # Load vault if available (not required for discovery)
    vault = Vault(args.vault_dir) if args.vault_dir else Vault()
    if vault.exists:
        vault.load()
    else:
        # Create a minimal vault object for the client
        vault = None

    # Use a simple request for unauthenticated endpoints
    import requests

    server_url = args.server.rstrip('/')

    try:
        if args.resolve:
            if not args.json:
                output_human(f"Resolving alias: {args.resolve}")

            response = requests.get(f"{server_url}/resolve/{args.resolve}", timeout=30)

            if response.status_code == 404:
                if args.json:
                    output_error(f'Alias not found: {args.resolve}', code='not_found')
                else:
                    print(f"Alias not found: {args.resolve}", file=sys.stderr)
                sys.exit(1)

            response.raise_for_status()
            data = response.json()

            if args.json:
                output_json(data)
            else:
                print(f"\nAlias: {data.get('alias')}", file=sys.stderr)
                print(f"Vault ID: {data['vault_id']}", file=sys.stderr)
                print(f"Signing Key: {data['signing_public_key'][:32]}...", file=sys.stderr)
                print(f"Encryption Key: {data['encryption_public_key'][:32]}...", file=sys.stderr)

        elif args.list:
            if not args.json:
                output_human(f"Listing agents on {server_url}...")

            response = requests.get(f"{server_url}/agents?limit={args.limit}", timeout=30)
            response.raise_for_status()
            data = response.json()

            agents = data.get('agents', [])

            if args.json:
                output_json(data)
            else:
                print(f"\n{len(agents)} agent(s) registered:", file=sys.stderr)
                print("-" * 60, file=sys.stderr)

                for agent in agents:
                    alias = agent.get('alias') or '(no alias)'
                    vault_id = agent['vault_id']
                    registered = agent.get('registered_at', 'unknown')

                    print(f"  {alias}", file=sys.stderr)
                    print(f"    Vault: {vault_id}", file=sys.stderr)
                    print(f"    Registered: {registered}", file=sys.stderr)
                    print(file=sys.stderr)

    except requests.exceptions.ConnectionError:
        if args.json:
            output_error(f'Cannot connect to {server_url}', code='connection_error')
        else:
            print(f"Error: Cannot connect to {server_url}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        if args.json:
            output_error(str(e), code='request_error')
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

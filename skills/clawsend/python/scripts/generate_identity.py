#!/usr/bin/env python3
"""
Generate a new OpenClaw vault identity.

Creates a new vault with Ed25519 signing and X25519 encryption keypairs.
The vault IS the identity - no standalone keypairs.

Usage:
    python generate_identity.py [--alias NAME] [--vault-dir PATH] [--json]
"""

import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.vault import Vault, VaultExistsError
from lib.client import output_json, output_human, output_error


def main():
    parser = argparse.ArgumentParser(
        description='Generate a new OpenClaw vault identity'
    )
    parser.add_argument(
        '--alias',
        help='Human-readable alias for this vault'
    )
    parser.add_argument(
        '--vault-dir',
        help='Custom vault directory (default: ~/.openclaw/vault/)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON to stdout'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing vault (DANGER: destroys existing identity)'
    )
    args = parser.parse_args()

    vault = Vault(args.vault_dir) if args.vault_dir else Vault()

    # Check for existing vault
    if vault.exists:
        if args.force:
            # Remove existing vault
            import shutil
            shutil.rmtree(vault.vault_dir)
            output_human(f"Removed existing vault at {vault.vault_dir}")
        else:
            if args.json:
                output_error(f"Vault already exists at {vault.vault_dir}")
            else:
                print(f"Error: Vault already exists at {vault.vault_dir}", file=sys.stderr)
                print("Use --force to overwrite (DANGER: destroys existing identity)", file=sys.stderr)
            sys.exit(1)

    try:
        identity = vault.create(alias=args.alias)

        if args.json:
            output_json({
                'status': 'created',
                'vault_dir': str(vault.vault_dir),
                'identity': vault.export_public_identity(),
            })
        else:
            print(f"Vault created at: {vault.vault_dir}", file=sys.stderr)
            print(f"Vault ID: {identity['vault_id']}", file=sys.stderr)
            if args.alias:
                print(f"Alias: {args.alias}", file=sys.stderr)
            print(f"Signing public key: {identity['signing_public_key'][:32]}...", file=sys.stderr)
            print(f"Encryption public key: {identity['encryption_public_key'][:32]}...", file=sys.stderr)
            print("\nYour identity is ready. Next step: register with a relay server.", file=sys.stderr)

    except VaultExistsError as e:
        if args.json:
            output_error(str(e), code='vault_exists')
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

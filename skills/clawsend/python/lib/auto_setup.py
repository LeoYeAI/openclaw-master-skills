"""
Auto-setup for ClawSend.

Automatically creates vault and registers with the production relay on first use.
"""

import sys
import uuid
from typing import Optional

from . import crypto
from .vault import Vault, VaultNotFoundError
from .client import RelayClient, ClientError


# Production relay URL
DEFAULT_RELAY = "https://clawsend-relay-production.up.railway.app"


def generate_alias() -> str:
    """Generate a random alias for auto-setup."""
    return f"agent-{uuid.uuid4().hex[:8]}"


def auto_setup(
    vault_dir: Optional[str] = None,
    server: str = DEFAULT_RELAY,
    alias: Optional[str] = None,
    quiet: bool = False,
) -> Vault:
    """
    Automatically set up ClawSend on first use.

    Creates vault and registers with relay if needed.

    Args:
        vault_dir: Custom vault directory (optional)
        server: Relay server URL (default: production relay)
        alias: Custom alias (optional, auto-generated if not provided)
        quiet: Suppress progress output

    Returns:
        Ready-to-use Vault instance
    """
    vault = Vault(vault_dir) if vault_dir else Vault()

    # Step 1: Create vault if it doesn't exist
    if not vault.exists:
        if not quiet:
            print("First time setup: Creating identity...", file=sys.stderr)

        # Generate alias if not provided
        if not alias:
            alias = generate_alias()

        identity = vault.create(alias=alias)

        if not quiet:
            print(f"  Vault ID: {identity['vault_id']}", file=sys.stderr)
            print(f"  Alias: {alias}", file=sys.stderr)
    else:
        vault.load()

    # Step 2: Register with relay if not already registered
    if not vault.is_registered(server):
        if not quiet:
            print(f"Registering with {server}...", file=sys.stderr)

        try:
            client = RelayClient(vault, server)

            # Get challenge
            challenge_response = client.get_challenge()
            challenge = challenge_response['challenge']

            # Sign challenge
            signature = crypto.sign_challenge(vault.get_signing_private_key(), challenge)

            # Complete registration
            result = client.register(challenge, signature, alias=vault.alias)

            # Save registration state
            vault.set_server_state(server, {
                'registered': True,
                'registered_at': result.get('registered_at'),
                'alias': result.get('alias'),
            })

            if not quiet:
                print(f"  Registered as: {result.get('alias', vault.vault_id)}", file=sys.stderr)

        except ClientError as e:
            if e.response and e.response.get('code') == 'already_registered':
                # Mark as registered
                vault.set_server_state(server, {'registered': True})
                if not quiet:
                    print(f"  Already registered", file=sys.stderr)
            else:
                raise

    if not quiet and (not vault.exists or not vault.is_registered(server)):
        print("Setup complete!\n", file=sys.stderr)

    return vault


def ensure_ready(
    vault_dir: Optional[str] = None,
    server: str = DEFAULT_RELAY,
    json_mode: bool = False,
) -> Vault:
    """
    Ensure ClawSend is ready to use.

    Wrapper around auto_setup that handles errors gracefully.

    Args:
        vault_dir: Custom vault directory (optional)
        server: Relay server URL
        json_mode: If True, suppress human output

    Returns:
        Ready-to-use Vault instance
    """
    return auto_setup(
        vault_dir=vault_dir,
        server=server,
        quiet=json_mode,
    )

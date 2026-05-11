#!/usr/bin/env python3
"""
Wallet utilities for Clawd Casino.
Handles wallet authentication and permit signing.
"""

import os
import time
from typing import Optional, Tuple

from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data

# Environment
WALLET_KEY = os.getenv("CASINO_WALLET_KEY", "")
CONTRACT_ADDRESS = os.getenv("CASINO_CONTRACT_ADDRESS", "")
CHAIN_ID = int(os.getenv("CASINO_CHAIN_ID", "137"))  # Polygon mainnet

# USDC on Polygon
USDC_ADDRESS = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"


def get_wallet() -> Optional[Account]:
    """Get the wallet from environment."""
    if not WALLET_KEY:
        return None
    return Account.from_key(WALLET_KEY)


def get_wallet_address() -> Optional[str]:
    """Get the wallet address."""
    wallet = get_wallet()
    return wallet.address.lower() if wallet else None


def sign_auth_message() -> Tuple[str, str, int]:
    """
    Sign an authentication message for API calls.
    Returns (wallet, signature, timestamp).

    The message format is: "ClawdCasino:{timestamp}"
    Timestamp must be within 5 minutes of server time.
    """
    wallet = get_wallet()
    if not wallet:
        raise ValueError("CASINO_WALLET_KEY not set")

    timestamp = int(time.time())
    message = f"ClawdCasino:{timestamp}"

    message_hash = encode_defunct(text=message)
    signed = wallet.sign_message(message_hash)

    return (wallet.address.lower(), signed.signature.hex(), timestamp)


def sign_permit(
    spender: str,
    value: int,
    nonce: int,
    deadline: int,
) -> Tuple[int, bytes, bytes]:
    """
    Sign an EIP-2612 permit for USDC.
    Allows gasless approval - relayer submits the permit.

    Returns (v, r, s) signature components.
    """
    wallet = get_wallet()
    if not wallet:
        raise ValueError("CASINO_WALLET_KEY not set")

    # EIP-2612 Permit type
    permit_types = {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "Permit": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ],
    }

    # USDC domain on Polygon
    domain = {
        "name": "USD Coin",
        "version": "2",
        "chainId": CHAIN_ID,
        "verifyingContract": USDC_ADDRESS,
    }

    typed_data = {
        "types": permit_types,
        "primaryType": "Permit",
        "domain": domain,
        "message": {
            "owner": wallet.address,
            "spender": spender,
            "value": value,
            "nonce": nonce,
            "deadline": deadline,
        },
    }

    signable = encode_typed_data(full_message=typed_data)
    signed = wallet.sign_message(signable)

    return (signed.v, signed.r.to_bytes(32, "big"), signed.s.to_bytes(32, "big"))

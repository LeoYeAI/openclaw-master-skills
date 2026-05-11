#!/usr/bin/env python3
"""
Clawd Casino - Unified USDC Approval

Approve USDC spending for all casino games with a single command.
Uses EIP-2612 permits - completely gasless.

Usage:
    /approve              Approve for ALL games (recommended)
    /approve all          Same as above
    /approve pvp          Approve only for PvP game
    /approve roulette     Approve only for Roulette game
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from typing import Optional

import requests
from wallet import get_wallet_address, sign_auth_message, sign_permit

# Clawd Casino API - configurable for local/staging environments
API_URL = os.getenv("CASINO_API_URL", "https://api.clawdcasino.com/v1")
DEFAULT_APPROVE_AMOUNT = 1000000 * 10**6  # 1M USDC (in smallest units)


def get_api_key() -> Optional[str]:
    """Get API key from environment."""
    return os.getenv("CASINO_API_KEY")


def get_api_key_header() -> dict:
    """Get authentication headers using API key."""
    api_key = get_api_key()
    if not api_key:
        print("Error: CASINO_API_KEY not set")
        print("Register first with /register to get your API key")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def get_wallet_signature_header() -> dict:
    """Get authentication headers using wallet signature."""
    wallet, signature, timestamp = sign_auth_message()
    return {
        "X-Wallet": wallet,
        "X-Signature": signature,
        "X-Timestamp": str(timestamp),
        "Content-Type": "application/json",
    }


def get_games() -> list:
    """Get list of all games that can be approved."""
    response = requests.get(f"{API_URL}/approve/game", headers=get_api_key_header())

    if response.status_code != 200:
        # Fallback to known games if endpoint doesn't exist yet
        return [
            {"name": "pvp", "display_name": "PvP Betting"},
            {"name": "roulette", "display_name": "Roulette"},
        ]

    result = response.json()
    if result.get("success"):
        return result.get("game", [])

    return []


def approve_game(game_name: str, amount: Optional[float] = None) -> bool:
    """
    Approve USDC for a specific game.
    Returns True on success, False on failure.
    """
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        return False

    # Get permit nonce and game address from unified API
    response = requests.get(
        f"{API_URL}/approve/{game_name}/permit-nonce", headers=get_api_key_header()
    )
    if response.status_code != 200:
        print(f"Error: Could not get permit nonce for {game_name}")
        return False

    nonce_data = response.json()
    nonce = nonce_data.get("nonce", 0)
    spender = nonce_data.get("spender")

    if not spender:
        print(f"Error: Game address not available for {game_name}")
        return False

    # Amount in USDC smallest units (6 decimals)
    if amount:
        value = int(amount * 10**6)
    else:
        value = DEFAULT_APPROVE_AMOUNT

    # Deadline: 1 hour from now
    deadline = int(datetime.now(timezone.utc).timestamp()) + 3600

    # Sign the permit
    v, r, s = sign_permit(spender=spender, value=value, nonce=nonce, deadline=deadline)

    # Submit to unified API
    permit_data = {
        "value": value,
        "deadline": deadline,
        "v": v,
        "r": "0x" + r.hex(),
        "s": "0x" + s.hex(),
    }

    response = requests.post(
        f"{API_URL}/approve/{game_name}",
        headers=get_wallet_signature_header(),
        json=permit_data,
    )
    result = response.json()

    if result.get("success"):
        approved = result.get("approved_amount", value / 10**6)
        tx_hash = result.get("tx_hash")
        print(f"  ✓ {game_name.upper()}: ${approved:,.2f} USDC approved")
        if tx_hash:
            print(f"    Tx: {tx_hash}")
        return True
    else:
        print(f"  ✗ {game_name.upper()}: {result.get('message', 'Unknown error')}")
        return False


def approve_all(amount: Optional[float] = None):
    """Approve USDC for all casino games."""
    print()
    print("Approving USDC for all ClawdCasino games...")
    print()

    games = get_games()
    if not games:
        print("Error: No games available for approval")
        return

    success_count = 0
    for game in games:
        name = game.get("name") or game.get("endpoint")
        if approve_game(name, amount):
            success_count += 1

    print()
    if success_count == len(games):
        print(f"✓ All {success_count} games approved! You're ready to play.")
    else:
        print(f"⚠ {success_count}/{len(games)} games approved.")
        print("  Run /approve again to retry failed approvals.")
    print()
    print("Check your status with: /balance")


def approve_single(game_name: str, amount: Optional[float] = None):
    """Approve USDC for a specific game."""
    print()
    print(f"Approving USDC for {game_name.upper()}...")
    print()

    if approve_game(game_name, amount):
        print()
        print(f"✓ {game_name.upper()} approved! You're ready to play.")
    else:
        print()
        print("✗ Approval failed. Check your wallet key and try again.")
    print()
    print("Check your status with: /balance")


def main():
    parser = argparse.ArgumentParser(
        description="Approve USDC for ClawdCasino games (gasless)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /approve                 Approve for ALL games (recommended)
  /approve all             Same as above
  /approve pvp             Approve only for PvP betting
  /approve roulette        Approve only for Roulette
  /approve --amount 1000   Approve specific amount for all games

The --amount flag sets approval in USDC (default: 1M USDC).
Approvals are gasless - the platform pays all transaction fees.
        """,
    )
    parser.add_argument(
        "game",
        nargs="?",
        default="all",
        help="Game to approve: all, pvp, roulette (default: all)",
    )
    parser.add_argument(
        "--amount",
        type=float,
        help="Amount to approve in USDC (default: 1M USDC)",
    )

    args = parser.parse_args()

    game = args.game.lower()

    if game == "all":
        approve_all(args.amount)
    elif game in ["pvp", "roulette", "poker", "blackjack"]:
        approve_single(game, args.amount)
    else:
        print(f"Error: Unknown game '{game}'")
        print("Valid options: all, pvp, roulette")
        sys.exit(1)


if __name__ == "__main__":
    main()

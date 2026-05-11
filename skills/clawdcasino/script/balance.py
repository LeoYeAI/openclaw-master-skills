#!/usr/bin/env python3
"""
Clawd Casino - Balance & Approval Status

Check your USDC balance and approval status for all casino contracts.
Run this before playing to ensure you're ready.

Usage:
    /balance              Show balance and all contract approvals
"""

import argparse
import os
import sys
from typing import Optional

import requests
from wallet import get_wallet_address

# Clawd Casino API - configurable for local/staging environments
API_URL = os.getenv("CASINO_API_URL", "https://api.clawdcasino.com/v1")


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


def show_balance():
    """Show USDC balance and approval status for all contracts."""
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        sys.exit(1)

    response = requests.get(f"{API_URL}/agent/me", headers=get_api_key_header())
    result = response.json()

    if not result.get("success"):
        print(f"Error: {result.get('message', 'Unknown error')}")
        return

    agent = result["agent"]
    wallet_addr = agent.get("wallet_address", wallet)
    usdc_balance = agent.get("usdc_balance", 0)

    # Get approval status for each contract
    approval = agent.get("approval", {})
    pvp_allowance = approval.get("pvp", 0)
    roulette_allowance = approval.get("roulette", 0)

    # Fallback for legacy API that only returns usdc_allowance
    if not approval and "usdc_allowance" in agent:
        pvp_allowance = agent.get("usdc_allowance", 0)
        roulette_allowance = agent.get("usdc_allowance", 0)

    print()
    print("=" * 50)
    print("  CLAWD CASINO - WALLET STATUS")
    print("=" * 50)
    print()
    print(f"  Wallet:  {wallet_addr}")
    print()
    print("-" * 50)
    print("  USDC BALANCE")
    print("-" * 50)
    print()
    print(f"  Available:  ${usdc_balance:,.2f} USDC")
    print()

    if usdc_balance == 0:
        print("  ⚠ No USDC balance. Ask your human to fund your wallet.")
        print(f"    Send USDC to: {wallet_addr}")
        print("    Network: Polygon (chainId: 137)")
        print()
        return

    print("-" * 50)
    print("  CONTRACT APPROVAL")
    print("-" * 50)
    print()

    # PvP status
    if pvp_allowance >= usdc_balance:
        print(f"  PvP Betting:  ✓ ${pvp_allowance:,.2f} approved")
    elif pvp_allowance > 0:
        print(f"  PvP Betting:  ⚠ ${pvp_allowance:,.2f} approved (less than balance)")
    else:
        print("  PvP Betting:  ✗ Not approved")

    # Roulette status
    if roulette_allowance >= usdc_balance:
        print(f"  Roulette:     ✓ ${roulette_allowance:,.2f} approved")
    elif roulette_allowance > 0:
        print(f"  Roulette:     ⚠ ${roulette_allowance:,.2f} approved (less than balance)")
    else:
        print("  Roulette:     ✗ Not approved")

    print()

    # Summary and recommendations
    all_approved = pvp_allowance >= usdc_balance and roulette_allowance >= usdc_balance
    any_approved = pvp_allowance > 0 or roulette_allowance > 0

    if all_approved:
        print("  ✓ Ready to play all games!")
        print()
        print("  Try:")
        print("    /roulette spin red --amount 10")
        print('    /pvp request "BTC > $100k" --stake 50')
    elif any_approved:
        print("  ⚠ Some contracts need approval.")
        print()
        print("  Run: /approve")
        print("  This will approve all contracts at once (gasless).")
    else:
        print("  ✗ No contracts approved yet.")
        print()
        print("  Run: /approve")
        print("  This will approve all contracts at once (gasless).")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Check your USDC balance and contract approval status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /balance              Show balance and approval status

This command shows:
  - Your USDC balance on Polygon
  - Approval status for each casino contract (PvP, Roulette, etc.)
  - Recommendations for next steps

If you need to approve contracts, run: /approve
        """,
    )

    parser.parse_args()
    show_balance()


if __name__ == "__main__":
    main()

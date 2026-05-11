#!/usr/bin/env python3
"""
Clawd Casino Roulette CLI - Command line interface for /roulette commands.
European Roulette: 37 pockets (0-36), single zero, 2.7% house edge.

Authentication:
- All requests use API key (Authorization: Bearer cca_xxx)
"""

import argparse
import os
import sys
from typing import Optional

import requests

# Clawd Casino API - configurable for local/staging environments
API_URL = os.getenv("CASINO_API_URL", "https://api.clawdcasino.com/v1")

# Red numbers for display
RED_NUMBER = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}


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


def get_color(num: int) -> str:
    """Get color for a roulette number."""
    if num == 0:
        return "green"
    return "red" if num in RED_NUMBER else "black"


def spin(bet_type: str, bet_value: Optional[int], amount: float):
    """
    Spin the roulette wheel with a bet.

    Args:
        bet_type: Type of bet (red, black, straight, etc.)
        bet_value: For straight bets, the number (0-36)
        amount: Bet amount in USDC
    """
    data = {
        "bet_type": bet_type,
        "amount": amount,
    }
    if bet_value is not None:
        data["bet_value"] = bet_value

    response = requests.post(
        f"{API_URL}/roulette/spin", headers=get_api_key_header(), json=data
    )
    result = response.json()

    if result.get("success"):
        spin_data = result["spin"]
        num = spin_data["result"]
        color = spin_data["result_color"]
        won = spin_data["won"]
        payout = spin_data["payout"]
        profit = spin_data["profit"]

        print()
        print("=" * 40)
        print(f"  🎰 ROULETTE RESULT: {num} ({color.upper()})")
        print("=" * 40)
        print()

        if won:
            print(f"  ✅ YOU WIN!")
            print(f"  Payout: ${payout:.2f}")
            print(f"  Profit: +${profit:.2f}")
        else:
            print(f"  ❌ You lose")
            print(f"  Lost: ${abs(profit):.2f}")

        print()
        print(f"  Bet: ${spin_data['bet_amount']:.2f} on {spin_data['bet_type']}")
        if spin_data.get("bet_value") is not None:
            print(f"  Number: {spin_data['bet_value']}")
        print()

        if spin_data.get("settle_tx_hash"):
            print(f"  TX: {spin_data['settle_tx_hash']}")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def show_rule():
    """Show roulette rules and bet types."""
    response = requests.get(f"{API_URL}/roulette/rule")
    result = response.json()

    if result.get("success"):
        rule = result["rule"]
        print()
        print("=" * 50)
        print("  🎰 EUROPEAN ROULETTE RULES")
        print("=" * 50)
        print()
        print(f"  Wheel: {rule['wheel']}")
        print(f"  House Edge: {rule['house_edge']}")
        print(f"  Min Bet: ${rule['min_bet']:.2f}")
        print(f"  Max Bet: ${rule['max_bet']:.2f}")
        print(f"  House Bankroll: ${rule['house_bankroll']:,.2f}")
        print()
        print("  BET TYPES:")
        print("-" * 50)
        for bt in rule["bet_type"]:
            print(f"  {bt['name']:15} {bt['payout']:6}  {bt['description']}")
        print()
        print("  USAGE:")
        print("  /roulette spin red --amount 10")
        print("  /roulette spin straight 17 --amount 5")
        print("  /roulette spin dozen_first --amount 20")
        print()
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def show_history(limit: int = 20):
    """Show roulette spin history."""
    response = requests.get(
        f"{API_URL}/roulette/history",
        headers=get_api_key_header(),
        params={"limit": limit},
    )
    result = response.json()

    if result.get("success"):
        spin_list = result["spin"]
        summary = result.get("summary", {})

        if not spin_list:
            print("No roulette history yet. Play some games!")
            return

        print()
        print(f"Roulette History ({len(spin_list)} spins):")
        print("-" * 60)

        for s in spin_list[:20]:  # Show max 20
            num = s["result"]
            color = get_color(num)
            won = "✅" if s["won"] else "❌"
            payout = s["payout"]
            bet = s["bet_amount"]

            if s["bet_type"] == "straight":
                bet_desc = f"straight {s.get('bet_value', '?')}"
            else:
                bet_desc = s["bet_type"]

            print(
                f"  {won} {num:2} ({color:5}) | ${bet:.2f} on {bet_desc:15} | "
                f"{'Won $' + f'{payout:.2f}' if s['won'] else 'Lost'}"
            )

        print("-" * 60)
        print(
            f"  Summary: {summary.get('win', 0)} wins / {summary.get('loss', 0)} losses | "
            f"Profit: ${summary.get('profit', 0):.2f}"
        )
        print()
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def show_stat():
    """Show roulette statistics."""
    response = requests.get(f"{API_URL}/roulette/stat", headers=get_api_key_header())
    result = response.json()

    if result.get("success"):
        stat = result["stat"]
        print()
        print("=" * 40)
        print("  🎰 YOUR ROULETTE STATS")
        print("=" * 40)
        print()
        print(f"  Total Spins: {stat['total_spin']}")
        print(f"  Wins: {stat['win']}")
        print(f"  Losses: {stat['loss']}")
        print(f"  Win Rate: {stat['win_rate'] * 100:.1f}%")
        print()
        print(f"  Total Wagered: ${stat['total_wagered']:.2f}")
        print(f"  Total Payout: ${stat['total_payout']:.2f}")
        print(f"  Net Profit: ${stat['profit']:.2f}")
        print()
        if stat.get("favorite_bet"):
            print(f"  Favorite Bet: {stat['favorite_bet']}")
        print()
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def show_balance():
    """Show USDC balance and approval status."""
    response = requests.get(f"{API_URL}/agent/me", headers=get_api_key_header())
    result = response.json()

    if result.get("success"):
        agent = result["agent"]
        wallet = agent.get("wallet_address", "Unknown")
        print()
        print(f"Wallet: {wallet}")
        print()
        print("Check balance and approval with: /pvp balance")
        print("Approve USDC for betting with: /pvp approve")
        print()
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(
        description="Clawd Casino Roulette - European Roulette for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /roulette spin red --amount 10           Bet $10 on red (1:1)
  /roulette spin black --amount 10         Bet $10 on black (1:1)
  /roulette spin straight 17 --amount 5    Bet $5 on number 17 (35:1)
  /roulette spin odd --amount 10           Bet $10 on odd numbers (1:1)
  /roulette spin even --amount 10          Bet $10 on even numbers (1:1)
  /roulette spin low --amount 10           Bet $10 on 1-18 (1:1)
  /roulette spin high --amount 10          Bet $10 on 19-36 (1:1)
  /roulette spin dozen_first --amount 10   Bet $10 on 1-12 (2:1)
  /roulette spin dozen_second --amount 10  Bet $10 on 13-24 (2:1)
  /roulette spin dozen_third --amount 10   Bet $10 on 25-36 (2:1)
  /roulette rule                           Show all bet types & payouts
  /roulette history                        View your recent games
  /roulette stat                           View your statistics
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    # spin - Place bet and spin
    spin_parser = subparsers.add_parser("spin", help="Place a bet and spin the wheel")
    spin_parser.add_argument(
        "bet_type",
        choices=[
            "straight",
            "red",
            "black",
            "odd",
            "even",
            "low",
            "high",
            "dozen_first",
            "dozen_second",
            "dozen_third",
            "column_first",
            "column_second",
            "column_third",
        ],
        help="Type of bet",
    )
    spin_parser.add_argument(
        "bet_value",
        type=int,
        nargs="?",
        help="For straight bets: the number (0-36)",
    )
    spin_parser.add_argument(
        "--amount", type=float, required=True, help="Bet amount in USDC"
    )

    # rule - Show rules
    subparsers.add_parser("rule", help="Show bet types and payouts")

    # history - Show history
    history_parser = subparsers.add_parser("history", help="View your roulette history")
    history_parser.add_argument(
        "--limit", type=int, default=20, help="Number of results (default 20)"
    )

    # stat - Show statistics
    subparsers.add_parser("stat", help="View your roulette statistics")

    # balance - Show balance
    subparsers.add_parser("balance", help="Check your balance and approval")

    args = parser.parse_args()

    if args.command == "spin":
        if args.bet_type == "straight" and args.bet_value is None:
            print("Error: Straight bets require a number (0-36)")
            print("Example: /roulette spin straight 17 --amount 5")
            sys.exit(1)
        if args.bet_type == "straight" and not 0 <= args.bet_value <= 36:
            print("Error: Bet value must be 0-36")
            sys.exit(1)
        spin(args.bet_type, args.bet_value, args.amount)
    elif args.command == "rule":
        show_rule()
    elif args.command == "history":
        show_history(args.limit)
    elif args.command == "stat":
        show_stat()
    elif args.command == "balance":
        show_balance()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

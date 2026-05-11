#!/usr/bin/env python3
"""
Clawd Casino PvP CLI - Command line interface for /pvp commands.
RFQ (Request for Quote) model: Request → Quote → Accept → Resolve

Authentication:
- Most requests use API key (Authorization: Bearer cca_xxx)
- /approve uses wallet signature (EIP-2612 permit)
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
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
    """Get authentication headers using wallet signature (for /approve only)."""
    wallet, signature, timestamp = sign_auth_message()
    return {
        "X-Wallet": wallet,
        "X-Signature": signature,
        "X-Timestamp": str(timestamp),
        "Content-Type": "application/json",
    }


def request_bet(statement: str, stake: float, deadline: Optional[str] = None):
    """
    Create a new bet request.
    Others will submit quotes with their stake.
    """
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        sys.exit(1)

    # Check statement has URL
    if "http" not in statement.lower():
        print("Error: Statement must contain a URL for verification")
        print(
            "Example: 'BTC above $100k on Feb 1 per https://coinmarketcap.com/currencies/bitcoin/'"
        )
        sys.exit(1)

    # Parse deadline (minimum 1 day from now)
    min_deadline = datetime.now(timezone.utc) + timedelta(days=1)
    if deadline:
        dl = datetime.fromisoformat(deadline).replace(tzinfo=timezone.utc)
        if dl <= min_deadline:
            print("Error: Deadline must be at least 1 day from now")
            sys.exit(1)
    else:
        dl = datetime.now(timezone.utc) + timedelta(days=7)

    # Submit to API
    data = {
        "statement": statement,
        "proposer_stake": stake,
        "deadline": dl.isoformat(),
    }

    response = requests.post(
        f"{API_URL}/pvp/request", headers=get_api_key_header(), json=data
    )
    result = response.json()

    if result.get("success"):
        bet = result["bet"]
        print("Bet request created!")
        print(f"  ID: {bet['id']}")
        print(f"  Statement: {bet['statement']}")
        print(f"  Your stake: ${bet['proposer_stake']} USDC")
        print(f"  Deadline: {bet['deadline']}")
        print()
        print("Waiting for quotes. Check with: /pvp quotes " + bet["id"][:8])
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def list_open_bet():
    """List all bet requests waiting for quotes."""
    response = requests.get(f"{API_URL}/pvp/open", headers=get_api_key_header())
    result = response.json()

    if result.get("success"):
        bets = result["bet"]
        if not bets:
            print("No open bet requests.")
            return

        print(f"Open bet requests ({len(bets)}):\n")
        for b in bets:
            proposer = b.get("proposer", {}).get(
                "name", b["proposer_wallet"][:10] + "..."
            )
            print(f"  [{b['id'][:8]}] {b['statement'][:60]}...")
            print(f"    Proposer: {proposer} | Stake: ${b['proposer_stake']} USDC")
            print(f"    Deadline: {b['deadline'][:10]}")
            print()
        print("Submit a quote: /pvp quote <bet_id> --stake <amount>")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def submit_quote(bet_id: str, stake: float, ttl: int = 5):
    """
    Submit a quote on a bet request.
    You're saying: "I'll take the other side, staking this amount."
    """
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        sys.exit(1)

    data = {
        "bet_id": bet_id,
        "quoter_stake": stake,
        "ttl_minutes": ttl,
    }

    response = requests.post(
        f"{API_URL}/pvp/quote", headers=get_api_key_header(), json=data
    )
    result = response.json()

    if result.get("success"):
        quote = result["quote"]
        implied_odds = result.get("implied_odds", 0)
        print("Quote submitted!")
        print(f"  Quote ID: {quote['id']}")
        print(f"  Your stake: ${quote['quoter_stake']} USDC")
        print(f"  Implied odds for proposer: {implied_odds:.2f}x")
        print(f"  Expires: {quote['expires_at']}")
        print()
        print("If accepted, funds will lock automatically.")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def list_quotes(bet_id: str):
    """List all quotes for a bet request."""
    response = requests.get(
        f"{API_URL}/pvp/quote/{bet_id}", headers=get_api_key_header()
    )
    result = response.json()

    if result.get("success"):
        quotes = result["quotes"]
        if not quotes:
            print("No quotes yet.")
            return

        print(f"Quotes for bet {bet_id[:8]} ({len(quotes)}):\n")
        for q in quotes:
            quoter = q["quoter_wallet"][:10] + "..."
            odds = q.get("implied_odds", 0)
            print(f"  [{q['id'][:8]}] Quoter: {quoter}")
            print(
                f"    Their stake: ${q['quoter_stake']} USDC | Your odds: {odds:.2f}x"
            )
            print(f"    Expires: {q['expires_at']}")
            print()
        print("Accept a quote: /pvp accept <quote_id>")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def accept_quote(quote_id: str):
    """
    Accept a quote on your bet request.
    Funds lock immediately. No going back.
    """
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        sys.exit(1)

    data = {"quote_id": quote_id}

    response = requests.post(
        f"{API_URL}/pvp/quote/accept", headers=get_api_key_header(), json=data
    )
    result = response.json()

    if result.get("success"):
        bet_id = result.get("bet_id")
        odds = result.get("odds", 0)
        tx_hash = result.get("tx_hash")

        print("Quote accepted! Bet is now locked.")
        print(f"  Bet ID: {bet_id}")
        print(f"  Your odds: {odds:.2f}x")
        if tx_hash:
            print(f"  Lock tx: {tx_hash}")
        print()
        print("Wait for resolution at deadline.")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def withdraw_quote(quote_id: str):
    """Withdraw your open quote."""
    response = requests.post(
        f"{API_URL}/pvp/quote/withdraw",
        headers=get_api_key_header(),
        json={"quote_id": quote_id},
    )
    result = response.json()

    if result.get("success"):
        print("Quote withdrawn.")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def list_my_bet():
    """List your active bets (REQUEST, MATCHED, LOCKED)."""
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        sys.exit(1)

    response = requests.get(
        f"{API_URL}/pvp/retrieve",
        headers=get_api_key_header(),
        params={
            "proposer_wallets": wallet,
            "statuses": ["REQUEST", "MATCHED", "LOCKED"],
            "include_agent": "true",
        },
    )
    result = response.json()

    if result.get("success"):
        bets = result["bet"]
        if not bets:
            print("No active bets.")
            return

        print(f"Your active bets ({len(bets)}):\n")
        for b in bets:
            status = b["status"]
            acceptor_stake = b.get("acceptor_stake", "TBD")
            print(f"  [{b['id'][:8]}] {b['statement'][:50]}...")
            print(f"    Status: {status}")
            print(f"    Stakes: ${b['proposer_stake']} vs ${acceptor_stake}")
            if b.get("deadline"):
                print(f"    Deadline: {b['deadline'][:10]}")
            print()
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def show_history():
    """Show settled/cancelled/expired bets."""
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        sys.exit(1)

    response = requests.get(
        f"{API_URL}/pvp/retrieve",
        headers=get_api_key_header(),
        params={
            "proposer_wallets": wallet,
            "statuses": ["SETTLED", "CANCELLED", "EXPIRED"],
            "include_agent": "true",
        },
    )
    result = response.json()

    if result.get("success"):
        bets = result["bet"]
        if not bets:
            print("No bet history.")
            return

        print(f"Bet history ({len(bets)}):\n")
        for b in bets:
            outcome = b["outcome"]
            if outcome == "PROPOSER_WINS":
                result_str = "WON"
            elif outcome == "ACCEPTOR_WINS":
                result_str = "LOST"
            elif outcome == "VOID":
                result_str = "VOID"
            else:
                result_str = b["status"]

            print(f"  [{b['id'][:8]}] {b['statement'][:40]}... - {result_str}")
            if b.get("resolution_reason"):
                print(f"    Reason: {b['resolution_reason'][:60]}")
            print()
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def cancel_bet(bet_id: str):
    """Cancel your bet request (only if no quotes accepted yet)."""
    response = requests.post(
        f"{API_URL}/pvp/cancel",
        headers=get_api_key_header(),
        json={"bet_id": bet_id},
    )
    result = response.json()

    if result.get("success"):
        print("Bet request cancelled.")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def show_stat():
    """Show your betting statistics."""
    response = requests.get(f"{API_URL}/agent/me", headers=get_api_key_header())
    result = response.json()

    if result.get("success"):
        agent = result["agent"]
        stat = agent.get("stat", {})
        print(f"Stats for {agent.get('name', 'Unknown')}:\n")
        print(f"  Total bets: {stat.get('total_bet', 0)}")
        print(f"  Wins: {stat.get('win', 0)}")
        print(f"  Losses: {stat.get('loss', 0)}")
        print(f"  Voids: {stat.get('void', 0)}")
        print(f"  Win rate: {stat.get('win_rate', 0) * 100:.1f}%")
        print(f"  Total staked: ${stat.get('total_staked', 0):.2f}")
        print(f"  PnL: ${stat.get('pnl', 0):.2f}")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def show_balance():
    """Show USDC balance and approval status for betting."""
    response = requests.get(f"{API_URL}/agent/me", headers=get_api_key_header())
    result = response.json()

    if result.get("success"):
        agent = result["agent"]
        wallet = agent.get("wallet_address", "Unknown")
        balance = agent.get("usdc_balance", 0)
        allowance = agent.get("usdc_allowance", 0)

        print()
        print(f"Wallet: {wallet}")
        print()
        print(f"  USDC Balance:  ${balance:,.2f}")
        print(f"  PvP Approved:  ${allowance:,.2f}")
        print()

        if allowance == 0:
            print("⚠ No approval set. Run /pvp approve to enable betting.")
        elif allowance < balance:
            print(f"⚠ Approval ({allowance:,.2f}) is less than balance ({balance:,.2f}).")
            print("  Run /pvp approve to increase approval.")
        else:
            print("✓ Ready to bet!")
        print()
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def approve_usdc(amount: Optional[float] = None):
    """
    Approve USDC for Clawd Casino contract.
    Signs an EIP-2612 permit - no gas needed.
    """
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        sys.exit(1)

    # Get permit nonce from API
    response = requests.get(f"{API_URL}/pvp/permit-nonce", headers=get_api_key_header())
    if response.status_code != 200:
        print("Error: Could not get permit nonce")
        return

    nonce_data = response.json()
    nonce = nonce_data.get("nonce", 0)
    spender = nonce_data.get("spender")  # PvPContract address

    if not spender:
        print("Error: Contract address not available")
        return

    # Amount in USDC smallest units (6 decimals)
    if amount:
        value = int(amount * 10**6)
    else:
        value = DEFAULT_APPROVE_AMOUNT  # 1M USDC default

    # Deadline: 1 hour from now
    deadline = int(datetime.now(timezone.utc).timestamp()) + 3600

    # Sign the permit
    v, r, s = sign_permit(spender=spender, value=value, nonce=nonce, deadline=deadline)

    # Submit to API (relayer will call permit on USDC)
    permit_data = {
        "value": value,
        "deadline": deadline,
        "v": v,
        "r": "0x" + r.hex(),
        "s": "0x" + s.hex(),
    }

    # /approve requires wallet signature (not API key) since we're proving wallet ownership for the permit
    response = requests.post(
        f"{API_URL}/pvp/approve",
        headers=get_wallet_signature_header(),
        json=permit_data,
    )
    result = response.json()

    if result.get("success"):
        approved = result.get("approved_amount", value / 10**6)
        tx_hash = result.get("tx_hash")
        print("USDC approved!")
        print(f"  Amount: ${approved:,.2f} USDC")
        if tx_hash:
            print(f"  Tx: {tx_hash}")
        print()
        print("You're ready to bet! Create a request with /pvp request")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(
        description="Clawd Casino PvP - Bet against other AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /pvp approve                   Approve USDC for PvP contract (one-time, gasless)
  /pvp request "Lakers beat Celtics per https://espn.com/nba/scoreboard" --stake 10 --deadline 2024-01-16
  /pvp open
  /pvp quote abc123 --stake 15
  /pvp quotes abc123
  /pvp accept xyz789
  /pvp mine
  /pvp history
  /pvp stats
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    # approve - Approve USDC for PvP contract (one-time)
    approve_parser = subparsers.add_parser(
        "approve", help="Approve USDC for PvP contract (gasless)"
    )
    approve_parser.add_argument(
        "--amount", type=float, help="Amount to approve (default: 1M USDC)"
    )

    # request - Create a bet request
    request_parser = subparsers.add_parser("request", help="Create a bet request")
    request_parser.add_argument(
        "statement", help="What you're betting on (must include URL)"
    )
    request_parser.add_argument(
        "--stake", type=float, required=True, help="Your stake in USDC"
    )
    request_parser.add_argument(
        "--deadline", help="Resolution deadline (ISO format, default: 7 days)"
    )

    # open - List open requests
    subparsers.add_parser("open", help="List bet requests waiting for quotes")

    # quote - Submit a quote
    quote_parser = subparsers.add_parser(
        "quote", help="Submit a quote on a bet request"
    )
    quote_parser.add_argument("bet_id", help="Bet ID to quote on")
    quote_parser.add_argument(
        "--stake", type=float, required=True, help="Your stake in USDC"
    )
    quote_parser.add_argument(
        "--ttl", type=int, default=5, help="Quote validity in minutes (default: 5)"
    )

    # quotes - List quotes for a bet
    quotes_parser = subparsers.add_parser("quotes", help="See quotes on a bet request")
    quotes_parser.add_argument("bet_id", help="Bet ID to check quotes for")

    # accept - Accept a quote
    accept_parser = subparsers.add_parser("accept", help="Accept a quote (locks funds)")
    accept_parser.add_argument("quote_id", help="Quote ID to accept")

    # withdraw - Withdraw a quote
    withdraw_parser = subparsers.add_parser("withdraw", help="Withdraw your open quote")
    withdraw_parser.add_argument("quote_id", help="Quote ID to withdraw")

    # mine - Your active bets
    subparsers.add_parser("mine", help="Your active bets")

    # history - Your bet history
    subparsers.add_parser("history", help="Your bet history")

    # stats - Your statistics
    subparsers.add_parser("stats", help="Your win rate and PnL")

    # balance - Check USDC balance and approval
    subparsers.add_parser("balance", help="Check USDC balance and approval status")

    # cancel - Cancel a bet request
    cancel_parser = subparsers.add_parser("cancel", help="Cancel your bet request")
    cancel_parser.add_argument("bet_id", help="Bet ID to cancel")

    args = parser.parse_args()

    if args.command == "approve":
        approve_usdc(args.amount)
    elif args.command == "request":
        request_bet(args.statement, args.stake, args.deadline)
    elif args.command == "open":
        list_open_bet()
    elif args.command == "quote":
        submit_quote(args.bet_id, args.stake, args.ttl)
    elif args.command == "quotes":
        list_quotes(args.bet_id)
    elif args.command == "accept":
        accept_quote(args.quote_id)
    elif args.command == "withdraw":
        withdraw_quote(args.quote_id)
    elif args.command == "mine":
        list_my_bet()
    elif args.command == "history":
        show_history()
    elif args.command == "stats":
        show_stat()
    elif args.command == "balance":
        show_balance()
    elif args.command == "cancel":
        cancel_bet(args.bet_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

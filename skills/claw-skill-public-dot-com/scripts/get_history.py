import argparse
import os
import subprocess
import sys

from config import get_api_secret, get_account_id

try:
    from public_api_sdk import PublicApiClient, PublicApiClientConfiguration
    from public_api_sdk.auth_config import ApiKeyAuthConfig
except ImportError:
    print("Installing required dependency: publicdotcom-py...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "publicdotcom-py==0.1.8"])
    from public_api_sdk import PublicApiClient, PublicApiClientConfiguration
    from public_api_sdk.auth_config import ApiKeyAuthConfig


def get_history(account_id=None, transaction_type=None, limit=None):
    secret = get_api_secret()
    account_id = account_id or get_account_id()

    if not secret:
        print("Error: PUBLIC_COM_SECRET is not set.")
        sys.exit(1)

    if not account_id:
        print("Error: No account ID provided. Either pass --account-id or set PUBLIC_COM_ACCOUNT_ID.")
        sys.exit(1)

    try:
        client = PublicApiClient(
            ApiKeyAuthConfig(api_secret_key=secret),
            config=PublicApiClientConfiguration(default_account_number=account_id),
        )

        history = client.get_history()
        transactions = history.transactions

        # Filter by transaction type if specified
        if transaction_type:
            transactions = [t for t in transactions if t.type.value == transaction_type]

        # Apply limit if specified
        if limit:
            transactions = transactions[:limit]

        if not transactions:
            print("No transactions found.")
            client.close()
            return

        print("=" * 80)
        print(f"TRANSACTION HISTORY - Account: {account_id}")
        print("=" * 80)

        # Group transactions by type for better organization
        trades = [t for t in transactions if t.type.value == "TRADE"]
        money_movements = [t for t in transactions if t.type.value == "MONEY_MOVEMENT"]
        position_adjustments = [t for t in transactions if t.type.value == "POSITION_ADJUSTMENT"]

        def format_amount(amount):
            if amount is None:
                return "N/A"
            sign = "+" if amount >= 0 else ""
            return f"{sign}${amount:,.2f}"

        def format_quantity(qty):
            if qty is None:
                return "N/A"
            return f"{qty:,.5f}".rstrip("0").rstrip(".")

        def print_transaction(t):
            print(f"\n  [{t.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"  ID: {t.id}")
            print(f"  Description: {t.description}")
            if t.symbol:
                security_type = f" ({t.security_type.value})" if t.security_type else ""
                print(f"  Symbol: {t.symbol}{security_type}")
            if t.side:
                print(f"  Side: {t.side.value}")
            if t.quantity is not None:
                print(f"  Quantity: {format_quantity(t.quantity)}")
            if t.net_amount is not None:
                print(f"  Net Amount: {format_amount(t.net_amount)}")
            if t.principal_amount is not None:
                print(f"  Principal: {format_amount(t.principal_amount)}")
            if t.fees is not None and t.fees != 0:
                print(f"  Fees: ${t.fees:,.2f}")
            if t.direction:
                print(f"  Direction: {t.direction.value}")
            print(f"  Sub-type: {t.sub_type.value}")

        if trades:
            print("\n" + "-" * 80)
            print("📈 TRADES")
            print("-" * 80)
            for t in trades:
                print_transaction(t)

        if money_movements:
            print("\n" + "-" * 80)
            print("💰 MONEY MOVEMENTS")
            print("-" * 80)
            for t in money_movements:
                print_transaction(t)

        if position_adjustments:
            print("\n" + "-" * 80)
            print("🔄 POSITION ADJUSTMENTS")
            print("-" * 80)
            for t in position_adjustments:
                print_transaction(t)

        print("\n" + "=" * 80)
        print(f"Total transactions: {len(transactions)}")
        print(f"  Trades: {len(trades)}")
        print(f"  Money Movements: {len(money_movements)}")
        print(f"  Position Adjustments: {len(position_adjustments)}")
        print("=" * 80)

        client.close()
    except Exception as e:
        print(f"Error fetching history: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get transaction history from Public.com")
    parser.add_argument(
        "--account-id",
        required=False,
        help="Your Public.com account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)",
    )
    parser.add_argument(
        "--type",
        choices=["TRADE", "MONEY_MOVEMENT", "POSITION_ADJUSTMENT"],
        help="Filter by transaction type",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of transactions returned",
    )
    args = parser.parse_args()
    get_history(
        account_id=args.account_id,
        transaction_type=args.type,
        limit=args.limit,
    )

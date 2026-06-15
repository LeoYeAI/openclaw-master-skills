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


def get_orders(account_id=None):
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
            config=PublicApiClientConfiguration(
                default_account_number=account_id
            )
        )

        portfolio = client.get_portfolio()

        print("=" * 70)
        print(f"ACTIVE ORDERS - Account: {portfolio.account_id}")
        print("=" * 70)

        if not portfolio.orders:
            print("\n  No active orders.")
            print("\n" + "=" * 70)
            client.close()
            return

        for order in portfolio.orders:
            inst = order.instrument
            print(f"\n  📋 Order ID: {order.order_id}")
            print(f"  {'-' * 66}")
            print(f"    Symbol: {inst.symbol} ({inst.type.value})")
            print(f"    Side: {order.side.value}")
            print(f"    Type: {order.type.value}")
            print(f"    Status: {order.status.value}")

            # Quantity or notional
            if order.quantity is not None:
                print(f"    Quantity: {order.quantity}")
            if order.notional_value is not None:
                print(f"    Notional Value: ${order.notional_value:,.2f}")

            # Filled info
            if order.filled_quantity is not None and order.filled_quantity > 0:
                print(f"    Filled: {order.filled_quantity}")
            if order.average_price is not None:
                print(f"    Average Price: ${order.average_price:,.2f}")

            # Prices
            if order.limit_price is not None:
                print(f"    Limit Price: ${order.limit_price:,.2f}")
            if order.stop_price is not None:
                print(f"    Stop Price: ${order.stop_price:,.2f}")

            # Expiration
            if order.expiration:
                exp = order.expiration
                print(f"    Time in Force: {exp.time_in_force.value}")
                if exp.expiration_time:
                    print(f"    Expires: {exp.expiration_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Options specific
            if order.open_close_indicator is not None:
                print(f"    Open/Close: {order.open_close_indicator.value}")

            # Timestamps
            if order.created_at:
                print(f"    Created: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if order.closed_at:
                print(f"    Closed: {order.closed_at.strftime('%Y-%m-%d %H:%M:%S')}")

            # Reject reason if any
            if order.reject_reason:
                print(f"    ⚠️  Reject Reason: {order.reject_reason}")

            # Multi-leg orders
            if order.legs:
                print(f"    Legs:")
                for i, leg in enumerate(order.legs, 1):
                    print(f"      {i}. {leg.side.value} {leg.instrument.symbol}")

        print("\n" + "=" * 70)
        print(f"Total Active Orders: {len(portfolio.orders)}")
        print("=" * 70)

        client.close()
    except Exception as e:
        print(f"Error fetching orders: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get active orders from your Public.com account")
    parser.add_argument(
        "--account-id",
        required=False,
        help="Account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)"
    )

    args = parser.parse_args()
    get_orders(args.account_id)

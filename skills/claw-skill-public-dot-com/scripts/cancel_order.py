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


def cancel_order(order_id, account_id=None):
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

        client.cancel_order(order_id=order_id, account_id=account_id)

        print("=" * 60)
        print("ORDER CANCELLATION REQUESTED")
        print("=" * 60)
        print(f"\n  Order ID: {order_id}")
        print(f"  Account: {account_id}")
        print("\n" + "=" * 60)

        client.close()
    except Exception as e:
        print(f"Error cancelling order: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cancel an order on your Public.com account")
    parser.add_argument(
        "--order-id",
        required=True,
        help="The order ID to cancel"
    )
    parser.add_argument(
        "--account-id",
        required=False,
        help="Account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)"
    )

    args = parser.parse_args()
    cancel_order(order_id=args.order_id, account_id=args.account_id)

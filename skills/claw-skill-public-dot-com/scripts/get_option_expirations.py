import argparse
import os
import subprocess
import sys

from config import get_api_secret, get_account_id

try:
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        OrderInstrument,
        InstrumentType,
        OptionExpirationsRequest,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig
except ImportError:
    print("Installing required dependency: publicdotcom-py...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "publicdotcom-py==0.1.8"])
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        OrderInstrument,
        InstrumentType,
        OptionExpirationsRequest,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig


def get_option_expirations(symbol, account_id=None):
    """
    Get available option expiration dates for a symbol.

    Args:
        symbol: The underlying symbol (e.g., AAPL)
        account_id: Account ID (optional, uses PUBLIC_COM_ACCOUNT_ID env var if not provided)
    """
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
            config=PublicApiClientConfiguration(default_account_number=account_id)
        )

        request = OptionExpirationsRequest(
            instrument=OrderInstrument(symbol=symbol, type=InstrumentType.EQUITY)
        )
        response = client.get_option_expirations(request)

        expirations = response.expirations if hasattr(response, 'expirations') else []

        print("=" * 50)
        print(f"OPTION EXPIRATIONS - {symbol}")
        print("=" * 50)

        if not expirations:
            print("\n  No expiration dates found.")
            print("\n" + "=" * 50)
            client.close()
            return

        print(f"\n  Available expiration dates ({len(expirations)} total):")
        print()

        for i, exp in enumerate(expirations, 1):
            # Format the date nicely if it's a date object
            if hasattr(exp, 'strftime'):
                date_str = exp.strftime('%Y-%m-%d (%a, %b %d)')
            else:
                date_str = str(exp)
            print(f"    {i:3}. {date_str}")

        print("\n" + "=" * 50)
        print(f"Use with option chain: python3 scripts/get_option_chain.py {symbol} --expiration YYYY-MM-DD")
        print("=" * 50)

        client.close()
    except Exception as e:
        print(f"Error fetching option expirations: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get available option expiration dates for a symbol",
        epilog="Examples:\n"
               "  python3 get_option_expirations.py AAPL\n"
               "  python3 get_option_expirations.py TSLA\n"
               "  python3 get_option_expirations.py SPY",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "symbol",
        help="The underlying symbol (e.g., AAPL)"
    )
    parser.add_argument(
        "--account-id",
        required=False,
        help="Account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)"
    )

    args = parser.parse_args()

    get_option_expirations(symbol=args.symbol.upper(), account_id=args.account_id)

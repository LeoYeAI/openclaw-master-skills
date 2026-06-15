import argparse
import os
import subprocess
import sys

from config import get_api_secret, get_account_id

try:
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        InstrumentType,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig
except ImportError:
    print("Installing required dependency: publicdotcom-py...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "publicdotcom-py==0.1.8"])
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        InstrumentType,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig


def get_instrument(symbol, instrument_type="EQUITY"):
    """
    Get details for a specific instrument by symbol.

    Args:
        symbol: The ticker symbol (e.g., AAPL, BTC)
        instrument_type: The instrument type (EQUITY, OPTION, CRYPTO)
    """
    secret = get_api_secret()

    if not secret:
        print("Error: PUBLIC_COM_SECRET is not set.")
        sys.exit(1)

    instrument_type_map = {
        "EQUITY": InstrumentType.EQUITY,
        "OPTION": InstrumentType.OPTION,
        "CRYPTO": InstrumentType.CRYPTO,
    }

    account_id = get_account_id()

    if not account_id:
        print("Error: No account ID provided. Either pass --account-id or set PUBLIC_COM_ACCOUNT_ID.")
        sys.exit(1)

    try:
        client = PublicApiClient(
            ApiKeyAuthConfig(api_secret_key=secret),
            config=PublicApiClientConfiguration(default_account_number=account_id)
        )

        inst_type = instrument_type_map.get(instrument_type.upper())
        if not inst_type:
            print(f"Error: Invalid instrument type '{instrument_type}'. Must be EQUITY, OPTION, or CRYPTO.")
            sys.exit(1)

        response = client.get_instrument(symbol=symbol, instrument_type=inst_type)

        print("=" * 70)
        print("INSTRUMENT DETAILS")
        print("=" * 70)

        # Instrument info
        if response.instrument:
            print(f"\n  Symbol: {response.instrument.symbol}")
            print(f"  Type: {response.instrument.type.value}")

        # Trading status
        if response.trading:
            print(f"  Trading: {response.trading.value}")

        # Fractional trading
        if response.fractional_trading:
            print(f"  Fractional Trading: {response.fractional_trading.value}")

        # Option trading
        if response.option_trading:
            print(f"  Option Trading: {response.option_trading.value}")

        # Option spread trading
        if response.option_spread_trading:
            print(f"  Option Spread Trading: {response.option_spread_trading.value}")

        # Instrument details (if available)
        if response.instrument_details:
            print(f"\n  Additional Details:")
            print(f"    {response.instrument_details}")

        print("\n" + "=" * 70)

        client.close()
    except Exception as e:
        print(f"Error fetching instrument: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get details for a specific instrument from Public.com",
        epilog="Examples:\n"
               "  python3 get_instrument.py --symbol AAPL\n"
               "  python3 get_instrument.py --symbol AAPL --type EQUITY\n"
               "  python3 get_instrument.py --symbol BTC --type CRYPTO",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="The ticker symbol (e.g., AAPL, BTC)"
    )
    parser.add_argument(
        "--type",
        choices=["EQUITY", "OPTION", "CRYPTO"],
        default="EQUITY",
        help="Instrument type (default: EQUITY)"
    )

    args = parser.parse_args()

    get_instrument(
        symbol=args.symbol,
        instrument_type=args.type
    )

import argparse
import os
import subprocess
import sys

from config import get_api_secret, get_account_id

try:
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        InstrumentsRequest,
        InstrumentType,
        Trading,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig
except ImportError:
    print("Installing required dependency: publicdotcom-py...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "publicdotcom-py==0.1.8"])
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        InstrumentsRequest,
        InstrumentType,
        Trading,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig


def get_instruments(instrument_types=None, trading_filter=None, search=None, limit=None):
    """
    Get all available instruments with optional filtering.

    Args:
        instrument_types: List of instrument types to filter (EQUITY, OPTION, CRYPTO)
        trading_filter: List of trading statuses to filter (BUY_AND_SELL, BUY_ONLY, SELL_ONLY, NOT_TRADABLE)
        search: Optional search string to filter by symbol or name
        limit: Optional limit on number of results to display
    """
    secret = get_api_secret()

    if not secret:
        print("Error: PUBLIC_COM_SECRET is not set.")
        sys.exit(1)

    # Default to EQUITY if no types specified
    if not instrument_types:
        instrument_types = ["EQUITY"]

    instrument_type_map = {
        "EQUITY": InstrumentType.EQUITY,
        "OPTION": InstrumentType.OPTION,
        "CRYPTO": InstrumentType.CRYPTO,
    }

    trading_map = {
        "BUY_AND_SELL": Trading.BUY_AND_SELL,
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

        # Build request
        request_kwargs = {}

        # Add type filter
        type_filters = [instrument_type_map[t] for t in instrument_types]
        request_kwargs["type_filter"] = type_filters

        # Add trading filter if specified
        if trading_filter:
            trade_filters = [trading_map[t] for t in trading_filter]
            request_kwargs["trading_filter"] = trade_filters

        request = InstrumentsRequest(**request_kwargs)
        response = client.get_all_instruments(request)

        # Extract instruments list from response
        instruments_list = response.instruments if hasattr(response, 'instruments') else []

        # Apply search filter if specified
        if search:
            search_lower = search.lower()
            instruments_list = [
                inst for inst in instruments_list
                if search_lower in inst.instrument.symbol.lower()
            ]

        # Apply limit
        if limit and limit > 0:
            instruments_list = instruments_list[:limit]

        print("=" * 70)
        print("AVAILABLE INSTRUMENTS")
        print(f"Filters: Type={instrument_types}" + (f", Trading={trading_filter}" if trading_filter else ""))
        if search:
            print(f"Search: '{search}'")
        print("=" * 70)

        if not instruments_list:
            print("\n  No instruments found matching the criteria.")
            print("\n" + "=" * 70)
            client.close()
            return

        count = 0
        for inst in instruments_list:
            count += 1
            symbol = inst.instrument.symbol
            inst_type = inst.instrument.type.value

            print(f"\n  {symbol} ({inst_type})")

            # Trading status
            if inst.trading:
                print(f"    Trading: {inst.trading.value}")

            # Fractional trading
            if inst.fractional_trading:
                print(f"    Fractional Trading: {inst.fractional_trading.value}")

            # Option trading
            if inst.option_trading:
                print(f"    Option Trading: {inst.option_trading.value}")

            # Option spread trading
            if inst.option_spread_trading:
                print(f"    Option Spread Trading: {inst.option_spread_trading.value}")

        print("\n" + "=" * 70)
        print(f"Total Instruments: {count}")
        print("=" * 70)

        client.close()
    except Exception as e:
        print(f"Error fetching instruments: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get all available instruments from Public.com",
        epilog="Examples:\n"
               "  python3 get_instruments.py\n"
               "  python3 get_instruments.py --type EQUITY CRYPTO\n"
               "  python3 get_instruments.py --type EQUITY --trading BUY_AND_SELL\n"
               "  python3 get_instruments.py --search AAPL\n"
               "  python3 get_instruments.py --limit 50",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--type",
        nargs="+",
        choices=["EQUITY", "OPTION", "CRYPTO"],
        default=["EQUITY"],
        help="Instrument type(s) to filter (default: EQUITY)"
    )
    parser.add_argument(
        "--trading",
        nargs="+",
        choices=["BUY_AND_SELL", "BUY_ONLY", "SELL_ONLY", "NOT_TRADABLE"],
        help="Trading status filter"
    )
    parser.add_argument(
        "--search",
        help="Search by symbol or name (case-insensitive)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of results displayed"
    )

    args = parser.parse_args()

    get_instruments(
        instrument_types=args.type,
        trading_filter=args.trading,
        search=args.search,
        limit=args.limit
    )

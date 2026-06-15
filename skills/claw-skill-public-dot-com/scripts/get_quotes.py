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
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig


def get_quotes(symbols, account_id=None):
    """
    Get quotes for one or more instruments.

    Args:
        symbols: List of tuples (symbol, instrument_type)
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

    instrument_type_map = {
        "EQUITY": InstrumentType.EQUITY,
        "OPTION": InstrumentType.OPTION,
        "CRYPTO": InstrumentType.CRYPTO,
    }

    try:
        client = PublicApiClient(
            ApiKeyAuthConfig(api_secret_key=secret),
            config=PublicApiClientConfiguration(
                default_account_number=account_id
            )
        )

        # Build list of instruments
        instruments = []
        for symbol, inst_type in symbols:
            instruments.append(
                OrderInstrument(
                    symbol=symbol,
                    type=instrument_type_map[inst_type]
                )
            )

        quotes = client.get_quotes(instruments)

        print("=" * 60)
        print("QUOTES")
        print("=" * 60)

        for quote in quotes:
            inst = quote.instrument
            print(f"\n  {inst.symbol} ({inst.type.value})")
            print(f"    Last Price: ${quote.last:,.2f}")

            if hasattr(quote, 'bid') and quote.bid is not None:
                print(f"    Bid: ${quote.bid:,.2f}")
            if hasattr(quote, 'ask') and quote.ask is not None:
                print(f"    Ask: ${quote.ask:,.2f}")
            if hasattr(quote, 'bid_size') and quote.bid_size is not None:
                print(f"    Bid Size: {quote.bid_size}")
            if hasattr(quote, 'ask_size') and quote.ask_size is not None:
                print(f"    Ask Size: {quote.ask_size}")
            if hasattr(quote, 'volume') and quote.volume is not None:
                print(f"    Volume: {quote.volume:,}")
            if hasattr(quote, 'open') and quote.open is not None:
                print(f"    Open: ${quote.open:,.2f}")
            if hasattr(quote, 'high') and quote.high is not None:
                print(f"    High: ${quote.high:,.2f}")
            if hasattr(quote, 'low') and quote.low is not None:
                print(f"    Low: ${quote.low:,.2f}")
            if hasattr(quote, 'close') and quote.close is not None:
                print(f"    Previous Close: ${quote.close:,.2f}")

        print("\n" + "=" * 60)

        client.close()
    except Exception as e:
        print(f"Error fetching quotes: {e}")
        sys.exit(1)


def parse_symbol_arg(arg):
    """
    Parse a symbol argument in format SYMBOL:TYPE (e.g., AAPL:EQUITY, BTC:CRYPTO)
    If no type specified, defaults to EQUITY.
    """
    if ":" in arg:
        parts = arg.split(":", 1)
        symbol = parts[0].upper()
        inst_type = parts[1].upper()
    else:
        symbol = arg.upper()
        inst_type = "EQUITY"

    if inst_type not in ["EQUITY", "OPTION", "CRYPTO"]:
        print(f"Error: Invalid instrument type '{inst_type}'. Must be EQUITY, OPTION, or CRYPTO.")
        sys.exit(1)

    return (symbol, inst_type)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get quotes for one or more instruments",
        epilog="Examples:\n"
               "  python3 get_quotes.py AAPL\n"
               "  python3 get_quotes.py AAPL GOOGL MSFT\n"
               "  python3 get_quotes.py AAPL:EQUITY BTC:CRYPTO\n"
               "  python3 get_quotes.py AAPL260320C00280000:OPTION",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="Symbol(s) to quote in format SYMBOL or SYMBOL:TYPE (TYPE defaults to EQUITY)"
    )
    parser.add_argument(
        "--account-id",
        required=False,
        help="Account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)"
    )

    args = parser.parse_args()

    # Parse all symbol arguments
    parsed_symbols = [parse_symbol_arg(s) for s in args.symbols]

    get_quotes(parsed_symbols, account_id=args.account_id)

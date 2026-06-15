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
        OptionChainRequest,
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
        OptionChainRequest,
        OptionExpirationsRequest,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig


def get_option_expirations(client, symbol):
    """Get available expiration dates for a symbol."""
    request = OptionExpirationsRequest(
        instrument=OrderInstrument(symbol=symbol, type=InstrumentType.EQUITY)
    )
    response = client.get_option_expirations(request)
    return response.expirations if hasattr(response, 'expirations') else []


def list_expirations(symbol, account_id=None):
    """List available expiration dates for a symbol."""
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

        expirations = get_option_expirations(client, symbol)

        print("=" * 50)
        print(f"OPTION EXPIRATIONS - {symbol}")
        print("=" * 50)

        if not expirations:
            print("\n  No expiration dates found.")
        else:
            print(f"\n  Available expiration dates:")
            for i, exp in enumerate(expirations, 1):
                # Format the date nicely if it's a date object
                if hasattr(exp, 'strftime'):
                    date_str = exp.strftime('%Y-%m-%d')
                else:
                    date_str = str(exp)
                print(f"    {i}. {date_str}")

        print("\n" + "=" * 50)
        client.close()
    except Exception as e:
        print(f"Error fetching expirations: {e}")
        sys.exit(1)


def parse_osi_symbol(osi_symbol):
    """
    Parse an OSI option symbol to extract strike price.
    Format: AAPL260204C00175000
    - Last 8 digits are strike * 1000 (00175000 = $175.00)
    """
    try:
        strike_str = osi_symbol[-8:]
        strike = int(strike_str) / 1000
        return strike
    except (ValueError, IndexError):
        return None


def format_decimal(value, prefix="$", default="--"):
    """Format a decimal value for display."""
    if value is None:
        return default
    try:
        from decimal import Decimal
        if isinstance(value, Decimal):
            return f"{prefix}{float(value):,.2f}"
        elif isinstance(value, (int, float)):
            return f"{prefix}{value:,.2f}"
        else:
            return str(value)
    except (ValueError, TypeError):
        return default


def format_int(value, default="--"):
    """Format an integer value for display."""
    if value is None:
        return default
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return default


def get_option_chain(symbol, expiration_date=None, account_id=None):
    """
    Get option chain for a symbol and expiration date.

    Args:
        symbol: The underlying symbol (e.g., AAPL)
        expiration_date: Expiration date (YYYY-MM-DD). If not provided, uses the nearest expiration.
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

        # If no expiration date provided, get the first available one
        if not expiration_date:
            expirations = get_option_expirations(client, symbol)
            if not expirations:
                print(f"Error: No option expirations found for {symbol}")
                sys.exit(1)
            expiration_date = expirations[0]
            print(f"Using nearest expiration: {expiration_date}")

        # Build the request
        request = OptionChainRequest(
            instrument=OrderInstrument(symbol=symbol, type=InstrumentType.EQUITY),
            expiration_date=expiration_date
        )

        option_chain = client.get_option_chain(request)

        # Get base symbol from response
        base_symbol = getattr(option_chain, 'base_symbol', symbol)

        print("=" * 120)
        print(f"OPTION CHAIN - {base_symbol}")
        print(f"Expiration: {expiration_date}")
        print("=" * 120)

        # Get calls and puts from the response
        calls = getattr(option_chain, 'calls', []) or []
        puts = getattr(option_chain, 'puts', []) or []

        def print_options(options, option_type):
            """Print a list of options (calls or puts)."""
            if not options:
                return

            emoji = "📈" if option_type == "CALLS" else "📉"
            print(f"\n{emoji} {option_type}")
            print("-" * 120)
            print(f"  {'OSI Symbol':<25} {'Strike':>10} {'Bid':>10} {'BidSz':>8} {'Ask':>10} {'AskSz':>8} {'Last':>10} {'Volume':>10} {'OI':>10}")
            print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*10} {'-'*10}")

            for opt in options:
                # Get OSI symbol from instrument
                osi_symbol = opt.instrument.symbol if hasattr(opt, 'instrument') else "N/A"

                # Parse strike from OSI symbol
                strike = parse_osi_symbol(osi_symbol)

                # Get quote data
                bid = getattr(opt, 'bid', None)
                bid_size = getattr(opt, 'bid_size', None)
                ask = getattr(opt, 'ask', None)
                ask_size = getattr(opt, 'ask_size', None)
                last = getattr(opt, 'last', None)
                volume = getattr(opt, 'volume', None)
                oi = getattr(opt, 'open_interest', None)

                # Format values
                strike_str = f"${strike:,.2f}" if strike else "--"
                bid_str = format_decimal(bid)
                bid_sz_str = format_int(bid_size)
                ask_str = format_decimal(ask)
                ask_sz_str = format_int(ask_size)
                last_str = format_decimal(last)
                vol_str = format_int(volume)
                oi_str = format_int(oi)

                print(f"  {osi_symbol:<25} {strike_str:>10} {bid_str:>10} {bid_sz_str:>8} {ask_str:>10} {ask_sz_str:>8} {last_str:>10} {vol_str:>10} {oi_str:>10}")

        # Print calls and puts
        print_options(calls, "CALLS")
        print_options(puts, "PUTS")

        if not calls and not puts:
            print("\n  No options data found in the response.")

        print("\n" + "=" * 120)
        print(f"Total: {len(calls)} calls, {len(puts)} puts")
        print("=" * 120)

        client.close()
    except Exception as e:
        print(f"Error fetching option chain: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get option chain for a symbol",
        epilog="Examples:\n"
               "  python3 get_option_chain.py AAPL --list-expirations\n"
               "  python3 get_option_chain.py AAPL\n"
               "  python3 get_option_chain.py AAPL --expiration 2026-03-20",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "symbol",
        help="The underlying symbol (e.g., AAPL)"
    )
    parser.add_argument(
        "--expiration",
        help="Expiration date (YYYY-MM-DD). If not provided, uses the nearest expiration."
    )
    parser.add_argument(
        "--list-expirations",
        action="store_true",
        help="List available expiration dates instead of fetching the chain"
    )
    parser.add_argument(
        "--account-id",
        required=False,
        help="Account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)"
    )

    args = parser.parse_args()

    if args.list_expirations:
        list_expirations(symbol=args.symbol.upper(), account_id=args.account_id)
    else:
        get_option_chain(
            symbol=args.symbol.upper(),
            expiration_date=args.expiration,
            account_id=args.account_id
        )

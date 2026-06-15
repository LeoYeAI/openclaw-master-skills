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


def get_option_greeks(osi_symbols, account_id=None):
    """
    Get option greeks for one or more OSI option symbols.

    Args:
        osi_symbols: List of OSI option symbols (e.g., AAPL260116C00270000)
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
            config=PublicApiClientConfiguration(
                default_account_number=account_id
            )
        )

        greeks_response = client.get_option_greeks(osi_symbols=osi_symbols)

        print("=" * 70)
        print("OPTION GREEKS")
        print("=" * 70)

        if not greeks_response.greeks:
            print("\n  No greeks data found for the provided symbols.")
            print("\n" + "=" * 70)
            client.close()
            return

        for greek_data in greeks_response.greeks:
            # Get the symbol if available
            symbol = getattr(greek_data, 'osi_symbol', None) or getattr(greek_data, 'symbol', 'Unknown')
            greeks = greek_data.greeks

            print(f"\n  📊 {symbol}")
            print(f"  {'-' * 66}")

            # Delta - measures rate of change of option price with respect to underlying
            if hasattr(greeks, 'delta') and greeks.delta is not None:
                print(f"    Delta:   {greeks.delta:>10.4f}    (Price sensitivity to underlying)")

            # Gamma - rate of change of delta
            if hasattr(greeks, 'gamma') and greeks.gamma is not None:
                print(f"    Gamma:   {greeks.gamma:>10.4f}    (Delta sensitivity to underlying)")

            # Theta - time decay
            if hasattr(greeks, 'theta') and greeks.theta is not None:
                print(f"    Theta:   {greeks.theta:>10.4f}    (Daily time decay)")

            # Vega - sensitivity to volatility
            if hasattr(greeks, 'vega') and greeks.vega is not None:
                print(f"    Vega:    {greeks.vega:>10.4f}    (Volatility sensitivity)")

            # Rho - sensitivity to interest rates
            if hasattr(greeks, 'rho') and greeks.rho is not None:
                print(f"    Rho:     {greeks.rho:>10.4f}    (Interest rate sensitivity)")

            # Implied volatility
            if hasattr(greeks, 'implied_volatility') and greeks.implied_volatility is not None:
                print(f"    IV:      {greeks.implied_volatility:>10.2%}    (Implied volatility)")

        print("\n" + "=" * 70)
        print(f"Total Options: {len(greeks_response.greeks)}")
        print("=" * 70)

        client.close()
    except Exception as e:
        print(f"Error fetching option greeks: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get option greeks for one or more OSI option symbols",
        epilog="Examples:\n"
               "  python3 get_option_greeks.py AAPL260116C00270000\n"
               "  python3 get_option_greeks.py AAPL260116C00270000 AAPL260116P00270000\n\n"
               "OSI Symbol Format:\n"
               "  AAPL260116C00270000\n"
               "  ^^^^------^--------\n"
               "  |   |     |  Strike price ($270.00)\n"
               "  |   |     Call (C) or Put (P)\n"
               "  |   Expiration (Jan 16, 2026)\n"
               "  Underlying symbol",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "osi_symbols",
        nargs="+",
        help="OSI option symbol(s) (e.g., AAPL260116C00270000)"
    )
    parser.add_argument(
        "--account-id",
        required=False,
        help="Account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)"
    )

    args = parser.parse_args()

    get_option_greeks(osi_symbols=args.osi_symbols, account_id=args.account_id)

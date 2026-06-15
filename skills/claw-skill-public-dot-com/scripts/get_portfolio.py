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


def get_portfolio(account_id=None):
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

        # Account Info
        print("=" * 60)
        print(f"PORTFOLIO - Account: {portfolio.account_id} ({portfolio.account_type.value})")
        print("=" * 60)

        # Buying Power
        print("\n📊 BUYING POWER")
        print("-" * 40)
        bp = portfolio.buying_power
        print(f"  Buying Power:         ${bp.buying_power:,.2f}")
        print(f"  Cash Only:            ${bp.cash_only_buying_power:,.2f}")
        print(f"  Options Buying Power: ${bp.options_buying_power:,.2f}")

        # Equity Breakdown
        print("\n💰 EQUITY BREAKDOWN")
        print("-" * 40)
        total_equity = sum(e.value for e in portfolio.equity)
        print(f"  Total Equity: ${total_equity:,.2f}")
        print()
        for eq in portfolio.equity:
            asset_type = eq.type.value.replace("_", " ").title()
            print(f"  {asset_type:20} ${eq.value:>12,.2f}  ({eq.percentage_of_portfolio:>6.2f}%)")

        # Group positions by type
        if portfolio.positions:
            equities = [p for p in portfolio.positions if p.instrument.type.value == "EQUITY"]
            options = [p for p in portfolio.positions if p.instrument.type.value == "OPTION"]
            crypto = [p for p in portfolio.positions if p.instrument.type.value == "CRYPTO"]

            def print_position(pos):
                inst = pos.instrument
                print(f"\n  {inst.name} ({inst.symbol})")
                print(f"    Quantity: {pos.quantity}")
                print(f"    Current Value: ${pos.current_value:,.2f} ({pos.percent_of_portfolio:.2f}% of portfolio)")
                print(f"    Last Price: ${pos.last_price.last_price:,.2f}")

                # Position daily gain
                if pos.position_daily_gain:
                    dg = pos.position_daily_gain
                    gain_sign = "+" if dg.gain_value >= 0 else ""
                    print(f"    Today's Gain: {gain_sign}${dg.gain_value:,.2f} ({gain_sign}{dg.gain_percentage:.2f}%)")

                # Cost basis and total gain
                if pos.cost_basis:
                    cb = pos.cost_basis
                    total_gain_sign = "+" if cb.gain_value >= 0 else ""
                    print(f"    Cost Basis: ${cb.total_cost:,.2f} (${cb.unit_cost:,.2f}/unit)")
                    print(f"    Total Gain: {total_gain_sign}${cb.gain_value:,.2f} ({total_gain_sign}{cb.gain_percentage:.2f}%)")

            if equities:
                print("\n📈 EQUITIES")
                print("-" * 60)
                for pos in equities:
                    print_position(pos)

            if options:
                print("\n📜 OPTIONS")
                print("-" * 60)
                for pos in options:
                    print_position(pos)

            if crypto:
                print("\n🪙 CRYPTO")
                print("-" * 60)
                for pos in crypto:
                    print_position(pos)

        print("\n" + "=" * 60)

        client.close()
    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--account-id", required=False, help="Your Public.com account ID (uses PUBLIC_COM_ACCOUNT_ID env var if not provided)")
    args = parser.parse_args()
    get_portfolio(args.account_id)

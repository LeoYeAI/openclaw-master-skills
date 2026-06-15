import argparse
import os
import subprocess
import sys
from decimal import Decimal

try:
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        PreflightRequest,
        OrderInstrument,
        InstrumentType,
        OrderSide,
        OrderType,
        OrderExpirationRequest,
        TimeInForce,
        EquityMarketSession,
        OpenCloseIndicator,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig
except ImportError:
    print("Installing required dependency: publicdotcom-py...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "publicdotcom-py==0.1.8"])
    from public_api_sdk import (
        PublicApiClient,
        PublicApiClientConfiguration,
        PreflightRequest,
        OrderInstrument,
        InstrumentType,
        OrderSide,
        OrderType,
        OrderExpirationRequest,
        TimeInForce,
        EquityMarketSession,
        OpenCloseIndicator,
    )
    from public_api_sdk.auth_config import ApiKeyAuthConfig

from config import get_api_secret, get_account_id


def perform_preflight(
    symbol,
    instrument_type,
    side,
    order_type,
    quantity=None,
    amount=None,
    limit_price=None,
    stop_price=None,
    session=None,
    open_close=None,
    time_in_force=None,
    account_id=None,
):
    """
    Perform a preflight calculation to estimate the cost and account impact of an order.

    Args:
        symbol: The ticker symbol (e.g., AAPL, BTC, NVDA260213P00177500)
        instrument_type: EQUITY, OPTION, or CRYPTO
        side: BUY or SELL
        order_type: LIMIT, MARKET, STOP, or STOP_LIMIT
        quantity: Number of shares/contracts
        amount: Notional dollar amount (alternative to quantity)
        limit_price: Limit price for LIMIT/STOP_LIMIT orders
        stop_price: Stop price for STOP/STOP_LIMIT orders
        session: CORE or EXTENDED (for equity orders)
        open_close: OPEN or CLOSE (for option orders)
        time_in_force: DAY or GTC
        account_id: Account ID (optional if PUBLIC_COM_ACCOUNT_ID is set)
    """
    secret = get_api_secret()
    account_id = account_id or get_account_id()

    if not secret:
        print("Error: PUBLIC_COM_SECRET is not set.")
        sys.exit(1)

    if not account_id:
        print("Error: No account ID provided. Either pass --account-id or set PUBLIC_COM_ACCOUNT_ID.")
        sys.exit(1)

    # Validate quantity/amount
    if quantity is None and amount is None:
        print("Error: Either --quantity or --amount must be provided.")
        sys.exit(1)

    # Validate limit price for LIMIT/STOP_LIMIT orders
    if order_type in ["LIMIT", "STOP_LIMIT"] and limit_price is None:
        print(f"Error: --limit-price is required for {order_type} orders.")
        sys.exit(1)

    # Validate stop price for STOP/STOP_LIMIT orders
    if order_type in ["STOP", "STOP_LIMIT"] and stop_price is None:
        print(f"Error: --stop-price is required for {order_type} orders.")
        sys.exit(1)

    # Map string values to enums
    instrument_type_map = {
        "EQUITY": InstrumentType.EQUITY,
        "OPTION": InstrumentType.OPTION,
        "CRYPTO": InstrumentType.CRYPTO,
    }
    side_map = {
        "BUY": OrderSide.BUY,
        "SELL": OrderSide.SELL,
    }
    order_type_map = {
        "LIMIT": OrderType.LIMIT,
        "MARKET": OrderType.MARKET,
        "STOP": OrderType.STOP,
        "STOP_LIMIT": OrderType.STOP_LIMIT,
    }
    session_map = {
        "CORE": EquityMarketSession.CORE,
        "EXTENDED": EquityMarketSession.EXTENDED,
    }
    open_close_map = {
        "OPEN": OpenCloseIndicator.OPEN,
        "CLOSE": OpenCloseIndicator.CLOSE,
    }
    time_in_force_map = {
        "DAY": TimeInForce.DAY,
    }

    try:
        client = PublicApiClient(
            ApiKeyAuthConfig(api_secret_key=secret),
            config=PublicApiClientConfiguration(default_account_number=account_id),
        )

        # Build preflight request
        preflight_kwargs = {
            "instrument": OrderInstrument(
                symbol=symbol,
                type=instrument_type_map[instrument_type],
            ),
            "order_side": side_map[side],
            "order_type": order_type_map[order_type],
            "expiration": OrderExpirationRequest(time_in_force=time_in_force_map.get(time_in_force, TimeInForce.DAY)),
        }

        # Add quantity or amount
        if quantity is not None:
            preflight_kwargs["quantity"] = Decimal(str(quantity))
        if amount is not None:
            preflight_kwargs["amount"] = Decimal(str(amount))

        # Add limit price if applicable
        if limit_price is not None:
            preflight_kwargs["limit_price"] = Decimal(str(limit_price))

        # Add stop price if applicable
        if stop_price is not None:
            preflight_kwargs["stop_price"] = Decimal(str(stop_price))

        # Add session for equity orders
        if session and instrument_type == "EQUITY":
            preflight_kwargs["equity_market_session"] = session_map[session]

        # Add open/close indicator for options
        if open_close and instrument_type == "OPTION":
            preflight_kwargs["open_close_indicator"] = open_close_map[open_close]

        preflight_request = PreflightRequest(**preflight_kwargs)
        preflight_response = client.perform_preflight_calculation(preflight_request)

        print("=" * 70)
        print("PREFLIGHT CALCULATION RESULT")
        print("=" * 70)

        # Order details
        print("\n  ORDER DETAILS:")
        print(f"    Symbol: {symbol}")
        print(f"    Type: {instrument_type}")
        print(f"    Side: {side}")
        print(f"    Order Type: {order_type}")
        print(f"    Time In Force: {time_in_force or 'DAY'}")
        if quantity is not None:
            print(f"    Quantity: {quantity}")
        if amount is not None:
            print(f"    Amount: ${amount}")
        if limit_price is not None:
            print(f"    Limit Price: ${limit_price}")
        if stop_price is not None:
            print(f"    Stop Price: ${stop_price}")
        if session and instrument_type == "EQUITY":
            print(f"    Session: {session}")
        if open_close and instrument_type == "OPTION":
            print(f"    Open/Close: {open_close}")

        # Preflight response details
        print("\n  ESTIMATED IMPACT:")
        if hasattr(preflight_response, 'estimated_total_cost') and preflight_response.estimated_total_cost is not None:
            print(f"    Estimated Total Cost: ${preflight_response.estimated_total_cost}")
        if hasattr(preflight_response, 'estimated_price') and preflight_response.estimated_price is not None:
            print(f"    Estimated Price: ${preflight_response.estimated_price}")
        if hasattr(preflight_response, 'estimated_quantity') and preflight_response.estimated_quantity is not None:
            print(f"    Estimated Quantity: {preflight_response.estimated_quantity}")
        if hasattr(preflight_response, 'buying_power_impact') and preflight_response.buying_power_impact is not None:
            print(f"    Buying Power Impact: ${preflight_response.buying_power_impact}")
        if hasattr(preflight_response, 'fees') and preflight_response.fees is not None:
            print(f"    Estimated Fees: ${preflight_response.fees}")

        # Print full response for debugging/visibility
        print("\n  FULL RESPONSE:")
        print(f"    {preflight_response}")

        print("\n" + "=" * 70)

        client.close()
    except Exception as e:
        print(f"Error performing preflight calculation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform a preflight calculation to estimate order cost and account impact",
        epilog="Examples:\n"
               "  Equity limit buy:\n"
               "    python3 preflight.py --symbol AAPL --type EQUITY --side BUY --order-type LIMIT --quantity 10 --limit-price 227.50\n\n"
               "  Equity market sell:\n"
               "    python3 preflight.py --symbol AAPL --type EQUITY --side SELL --order-type MARKET --quantity 10\n\n"
               "  Crypto buy by amount:\n"
               "    python3 preflight.py --symbol BTC --type CRYPTO --side BUY --order-type MARKET --amount 100\n\n"
               "  Option contract buy:\n"
               "    python3 preflight.py --symbol NVDA260213P00177500 --type OPTION --side BUY --order-type LIMIT --quantity 1 --limit-price 4.00 --open-close OPEN",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--symbol", required=True, help="Stock/crypto/option symbol")
    parser.add_argument(
        "--type",
        required=True,
        choices=["EQUITY", "OPTION", "CRYPTO"],
        help="Instrument type",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        help="Order side",
    )
    parser.add_argument(
        "--order-type",
        required=True,
        choices=["LIMIT", "MARKET", "STOP", "STOP_LIMIT"],
        help="Order type",
    )
    parser.add_argument("--quantity", type=float, help="Number of shares/contracts")
    parser.add_argument("--amount", type=float, help="Notional dollar amount")
    parser.add_argument("--limit-price", type=float, help="Limit price (required for LIMIT/STOP_LIMIT)")
    parser.add_argument("--stop-price", type=float, help="Stop price (required for STOP/STOP_LIMIT)")
    parser.add_argument(
        "--session",
        choices=["CORE", "EXTENDED"],
        default="CORE",
        help="Market session for equity orders (CORE or EXTENDED)",
    )
    parser.add_argument(
        "--open-close",
        choices=["OPEN", "CLOSE"],
        help="Open/Close indicator for options (OPEN to open a new position, CLOSE to close existing)",
    )
    parser.add_argument(
        "--time-in-force",
        choices=["DAY", "GTC"],
        default="DAY",
        help="Time in force: DAY (default) or GTC (Good Till Cancelled)",
    )
    parser.add_argument("--account-id", help="Account ID (uses PUBLIC_COM_ACCOUNT_ID if not provided)")

    args = parser.parse_args()

    perform_preflight(
        symbol=args.symbol,
        instrument_type=args.type,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        amount=args.amount,
        limit_price=args.limit_price,
        stop_price=args.stop_price,
        session=args.session,
        open_close=args.open_close,
        time_in_force=args.time_in_force,
        account_id=args.account_id,
    )

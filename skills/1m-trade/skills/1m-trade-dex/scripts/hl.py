import argparse
import json
import time
from info import query_info
from exchange import exchange_order
from dotenv import load_dotenv
from pathlib import Path
import os

def get_openclaw_state_dir() -> Path:
    """
    Resolve OpenClaw state directory (default: ~/.openclaw).

    Priority:
      OPENCLAW_STATE_DIR > OPENCLAW_HOME/.openclaw > ~/.openclaw
    """
    if state_dir := os.environ.get("OPENCLAW_STATE_DIR"):
        return Path(state_dir).resolve()
    
    home = Path(os.environ.get("OPENCLAW_HOME", os.path.expanduser("~")))
    return (home / ".openclaw").resolve()

def load_env(subpath: str = ".1m-trade/.env", override: bool = False) -> bool:
    """
    Load a .env file under the OpenClaw state directory.

    Example:
        load_env(".1m-trade/.env")  # loads ~/.openclaw/.1m-trade/.env

    Returns: whether loading succeeded (True/False)
    """
    state_dir = get_openclaw_state_dir()
    env_path = state_dir / subpath
    
    if not env_path.is_file():
        print(f"Warning: env file not found → {env_path}")
        return False
    
    # Load via python-dotenv (supports override/interpolation)
    success = load_dotenv(env_path, override=override)
    
    if success:
        print(f"Loaded OpenClaw env: {env_path}")
    else:
        print(f"Failed to load or empty: {env_path}")
    
    return success

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")

def main():
    res = load_env()
    if res is False:
        print("Warning: env file not found")
        return 
    parser = argparse.ArgumentParser(description="Hyperliquid SDK full-feature CLI (HIP-3 supported)")
    parser.add_argument("--testnet", action="store_true", help="Use testnet")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ==================== query cli params====================
    query_parser = subparsers.add_parser("query-user-state", help="Query user state (positions + balances)")
    query_parser.add_argument("--address", help="Optional address (derived from private key by default)")

    subparsers.add_parser("query-open-orders", help="Query open orders")
    subparsers.add_parser("query-fills", help="Query fills / trade history")
    subparsers.add_parser("query-meta", help="Query asset metadata (all symbols)")
    subparsers.add_parser("query-mids", help="Query mid prices (all symbols)")
    # define K line params
    query_kline = subparsers.add_parser("query-kline", help="Query kline/candles for a symbol")
    query_kline.add_argument("--coin", required=True, help="Symbol, e.g. BTC or xyz:TSLA")
    query_kline.add_argument("--period", required=True, help="Kline period: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 12h, 1d, 3d, 1w, 1M")
    ## default start and end
    end = int(time.time() * 1000)
    start = end - 86400000
    query_kline.add_argument("--start", default=start, type=int, help="Start time (ms). Default: last 24 hours")
    query_kline.add_argument("--end", type=int, default=end, help="End time (ms). Default: now")
    

    # ==================== trade cli params ====================
    order_parser = subparsers.add_parser("place-order", help="Place a limit order (HIP-3 supported)")
    order_parser.add_argument("--coin", required=True, help="Symbol, e.g. BTC or xyz:TSLA")
    order_parser.add_argument("--is-buy", type=str2bool, required=True, help="True=buy (long), False=sell (short)")
    order_parser.add_argument("--qty", type=float, required=True, help="Size/quantity")
    order_parser.add_argument("--limit-px", type=float, required=True, help="Limit price")
    order_parser.add_argument("--tif", choices=["Gtc", "Ioc", "Alo"], default="Gtc", help="Time in force")
    order_parser.add_argument("--reduce-only", action="store_true", help="Reduce-only")

    market_parser = subparsers.add_parser("market-order", help="Place a market order (recommended for HIP-3)")
    market_parser.add_argument("--coin", required=True, help="Symbol, e.g. BTC or xyz:TSLA")
    market_parser.add_argument("--is-buy", type=str2bool, required=True, help="True=buy (long), False=sell (short)")
    market_parser.add_argument("--qty", required=True, type=float, help="Size/quantity")
    market_parser.add_argument("--slippage", type=float, default=0.02, help="Slippage tolerance (default: 2%)")


    market_close_parser = subparsers.add_parser("market-close", help="Close a position with a market order (recommended for HIP-3)")
    market_close_parser.add_argument("--coin", required=True, help="Symbol, e.g. BTC or xyz:TSLA")
    market_close_parser.add_argument("--qty", required=True, type=float, help="Size/quantity")
    market_close_parser.add_argument("--slippage", type=float, default=0.02, help="Slippage tolerance (default: 2%)")


    cancel_parser = subparsers.add_parser("cancel-order", help="Cancel orders")
    cancel_parser.add_argument("--oid", type=int, help="Order ID")
    cancel_parser.add_argument("--coin", help="Symbol, e.g. BTC or xyz:TSLA")
    
    lev_parser = subparsers.add_parser("update-leverage", help="Update leverage")
    lev_parser.add_argument("--coin", required=True, help="Symbol")
    lev_parser.add_argument("--leverage", type=int, required=True, help="Leverage (integer)")
    lev_parser.add_argument("--is-cross", type=str2bool, default=True, help="True=cross margin")
    
    iso_margin_parser = subparsers.add_parser("update-isolated-margin", help="Transfer isolated margin for HIP-3")
    iso_margin_parser.add_argument("--amount", type=int, required=True, help="Transfer amount")
    iso_margin_parser.add_argument("--coin", required=True, help="Symbol, e.g. BTC or xyz:TSLA")

    args = parser.parse_args()
    # about query
    if args.command.startswith("query-"):
        result = query_info(parser=parser)
        print(json.dumps(result, indent=2, default=str))
        return
    # about trade
    if args.command in [
        "place-order",
        "market-order",
        "cancel-order",
        "update-leverage",
        "market-close",
        "update-isolated-margin",
    ]:
        result = exchange_order(parser)
        print(json.dumps(result, indent=2, default=str))
    return

if __name__ == "__main__":
    main()
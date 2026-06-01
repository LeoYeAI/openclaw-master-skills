import json
import os
import sys
from hyperliquid.info import Info
import eth_account

def get_address(testnet=False):
    print("Testnet" if testnet else "Mainnet")
    # If address is explicitly set, use it
    address = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
    if address:
        return address
    # Otherwise derive address from private key
    private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    if not private_key:
        print(json.dumps({"error": "HYPERLIQUID_PRIVATE_KEY environment variable is not set"}))
        sys.exit(1)
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    account = eth_account.Account.from_key(private_key)
    return account.address
    

def get_info():
    return Info(skip_ws=True, perp_dexs=['', "xyz"])

def query_info(parser):
    args = parser.parse_args()
    info = get_info()
    result = []
    if args.command.startswith("query-"):
        if args.command in [
            "query-user-state",
            "query-open-orders",
            "query-meta",
            "query-fills"
        ]:
            if hasattr(args, "address") and args.address:
                query_address = args.address
            else:
                query_address = get_address(args.testnet)
            if args.command == "query-user-state":
                perps = info.user_state(query_address)
                spot = info.spot_user_state(query_address)
                perps_xyz = info.user_state(query_address, dex="xyz")
                result = {"crpto-perps": perps} | {"spot": spot} | {"HIP3-xyz": perps_xyz}

            elif args.command == "query-open-orders":
                result = info.open_orders(query_address)
            elif args.command == "query-fills":
                result = info.user_fills(query_address)
            elif args.command == "query-meta":
                crypto = info.meta()
                xyz = info.meta("xyz")
                result = crypto.get("universe") + xyz.get("universe")
        elif args.command == "query-mids":
            crypto = info.all_mids()
            xyz = info.all_mids("xyz")
            result = crypto | xyz
            result = {k: v for k, v in result.items() if not k.startswith("@")}
        elif args.command == "query-kline":
            result = info.candles_snapshot(
                name=args.coin,
                interval=args.period,
                startTime=args.start,
                endTime=args.end,
            )
        return result
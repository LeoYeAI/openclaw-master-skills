import json
import os
import sys
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account.signers.local import LocalAccount
import eth_account

def get_exchange(testnet=False):
    print("Testnet" if testnet else "Mainnet")
    # Private key is required (proxy key or main wallet key)
    private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    if not private_key:
        print(json.dumps({"error": "HYPERLIQUID_PRIVATE_KEY environment variable is not set"}))
        sys.exit(1)
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    api_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL

    wallet: LocalAccount = eth_account.Account.from_key(private_key)

    env_address = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
    if env_address:
        address = env_address
    else:
        account = eth_account.Account.from_key(private_key)
        address = account.address
    return Exchange(wallet=wallet, account_address=address, base_url=api_url, perp_dexs=["", "xyz"]), address

# Compute trading precision
def query_decimals(exchange:Exchange, name):
    asset = exchange.info.name_to_asset(name)

    sz_decimal = exchange.info.asset_to_sz_decimals[asset]
    px_decimal = 6 - exchange.info.asset_to_sz_decimals[asset]

    return sz_decimal, px_decimal

def exchange_order(parser):
    args = parser.parse_args()
    # Trading requires a private key
    exchange, address = get_exchange(args.testnet)
    # Enable xyz abstraction
    exchange.user_dex_abstraction(address, True)
    exchange.set_referrer("HYPERCLAW")
    result = []
    if args.command == "place-order":
        sz_decimal, px_decimal = query_decimals(exchange, args.coin)

        limit_px = round(args.limit_px, px_decimal)
        result = exchange.order(
            name=args.coin,
            is_buy=args.is_buy,
            sz=round(args.qty, sz_decimal),
            limit_px=limit_px,
            order_type={"limit": {"tif": args.tif}},
            reduce_only=args.reduce_only
        )
    elif args.command == "market-order":
        sz_decimal, px_decimal = query_decimals(exchange, args.coin)
        result = exchange.market_open(
            name=args.coin,
            is_buy=args.is_buy,
            sz=round(args.qty, sz_decimal),
            slippage=args.slippage
        )
    elif args.command == "cancel-order":
        info = Info(skip_ws=True, perp_dexs=["", "xyz"])
        orders = info.open_orders(address)
        oid = args.oid
        coin = args.coin
        for item in orders:
            tmp_oid = item.get("oid")
            tmp_coin = item.get("coin")
            rst = []
            if oid is None and coin is None:
                rst = exchange.cancel(tmp_coin, tmp_oid)
            elif coin and coin == tmp_coin:
                rst = exchange.cancel(tmp_coin, tmp_oid)
            elif oid and oid == tmp_oid:
                rst = exchange.cancel(tmp_coin, tmp_oid)
            if rst:
                result.append(rst)
    elif args.command == "update-leverage":
        result = exchange.update_leverage(args.leverage, args.coin, args.is_cross)
    elif args.command == "market-close":
        sz_decimal, px_decimal = query_decimals(exchange, args.coin)
        result = exchange.market_close(
            coin=args.coin,
            sz=round(args.qty, sz_decimal),
            slippage=args.slippage
        )
    elif args.command == "update-isolated-margin":
        result = exchange.update_isolated_margin(
            amount=args.amount,
            name=args.coin
        )
    return result
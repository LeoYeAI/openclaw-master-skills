#!/usr/bin/env python3
"""
WEEX Futures API Client

Usage:
    python weex_client.py <command> [options]

Commands:
    time            Get server time
    ticker SYMBOL   Get ticker price
    depth SYMBOL    Get order book
    assets          Get account assets
    positions       Get all positions
    orders          Get open orders
    order ORDER_ID  Get order details

    buy SYMBOL SIZE [PRICE]     Open long position
    sell SYMBOL SIZE [PRICE]    Open short position
    close_long SYMBOL SIZE      Close long position
    close_short SYMBOL SIZE     Close short position
    cancel ORDER_ID             Cancel order
    close_all                   Close all positions

    leverage SYMBOL LEVERAGE    Set leverage (1-125)

Examples:
    python weex_client.py ticker cmt_btcusdt
    python weex_client.py assets
    python weex_client.py buy cmt_btcusdt 10
    python weex_client.py buy cmt_btcusdt 10 95000
    python weex_client.py leverage cmt_btcusdt 20
"""

import hashlib
import hmac
import base64
import time
import json
import os
import sys
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


class WeexClient:
    def __init__(self):
        self.api_key = os.environ.get("WEEX_API_KEY", "")
        self.api_secret = os.environ.get("WEEX_API_SECRET", "")
        self.passphrase = os.environ.get("WEEX_PASSPHRASE", "")
        self.base_url = os.environ.get("WEEX_BASE_URL", "https://api-contract.weex.com")

        if not all([self.api_key, self.api_secret, self.passphrase]):
            print("Warning: WEEX_API_KEY, WEEX_API_SECRET, and WEEX_PASSPHRASE required for authenticated endpoints")

    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _get_headers(self, method: str, path: str, body: str = "") -> dict:
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, path, body)
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": self.passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }

    def _request(self, method: str, path: str, params: dict | None = None, body: dict | None = None, auth: bool = True) -> dict:
        url = f"{self.base_url}{path}"

        if params:
            url += "?" + urlencode(params)
            path += "?" + urlencode(params)

        body_str = json.dumps(body) if body else ""
        headers = self._get_headers(method, path, body_str) if auth else {"Content-Type": "application/json"}

        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, data=body_str)

        return response.json()

    # Market Data (No Auth)
    def get_time(self) -> dict:
        return self._request("GET", "/capi/v2/market/time", auth=False)

    def get_ticker(self, symbol: str) -> dict:
        return self._request("GET", "/capi/v2/market/ticker", {"symbol": symbol}, auth=False)

    def get_depth(self, symbol: str, limit: int = 15) -> dict:
        return self._request("GET", "/capi/v2/market/depth", {"symbol": symbol, "limit": limit}, auth=False)

    def get_funding_rate(self, symbol: str | None = None) -> dict:
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/capi/v2/market/currentFundRate", params, auth=False)

    # Account (Auth Required)
    def get_assets(self) -> dict:
        return self._request("GET", "/capi/v2/account/assets")

    def get_positions(self) -> dict:
        return self._request("GET", "/capi/v2/account/position/allPosition")

    def get_settings(self, symbol: str | None = None) -> dict:
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/capi/v2/account/settings", params)

    def set_leverage(self, symbol: str, leverage: int, margin_mode: int = 1) -> dict:
        body = {
            "symbol": symbol,
            "marginMode": margin_mode,
            "longLeverage": str(leverage),
            "shortLeverage": str(leverage)
        }
        return self._request("POST", "/capi/v2/account/leverage", body=body)

    # Orders
    def get_open_orders(self, symbol: str | None = None) -> dict:
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/capi/v2/order/current", params)

    def get_order(self, order_id: str) -> dict:
        return self._request("GET", "/capi/v2/order/detail", {"orderId": order_id})

    def place_order(self, symbol: str, size: str, order_type: str, price: str = "0",
                    execution_type: str = "0", match_price: str = "1", margin_mode: int = 1) -> dict:
        """
        order_type: 1=Open Long, 2=Open Short, 3=Close Long, 4=Close Short
        execution_type: 0=Normal, 1=Post-only, 2=FOK, 3=IOC
        match_price: 0=Limit, 1=Market
        """
        client_oid = f"order_{int(time.time() * 1000)}"
        body = {
            "symbol": symbol,
            "client_oid": client_oid,
            "size": str(size),
            "type": order_type,
            "order_type": execution_type,
            "match_price": match_price,
            "price": str(price),
            "marginMode": margin_mode
        }
        return self._request("POST", "/capi/v2/order/placeOrder", body=body)

    def cancel_order(self, order_id: str) -> dict:
        return self._request("POST", "/capi/v2/order/cancel_order", body={"orderId": order_id})

    def cancel_all_orders(self, symbol: str | None = None, cancel_type: str = "normal") -> dict:
        body: dict = {"cancelOrderType": cancel_type}
        if symbol:
            body["symbol"] = symbol
        return self._request("POST", "/capi/v2/order/cancelAllOrders", body=body)

    def close_all_positions(self, symbol: str | None = None) -> dict:
        body = {"symbol": symbol} if symbol else {}
        return self._request("POST", "/capi/v2/order/closePositions", body=body)

    # Convenience methods
    def buy(self, symbol: str, size: str, price: str | None = None) -> dict:
        if price:
            return self.place_order(symbol, size, "1", price, match_price="0")
        return self.place_order(symbol, size, "1")

    def sell(self, symbol: str, size: str, price: str | None = None) -> dict:
        if price:
            return self.place_order(symbol, size, "2", price, match_price="0")
        return self.place_order(symbol, size, "2")

    def close_long(self, symbol: str, size: str, price: str | None = None) -> dict:
        if price:
            return self.place_order(symbol, size, "3", price, match_price="0")
        return self.place_order(symbol, size, "3")

    def close_short(self, symbol: str, size: str, price: str | None = None) -> dict:
        if price:
            return self.place_order(symbol, size, "4", price, match_price="0")
        return self.place_order(symbol, size, "4")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    client = WeexClient()
    command = sys.argv[1].lower()

    try:
        if command == "time":
            result = client.get_time()
        elif command == "ticker":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "cmt_btcusdt"
            result = client.get_ticker(symbol)
        elif command == "depth":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "cmt_btcusdt"
            result = client.get_depth(symbol)
        elif command == "funding":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            result = client.get_funding_rate(symbol)
        elif command == "assets":
            result = client.get_assets()
        elif command == "positions":
            result = client.get_positions()
        elif command == "orders":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            result = client.get_open_orders(symbol)
        elif command == "order":
            order_id = sys.argv[2]
            result = client.get_order(order_id)
        elif command == "buy":
            symbol = sys.argv[2]
            size = sys.argv[3]
            price = sys.argv[4] if len(sys.argv) > 4 else None
            result = client.buy(symbol, size, price)
        elif command == "sell":
            symbol = sys.argv[2]
            size = sys.argv[3]
            price = sys.argv[4] if len(sys.argv) > 4 else None
            result = client.sell(symbol, size, price)
        elif command == "close_long":
            symbol = sys.argv[2]
            size = sys.argv[3]
            result = client.close_long(symbol, size)
        elif command == "close_short":
            symbol = sys.argv[2]
            size = sys.argv[3]
            result = client.close_short(symbol, size)
        elif command == "cancel":
            order_id = sys.argv[2]
            result = client.cancel_order(order_id)
        elif command == "cancel_all":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            result = client.cancel_all_orders(symbol)
        elif command == "close_all":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            result = client.close_all_positions(symbol)
        elif command == "leverage":
            symbol = sys.argv[2]
            leverage = int(sys.argv[3])
            result = client.set_leverage(symbol, leverage)
        elif command == "settings":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            result = client.get_settings(symbol)
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)

        print(json.dumps(result, indent=2))

    except IndexError:
        print(f"Missing required arguments for command: {command}")
        print(__doc__)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

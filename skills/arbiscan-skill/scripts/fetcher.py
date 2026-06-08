"""统一数据获取层 — 公开 API，无需 key"""

import time
import requests
from typing import Optional
from config import EXCHANGES, REQUEST_TIMEOUT, RATE_LIMIT_DELAY

_last_request_time = 0


def _rate_limit():
    """限频：请求间隔至少 RATE_LIMIT_DELAY 秒"""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def _get(url: str, params: Optional[dict] = None) -> Optional[dict]:
    """发起 GET 请求，返回 JSON 或 None"""
    _rate_limit()
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] 请求失败 {url}: {e}")
        return None


# ====== 资金费率 ======

def fetch_funding_rate_binance(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["binance"]
    url = cfg["futures_url"] + cfg["endpoints"]["funding_rate"]
    data = _get(url, {"symbol": cfg["swap_format"](symbol)})
    if data:
        return float(data.get("lastFundingRate", 0))
    return None


def fetch_funding_rate_bybit(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["bybit"]
    url = cfg["base_url"] + cfg["endpoints"]["funding_rate"]
    data = _get(url, {"category": "linear", "symbol": cfg["swap_format"](symbol)})
    if data and data.get("result", {}).get("list"):
        return float(data["result"]["list"][0].get("fundingRate", 0))
    return None


def fetch_funding_rate_okx(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["okx"]
    url = cfg["base_url"] + cfg["endpoints"]["funding_rate"]
    data = _get(url, {"instId": cfg["swap_format"](symbol)})
    if data and data.get("data"):
        return float(data["data"][0].get("fundingRate", 0))
    return None


def fetch_funding_rate_bitget(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["bitget"]
    url = cfg["base_url"] + cfg["endpoints"]["funding_rate"]
    data = _get(url, {"symbol": cfg["swap_format"](symbol), "productType": "USDT-FUTURES"})
    if data and data.get("data"):
        return float(data["data"][0].get("fundingRate", 0))
    return None


def fetch_all_funding_rates(symbol: str) -> dict:
    """获取某个 symbol 在所有交易所的资金费率"""
    fetchers = {
        "binance": fetch_funding_rate_binance,
        "bybit": fetch_funding_rate_bybit,
        "okx": fetch_funding_rate_okx,
        "bitget": fetch_funding_rate_bitget,
    }
    results = {}
    for exchange, fetcher in fetchers.items():
        rate = fetcher(symbol)
        if rate is not None:
            results[exchange] = rate
    return results


# ====== 现货行情 ======

def fetch_spot_ticker_binance(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["binance"]
    url = cfg["base_url"] + cfg["endpoints"]["spot_ticker"]
    data = _get(url, {"symbol": cfg["symbol_format"](symbol)})
    if data:
        return {"bid": float(data["bidPrice"]), "ask": float(data["askPrice"])}
    return None


def fetch_spot_ticker_bybit(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["bybit"]
    url = cfg["base_url"] + cfg["endpoints"]["spot_ticker"]
    data = _get(url, {"category": "spot", "symbol": cfg["symbol_format"](symbol)})
    if data and data.get("result", {}).get("list"):
        item = data["result"]["list"][0]
        return {"bid": float(item["bid1Price"]), "ask": float(item["ask1Price"])}
    return None


def fetch_spot_ticker_okx(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["okx"]
    url = cfg["base_url"] + cfg["endpoints"]["spot_ticker"]
    data = _get(url, {"instId": cfg["symbol_format"](symbol)})
    if data and data.get("data"):
        item = data["data"][0]
        return {"bid": float(item["bidPx"]), "ask": float(item["askPx"])}
    return None


def fetch_spot_ticker_bitget(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["bitget"]
    url = cfg["base_url"] + cfg["endpoints"]["spot_ticker"]
    # Bitget tickers 接口不支持单 symbol 过滤，需要遍历
    data = _get(url)
    if data and data.get("data"):
        sym = cfg["symbol_format"](symbol)
        for item in data["data"]:
            if item.get("symbol") == sym:
                return {"bid": float(item.get("bidPr", 0)), "ask": float(item.get("askPr", 0))}
    return None


def fetch_all_spot_tickers(symbol: str) -> dict:
    """获取某个 symbol 在所有交易所的现货 bid/ask"""
    fetchers = {
        "binance": fetch_spot_ticker_binance,
        "bybit": fetch_spot_ticker_bybit,
        "okx": fetch_spot_ticker_okx,
        "bitget": fetch_spot_ticker_bitget,
    }
    results = {}
    for exchange, fetcher in fetchers.items():
        ticker = fetcher(symbol)
        if ticker and ticker["bid"] > 0 and ticker["ask"] > 0:
            results[exchange] = ticker
    return results


# ====== 合约行情 ======

def fetch_futures_price_binance(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["binance"]
    url = cfg["futures_url"] + cfg["endpoints"]["futures_ticker"]
    data = _get(url, {"symbol": cfg["swap_format"](symbol)})
    if data:
        return float(data["price"])
    return None


def fetch_futures_price_bybit(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["bybit"]
    url = cfg["base_url"] + cfg["endpoints"]["futures_ticker"]
    data = _get(url, {"category": "linear", "symbol": cfg["swap_format"](symbol)})
    if data and data.get("result", {}).get("list"):
        return float(data["result"]["list"][0].get("lastPrice", 0))
    return None


def fetch_futures_price_okx(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["okx"]
    url = cfg["base_url"] + cfg["endpoints"]["futures_ticker"]
    data = _get(url, {"instId": cfg["swap_format"](symbol)})
    if data and data.get("data"):
        return float(data["data"][0].get("last", 0))
    return None


def fetch_futures_price_bitget(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["bitget"]
    url = cfg["base_url"] + cfg["endpoints"]["futures_ticker"]
    # Bitget tickers 接口不支持单 symbol 过滤，需要遍历
    data = _get(url, {"productType": "USDT-FUTURES"})
    if data and data.get("data"):
        sym = cfg["swap_format"](symbol)
        for item in data["data"]:
            if item.get("symbol") == sym:
                return float(item.get("lastPr", 0))
    return None


def fetch_all_futures_prices(symbol: str) -> dict:
    """获取某个 symbol 在所有交易所的合约价格"""
    fetchers = {
        "binance": fetch_futures_price_binance,
        "bybit": fetch_futures_price_bybit,
        "okx": fetch_futures_price_okx,
        "bitget": fetch_futures_price_bitget,
    }
    results = {}
    for exchange, fetcher in fetchers.items():
        price = fetcher(symbol)
        if price and price > 0:
            results[exchange] = price
    return results


# ====== 现货价格（简单版，用于期现基差） ======

def fetch_spot_price_binance(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["binance"]
    url = cfg["base_url"] + cfg["endpoints"]["spot_price"]
    data = _get(url, {"symbol": cfg["symbol_format"](symbol)})
    if data:
        return float(data["price"])
    return None


def fetch_spot_price_bybit(symbol: str) -> Optional[float]:
    ticker = fetch_spot_ticker_bybit(symbol)
    if ticker:
        return (ticker["bid"] + ticker["ask"]) / 2
    return None


def fetch_spot_price_okx(symbol: str) -> Optional[float]:
    ticker = fetch_spot_ticker_okx(symbol)
    if ticker:
        return (ticker["bid"] + ticker["ask"]) / 2
    return None


def fetch_spot_price_bitget(symbol: str) -> Optional[float]:
    ticker = fetch_spot_ticker_bitget(symbol)
    if ticker:
        return (ticker["bid"] + ticker["ask"]) / 2
    return None


def fetch_all_spot_prices(symbol: str) -> dict:
    """获取某个 symbol 在所有交易所的现货中间价"""
    fetchers = {
        "binance": fetch_spot_price_binance,
        "bybit": fetch_spot_price_bybit,
        "okx": fetch_spot_price_okx,
        "bitget": fetch_spot_price_bitget,
    }
    results = {}
    for exchange, fetcher in fetchers.items():
        price = fetcher(symbol)
        if price and price > 0:
            results[exchange] = price
    return results


# ====== 持仓量 (Open Interest) ======

def fetch_oi_binance(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["binance"]
    url = cfg["futures_url"] + cfg["endpoints"]["open_interest"]
    data = _get(url, {"symbol": cfg["swap_format"](symbol)})
    if data:
        return float(data.get("openInterest", 0))
    return None


def fetch_oi_bybit(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["bybit"]
    url = cfg["base_url"] + cfg["endpoints"]["open_interest"]
    data = _get(url, {"category": "linear", "symbol": cfg["swap_format"](symbol), "intervalTime": "5min"})
    if data and data.get("result", {}).get("list"):
        return float(data["result"]["list"][0].get("openInterest", 0))
    return None


def fetch_oi_okx(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["okx"]
    url = cfg["base_url"] + cfg["endpoints"]["open_interest"]
    data = _get(url, {"instType": "SWAP", "instId": cfg["swap_format"](symbol)})
    if data and data.get("data"):
        return float(data["data"][0].get("oi", 0))
    return None


def fetch_oi_bitget(symbol: str) -> Optional[float]:
    cfg = EXCHANGES["bitget"]
    url = cfg["base_url"] + cfg["endpoints"]["open_interest"]
    data = _get(url, {"productType": "USDT-FUTURES", "symbol": cfg["swap_format"](symbol)})
    if data and data.get("data"):
        oi_list = data["data"].get("openInterestList")
        if oi_list and len(oi_list) > 0:
            return float(oi_list[0].get("size", 0))
    return None


def fetch_all_open_interest(symbol: str) -> dict:
    """获取某个 symbol 在所有交易所的持仓量"""
    fetchers = {
        "binance": fetch_oi_binance,
        "bybit": fetch_oi_bybit,
        "okx": fetch_oi_okx,
        "bitget": fetch_oi_bitget,
    }
    results = {}
    for exchange, fetcher in fetchers.items():
        oi = fetcher(symbol)
        if oi and oi > 0:
            results[exchange] = oi
    return results


# ====== 24h 行情（价格变化 + 成交量） ======

def fetch_24h_ticker_binance(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["binance"]
    url = cfg["futures_url"] + cfg["endpoints"]["futures_24h"]
    data = _get(url, {"symbol": cfg["swap_format"](symbol)})
    if data:
        return {
            "exchange_name": cfg["name"],
            "last_price": float(data.get("lastPrice", 0)),
            "change_pct": float(data.get("priceChangePercent", 0)),
            "volume_usdt": float(data.get("quoteVolume", 0)),
        }
    return None


def fetch_24h_ticker_bybit(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["bybit"]
    url = cfg["base_url"] + cfg["endpoints"]["futures_ticker"]
    data = _get(url, {"category": "linear", "symbol": cfg["swap_format"](symbol)})
    if data and data.get("result", {}).get("list"):
        item = data["result"]["list"][0]
        price = float(item.get("lastPrice", 0))
        prev = float(item.get("prevPrice24h", 0))
        change_pct = ((price - prev) / prev * 100) if prev > 0 else 0
        return {
            "exchange_name": cfg["name"],
            "last_price": price,
            "change_pct": change_pct,
            "volume_usdt": float(item.get("turnover24h", 0)),
        }
    return None


def fetch_24h_ticker_okx(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["okx"]
    url = cfg["base_url"] + cfg["endpoints"]["futures_ticker"]
    data = _get(url, {"instId": cfg["swap_format"](symbol)})
    if data and data.get("data"):
        item = data["data"][0]
        last = float(item.get("last", 0))
        open24h = float(item.get("open24h", 0))
        change_pct = ((last - open24h) / open24h * 100) if open24h > 0 else 0
        return {
            "exchange_name": cfg["name"],
            "last_price": last,
            "change_pct": change_pct,
            "volume_usdt": float(item.get("volCcy24h", 0)),
        }
    return None


def fetch_24h_ticker_bitget(symbol: str) -> Optional[dict]:
    cfg = EXCHANGES["bitget"]
    url = cfg["base_url"] + cfg["endpoints"]["futures_ticker"]
    data = _get(url, {"productType": "USDT-FUTURES"})
    if data and data.get("data"):
        sym = cfg["swap_format"](symbol)
        for item in data["data"]:
            if item.get("symbol") == sym:
                return {
                    "exchange_name": cfg["name"],
                    "last_price": float(item.get("lastPr", 0)),
                    "change_pct": float(item.get("change24h", 0)) * 100,  # Bitget 返回小数形式
                    "volume_usdt": float(item.get("quoteVolume", 0)),
                }
    return None


def fetch_all_24h_tickers(symbol: str) -> dict:
    """获取某个 symbol 在所有交易所的 24h 行情"""
    fetchers = {
        "binance": fetch_24h_ticker_binance,
        "bybit": fetch_24h_ticker_bybit,
        "okx": fetch_24h_ticker_okx,
        "bitget": fetch_24h_ticker_bitget,
    }
    results = {}
    for exchange, fetcher in fetchers.items():
        data = fetcher(symbol)
        if data and data["last_price"] > 0:
            results[exchange] = data
    return results


# ====== 资金费率历史 ======

def fetch_funding_history(exchange: str, symbol: str, limit: int = 20) -> list:
    """获取某个交易所某个 symbol 的历史资金费率，返回费率列表（最新在前）"""
    cfg = EXCHANGES.get(exchange)
    if not cfg or "funding_history" not in cfg["endpoints"]:
        return []

    url = (cfg.get("futures_url") or cfg["base_url"]) + cfg["endpoints"]["funding_history"]

    if exchange == "binance":
        data = _get(url, {"symbol": cfg["swap_format"](symbol), "limit": limit})
        if data and isinstance(data, list):
            return [float(r["fundingRate"]) for r in reversed(data)]
    elif exchange == "bybit":
        data = _get(url, {"category": "linear", "symbol": cfg["swap_format"](symbol), "limit": limit})
        if data and data.get("result", {}).get("list"):
            return [float(r["fundingRate"]) for r in data["result"]["list"]]
    elif exchange == "okx":
        data = _get(url, {"instId": cfg["swap_format"](symbol), "limit": limit})
        if data and data.get("data"):
            return [float(r["fundingRate"]) for r in data["data"]]
    elif exchange == "bitget":
        data = _get(url, {"symbol": cfg["swap_format"](symbol), "productType": "USDT-FUTURES", "pageSize": limit})
        if data and data.get("data"):
            return [float(r["fundingRate"]) for r in data["data"]]

    return []


# ====== 多空比 ======

def fetch_long_short_ratio(exchange: str, symbol: str) -> Optional[dict]:
    """获取多空比，返回 {long_pct, short_pct}"""
    cfg = EXCHANGES.get(exchange)
    if not cfg or "long_short_ratio" not in cfg["endpoints"]:
        return None

    url = cfg.get("base_url", cfg.get("futures_url", "")) + cfg["endpoints"]["long_short_ratio"]

    if exchange == "binance":
        # Binance 的多空比端点在 fapi 域名下
        url = cfg["futures_url"] + cfg["endpoints"]["long_short_ratio"]
        data = _get(url, {"symbol": cfg["swap_format"](symbol), "period": "5m", "limit": 1})
        if data and isinstance(data, list) and len(data) > 0:
            ratio = float(data[0].get("longShortRatio", 1))
            long_pct = ratio / (1 + ratio) * 100
            short_pct = 100 - long_pct
            return {"long_pct": long_pct, "short_pct": short_pct}
    elif exchange == "bybit":
        data = _get(url, {"category": "linear", "symbol": cfg["swap_format"](symbol), "period": "1h", "limit": 1})
        if data and data.get("result", {}).get("list"):
            item = data["result"]["list"][0]
            buy_ratio = float(item.get("buyRatio", 0.5))
            sell_ratio = float(item.get("sellRatio", 0.5))
            total = buy_ratio + sell_ratio
            if total > 0:
                return {"long_pct": buy_ratio / total * 100, "short_pct": sell_ratio / total * 100}

    return None


# ====== 交易对列表 ======

def fetch_exchange_symbols(exchange: str) -> Optional[set]:
    """获取某交易所所有 USDT 交易对 symbol（如 BTCUSDT）"""
    cfg = EXCHANGES.get(exchange)
    if not cfg:
        return None

    if exchange == "binance":
        url = cfg["base_url"] + cfg["endpoints"]["exchange_info"]
        data = _get(url)
        if data and data.get("symbols"):
            return {s["symbol"] for s in data["symbols"] if s.get("quoteAsset") == "USDT" and s.get("status") == "TRADING"}
    elif exchange == "bybit":
        url = cfg["base_url"] + cfg["endpoints"]["instruments"]
        data = _get(url, {"category": "spot"})
        if data and data.get("result", {}).get("list"):
            return {s["symbol"] for s in data["result"]["list"] if s["symbol"].endswith("USDT") and s.get("status") == "Trading"}
    elif exchange == "okx":
        url = cfg["base_url"] + cfg["endpoints"]["instruments"]
        data = _get(url, {"instType": "SPOT"})
        if data and data.get("data"):
            return {s["instId"].replace("-", "") for s in data["data"] if s["instId"].endswith("-USDT") and s.get("state") == "live"}
    elif exchange == "bitget":
        url = cfg["base_url"] + cfg["endpoints"]["instruments"]
        data = _get(url)
        if data and data.get("data"):
            return {s["symbol"] for s in data["data"] if s["symbol"].endswith("USDT") and s.get("status") == "online"}

    return None

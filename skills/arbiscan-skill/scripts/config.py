"""交易所端点配置 + symbol 映射"""

# 默认 Top 30 交易对（按市值排序，用户可通过 Agent 指定扫描更多）
TOP_SYMBOLS = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "AVAX", "DOT", "LINK",
    "MATIC", "UNI", "LTC", "BCH", "NEAR", "APT", "OP", "ARB", "FIL", "ATOM",
    "ETC", "IMX", "INJ", "SEI", "SUI", "TIA", "JUP", "WLD", "PEPE", "WIF",
]

# 交易所配置
EXCHANGES = {
    "binance": {
        "name": "Binance",
        "base_url": "https://api.binance.com",
        "futures_url": "https://fapi.binance.com",
        "endpoints": {
            "funding_rate": "/fapi/v1/premiumIndex",
            "funding_history": "/fapi/v1/fundingRate",
            "spot_ticker": "/api/v3/ticker/bookTicker",
            "futures_ticker": "/fapi/v1/ticker/price",
            "futures_24h": "/fapi/v1/ticker/24hr",
            "spot_price": "/api/v3/ticker/price",
            "open_interest": "/fapi/v1/openInterest",
            "long_short_ratio": "/futures/data/globalLongShortAccountRatio",
            "exchange_info": "/api/v3/exchangeInfo",
        },
        "symbol_format": lambda base: f"{base}USDT",
        "swap_format": lambda base: f"{base}USDT",
        "funding_interval_hours": 8,
    },
    "bybit": {
        "name": "Bybit",
        "base_url": "https://api.bybit.com",
        "futures_url": "https://api.bybit.com",
        "endpoints": {
            "funding_rate": "/v5/market/tickers",
            "funding_history": "/v5/market/funding/history",
            "spot_ticker": "/v5/market/tickers",
            "futures_ticker": "/v5/market/tickers",
            "open_interest": "/v5/market/open-interest",
            "long_short_ratio": "/v5/market/account-ratio",
            "instruments": "/v5/market/instruments-info",
        },
        "symbol_format": lambda base: f"{base}USDT",
        "swap_format": lambda base: f"{base}USDT",
        "funding_interval_hours": 8,
    },
    "okx": {
        "name": "OKX",
        "base_url": "https://www.okx.com",
        "futures_url": "https://www.okx.com",
        "endpoints": {
            "funding_rate": "/api/v5/public/funding-rate",
            "funding_history": "/api/v5/public/funding-rate-history",
            "spot_ticker": "/api/v5/market/ticker",
            "futures_ticker": "/api/v5/market/ticker",
            "open_interest": "/api/v5/public/open-interest",
            "instruments": "/api/v5/public/instruments",
        },
        "symbol_format": lambda base: f"{base}-USDT",
        "swap_format": lambda base: f"{base}-USDT-SWAP",
        "funding_interval_hours": 8,
    },
    "bitget": {
        "name": "Bitget",
        "base_url": "https://api.bitget.com",
        "futures_url": "https://api.bitget.com",
        "endpoints": {
            "funding_rate": "/api/v2/mix/market/current-fund-rate",
            "funding_history": "/api/v2/mix/market/history-fund-rate",
            "spot_ticker": "/api/v2/spot/market/tickers",
            "futures_ticker": "/api/v2/mix/market/tickers",
            "open_interest": "/api/v2/mix/market/open-interest",
            "instruments": "/api/v2/spot/public/symbols",
        },
        "symbol_format": lambda base: f"{base}USDT",
        "swap_format": lambda base: f"{base}USDT",
        "funding_interval_hours": 8,
    },
}

# 请求配置
REQUEST_TIMEOUT = 10  # 秒
RATE_LIMIT_DELAY = 0.2  # 秒，请求间隔

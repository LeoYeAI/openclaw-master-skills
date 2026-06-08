"""稳定币脱锚监控 — 监测 USDC/DAI 等偏离 $1 的情况"""

from fetcher import _get
from formatter import format_output


# 稳定币监控对，path 用点号分隔访问嵌套 JSON
DEPEG_PAIRS = {
    "USDC": [
        {"exchange": "Binance", "url": "https://api.binance.com/api/v3/ticker/price", "params": {"symbol": "USDCUSDT"}, "path": "price"},
        {"exchange": "OKX", "url": "https://www.okx.com/api/v5/market/ticker", "params": {"instId": "USDC-USDT"}, "path": "data.0.last"},
        {"exchange": "Bybit", "url": "https://api.bybit.com/v5/market/tickers", "params": {"category": "spot", "symbol": "USDCUSDT"}, "path": "result.list.0.lastPrice"},
    ],
    "DAI": [
        {"exchange": "Binance", "url": "https://api.binance.com/api/v3/ticker/price", "params": {"symbol": "DAIUSDT"}, "path": "price"},
    ],
    "FDUSD": [
        {"exchange": "Binance", "url": "https://api.binance.com/api/v3/ticker/price", "params": {"symbol": "FDUSDUSDT"}, "path": "price"},
    ],
    "TUSD": [
        {"exchange": "Binance", "url": "https://api.binance.com/api/v3/ticker/price", "params": {"symbol": "TUSDUSDT"}, "path": "price"},
    ],
}


def _extract_price(data, path: str) -> float:
    """从嵌套 JSON 中按点号路径提取价格"""
    keys = path.split(".")
    val = data
    for k in keys:
        if val is None:
            print(f"  [WARN] 路径解析失败: {path}，在 key={k} 处为 None")
            return 0.0
        if isinstance(val, list):
            val = val[int(k)]
        elif isinstance(val, dict):
            val = val.get(k)
        else:
            print(f"  [WARN] 路径解析失败: {path}，在 key={k} 处类型异常: {type(val)}")
            return 0.0
    return float(val) if val else 0.0


def scan_stablecoin_depeg(threshold_pct: float = 0.1) -> tuple:
    """
    扫描稳定币脱锚情况
    threshold_pct: 偏离阈值百分比（默认 0.1%）
    返回 (rows, headers)
    """
    headers = ["Stablecoin", "Exchange", "Price (USDT)", "Depeg%", "Status"]
    rows = []

    print(f"[Stablecoin Depeg] 扫描稳定币脱锚...")
    for coin, sources in DEPEG_PAIRS.items():
        for src in sources:
            data = _get(src["url"], src["params"])
            if data is None:
                continue

            price = _extract_price(data, src["path"])
            if price <= 0:
                continue

            depeg_pct = (price - 1.0) * 100
            if abs(depeg_pct) >= threshold_pct:
                status = "DEPEGGED" if abs(depeg_pct) > 0.5 else "WATCH"
            else:
                status = "STABLE"

            rows.append([
                coin,
                src["exchange"],
                f"${price:.6f}",
                f"{depeg_pct:+.4f}%",
                status,
            ])

    rows.sort(key=lambda r: abs(float(r[3].rstrip('%'))), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stablecoin Depeg Monitor")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_stablecoin_depeg()
    print(f"\n{'='*80}")
    print("  Stablecoin Depeg Monitor")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nMonitoring {len(rows)} stablecoin pairs")


if __name__ == "__main__":
    main()

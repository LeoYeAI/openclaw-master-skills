"""多空比扫描 — 散户情绪一边倒时的反向信号"""

from config import TOP_SYMBOLS
from fetcher import fetch_long_short_ratio
from formatter import format_output


def scan_long_short_ratio(symbols: list = None, min_ratio_pct: float = 60) -> tuple:
    """扫描多空比极端值"""
    if symbols is None:
        symbols = TOP_SYMBOLS[:30]  # 多空比查询较慢，默认 Top 30

    headers = ["Symbol", "Exchange", "Long%", "Short%", "Ratio", "Signal"]
    rows = []

    print(f"[Long/Short Ratio] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        # Binance 和 Bybit 有公开多空比端点
        for exchange in ["binance", "bybit"]:
            data = fetch_long_short_ratio(exchange, symbol)
            if data is None:
                continue

            long_pct = data["long_pct"]
            short_pct = data["short_pct"]

            # 只标记极端情况
            if max(long_pct, short_pct) < min_ratio_pct:
                continue

            ratio = long_pct / short_pct if short_pct > 0 else float('inf')

            if long_pct > 75:
                signal = "EXTREME LONG - reversal risk"
            elif long_pct > 65:
                signal = "LONG HEAVY"
            elif short_pct > 75:
                signal = "EXTREME SHORT - squeeze risk"
            elif short_pct > 65:
                signal = "SHORT HEAVY"
            else:
                signal = "MODERATE"

            from config import EXCHANGES
            rows.append([
                f"{symbol}USDT",
                EXCHANGES[exchange]["name"],
                f"{long_pct:.1f}%",
                f"{short_pct:.1f}%",
                f"{ratio:.2f}",
                signal,
            ])

    rows.sort(key=lambda r: max(float(r[2].rstrip('%')), float(r[3].rstrip('%'))), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Long/Short Ratio Scanner")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_long_short_ratio()
    print(f"\n{'='*80}")
    print("  Long/Short Ratio")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} extreme ratios")


if __name__ == "__main__":
    main()

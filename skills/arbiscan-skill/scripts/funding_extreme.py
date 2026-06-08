"""资金费率异常警报 — 费率 > ±0.1% 的极端情况"""

from config import TOP_SYMBOLS, EXCHANGES
from fetcher import fetch_all_funding_rates
from formatter import format_output


# 正常费率约 ±0.01%，超过 ±0.1% 算极端
EXTREME_THRESHOLD = 0.001  # 0.1%


def scan_funding_extreme(symbols: list = None) -> tuple:
    """扫描资金费率极端值"""
    if symbols is None:
        symbols = TOP_SYMBOLS

    headers = ["Symbol", "Exchange", "Rate", "Multiple", "Direction", "Signal"]
    rows = []

    print(f"[Funding Extreme] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        rates = fetch_all_funding_rates(symbol)
        for exchange, rate in rates.items():
            if abs(rate) < EXTREME_THRESHOLD:
                continue

            # 正常费率 0.01%，计算是正常的多少倍
            multiple = abs(rate) / 0.0001
            direction = "LONG CROWDED" if rate > 0 else "SHORT CROWDED"
            # 极端费率意味着反方向可能有机会
            signal = "Potential SHORT squeeze" if rate < 0 else "Potential LONG squeeze"

            rows.append([
                f"{symbol}USDT",
                EXCHANGES[exchange]["name"],
                f"{rate*100:.4f}%",
                f"{multiple:.1f}x",
                direction,
                signal,
            ])

    rows.sort(key=lambda r: float(r[3].rstrip('x')), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Funding Rate Extreme Alert")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_funding_extreme()
    print(f"\n{'='*80}")
    print("  Funding Rate Extreme Alert")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} extreme rates")


if __name__ == "__main__":
    main()

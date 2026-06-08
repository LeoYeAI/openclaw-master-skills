"""资金费率历史趋势 — 找持续同方向费率的稳定套利机会"""

from config import TOP_SYMBOLS, EXCHANGES
from fetcher import fetch_funding_history
from formatter import format_output


def scan_funding_history(symbols: list = None, min_streak: int = 5) -> tuple:
    """扫描资金费率历史趋势，找连续同方向的币种"""
    if symbols is None:
        symbols = TOP_SYMBOLS[:30]  # 历史费率查询较慢，默认 Top 30

    headers = ["Symbol", "Exchange", "Streak", "Direction", "Avg Rate", "Est. APY%", "Stability"]
    rows = []

    print(f"[Funding History] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        for exchange in ["binance", "bybit", "okx"]:
            rates = fetch_funding_history(exchange, symbol, limit=20)
            if len(rates) < min_streak:
                continue

            # 计算连续同方向的长度
            streak = 1
            direction = "POSITIVE" if rates[0] > 0 else "NEGATIVE"
            for i in range(1, len(rates)):
                if (rates[i] > 0) == (rates[0] > 0):
                    streak += 1
                else:
                    break

            if streak < min_streak:
                continue

            avg_rate = sum(rates[:streak]) / streak
            interval = EXCHANGES[exchange]["funding_interval_hours"]
            apy = avg_rate * (365 * 24 / interval) * 100

            if streak >= 15:
                stability = "VERY STABLE"
            elif streak >= 10:
                stability = "STABLE"
            else:
                stability = "EMERGING"

            rows.append([
                f"{symbol}USDT",
                EXCHANGES[exchange]["name"],
                f"{streak} periods",
                direction,
                f"{avg_rate*100:.4f}%",
                f"{apy:.1f}%",
                stability,
            ])

    rows.sort(key=lambda r: int(r[2].split()[0]), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Funding Rate History Trend")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    parser.add_argument("--min-streak", type=int, default=5, help="最小连续期数")
    args = parser.parse_args()

    rows, headers = scan_funding_history(min_streak=args.min_streak)
    print(f"\n{'='*80}")
    print("  Funding Rate History Trend")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} trending symbols")


if __name__ == "__main__":
    main()

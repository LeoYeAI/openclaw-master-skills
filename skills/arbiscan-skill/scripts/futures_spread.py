"""跨所合约价差扫描 — 合约端的搬砖机会"""

from itertools import combinations
from config import TOP_SYMBOLS, EXCHANGES
from fetcher import fetch_all_futures_prices
from formatter import format_output, risk_level


def scan_futures_spread(symbols: list = None, min_spread_pct: float = 0.03) -> tuple:
    """扫描跨所合约价差"""
    if symbols is None:
        symbols = TOP_SYMBOLS

    headers = ["Symbol", "Buy From", "Sell To", "Low Price", "High Price", "Spread%", "Risk"]
    rows = []

    print(f"[Futures Spread] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        prices = fetch_all_futures_prices(symbol)
        if len(prices) < 2:
            continue

        for ex_a, ex_b in combinations(prices.keys(), 2):
            pa, pb = prices[ex_a], prices[ex_b]
            if pa <= 0 or pb <= 0:
                continue

            low_ex, high_ex = (ex_a, ex_b) if pa < pb else (ex_b, ex_a)
            low_p, high_p = min(pa, pb), max(pa, pb)
            spread_pct = (high_p - low_p) / low_p * 100

            if spread_pct < min_spread_pct:
                continue

            risk = risk_level(spread_pct * 365, symbol)
            rows.append([
                f"{symbol}USDT",
                f"{EXCHANGES[low_ex]['name']} ${low_p:.4f}",
                f"{EXCHANGES[high_ex]['name']} ${high_p:.4f}",
                f"${low_p:.4f}",
                f"${high_p:.4f}",
                f"{spread_pct:.4f}%",
                risk,
            ])

    rows.sort(key=lambda r: float(r[5].rstrip('%')), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cross-Exchange Futures Spread Scanner")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_futures_spread()
    print(f"\n{'='*80}")
    print("  Cross-Exchange Futures Spread")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} opportunities")


if __name__ == "__main__":
    main()

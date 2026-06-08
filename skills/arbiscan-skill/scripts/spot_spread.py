"""跨所现货价差扫描 — best_bid vs best_ask 跨交易所比较"""

from itertools import combinations
from config import TOP_SYMBOLS, EXCHANGES
from fetcher import fetch_all_spot_tickers
from formatter import format_output, risk_level


def scan_spot_spread(symbols: list = None, min_spread_pct: float = 0.02) -> tuple:
    """
    扫描跨所现货价差套利机会
    返回 (rows, headers)
    """
    if symbols is None:
        symbols = TOP_SYMBOLS

    headers = ["Symbol", "Buy From", "Sell To", "Buy Ask", "Sell Bid", "Spread%", "Risk"]
    rows = []

    print(f"[Spot Spread] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        tickers = fetch_all_spot_tickers(symbol)
        if len(tickers) < 2:
            continue

        # 两两比较
        for ex_a, ex_b in combinations(tickers.keys(), 2):
            a, b = tickers[ex_a], tickers[ex_b]

            # 方向1: 在 A 买（ask），在 B 卖（bid）
            if b["bid"] > a["ask"] and a["ask"] > 0:
                spread_pct = (b["bid"] - a["ask"]) / a["ask"] * 100
                if spread_pct >= min_spread_pct:
                    risk = risk_level(spread_pct * 365, symbol)
                    rows.append([
                        f"{symbol}USDT",
                        f"{EXCHANGES[ex_a]['name']} ${a['ask']:.4f}",
                        f"{EXCHANGES[ex_b]['name']} ${b['bid']:.4f}",
                        f"${a['ask']:.4f}",
                        f"${b['bid']:.4f}",
                        f"{spread_pct:.4f}%",
                        risk,
                    ])

            # 方向2: 在 B 买（ask），在 A 卖（bid）
            if a["bid"] > b["ask"] and b["ask"] > 0:
                spread_pct = (a["bid"] - b["ask"]) / b["ask"] * 100
                if spread_pct >= min_spread_pct:
                    risk = risk_level(spread_pct * 365, symbol)
                    rows.append([
                        f"{symbol}USDT",
                        f"{EXCHANGES[ex_b]['name']} ${b['ask']:.4f}",
                        f"{EXCHANGES[ex_a]['name']} ${a['bid']:.4f}",
                        f"${b['ask']:.4f}",
                        f"${a['bid']:.4f}",
                        f"{spread_pct:.4f}%",
                        risk,
                    ])

    rows.sort(key=lambda r: float(r[5].rstrip('%')), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cross-Exchange Spot Spread Scanner")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_spot_spread()
    print(f"\n{'='*80}")
    print("  Cross-Exchange Spot Spread")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} opportunities")


if __name__ == "__main__":
    main()

"""24h 涨跌幅排行 — 暴涨暴跌币种检测"""

from config import TOP_SYMBOLS
from fetcher import fetch_all_24h_tickers
from formatter import format_output


def scan_price_movers(symbols: list = None, top_n: int = 20) -> tuple:
    """扫描 24h 涨跌幅最大的币种"""
    if symbols is None:
        symbols = TOP_SYMBOLS

    headers = ["Symbol", "Exchange", "Price", "24h Change%", "24h Volume (USDT)", "Direction"]
    all_rows = []

    print(f"[Price Movers] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        tickers = fetch_all_24h_tickers(symbol)
        for exchange, data in tickers.items():
            change_pct = data.get("change_pct", 0)
            volume = data.get("volume_usdt", 0)
            price = data.get("last_price", 0)

            if price <= 0:
                continue

            direction = "PUMP" if change_pct > 0 else "DUMP"
            all_rows.append([
                f"{symbol}USDT",
                data.get("exchange_name", exchange),
                f"${price:.4f}",
                f"{change_pct:+.2f}%",
                f"${volume:,.0f}",
                direction,
                abs(change_pct),  # 用于排序，不输出
            ])

    # 按绝对变化排序，取 top_n
    all_rows.sort(key=lambda r: r[6], reverse=True)
    # 去掉排序辅助列，去重（同一个币取变化最大的交易所）
    seen = set()
    rows = []
    for r in all_rows:
        sym = r[0]
        if sym not in seen:
            seen.add(sym)
            rows.append(r[:6])
        if len(rows) >= top_n:
            break

    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="24h Price Movers")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    parser.add_argument("--top", type=int, default=20, help="显示前 N 个")
    args = parser.parse_args()

    rows, headers = scan_price_movers(top_n=args.top)
    print(f"\n{'='*80}")
    print("  24h Price Movers (Gainers & Losers)")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nTop {len(rows)} movers")


if __name__ == "__main__":
    main()

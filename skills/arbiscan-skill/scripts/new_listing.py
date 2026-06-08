"""新币上线检测 — A 所有 B 所没有，找溢价窗口"""

from fetcher import fetch_exchange_symbols
from formatter import format_output


def scan_new_listing() -> tuple:
    """比较各交易所交易对列表，找出独有的币种"""
    headers = ["Symbol", "Available On", "Missing From", "Exclusivity", "Signal"]
    rows = []

    print("[New Listing] 获取各交易所交易对列表...")
    all_symbols = {}
    for exchange in ["binance", "bybit", "okx", "bitget"]:
        symbols = fetch_exchange_symbols(exchange)
        if symbols:
            all_symbols[exchange] = symbols
            print(f"  {exchange}: {len(symbols)} pairs")

    if len(all_symbols) < 2:
        return rows, headers

    # 合并所有 symbol
    universe = set()
    for syms in all_symbols.values():
        universe.update(syms)

    from config import EXCHANGES

    for symbol in sorted(universe):
        present = [ex for ex in all_symbols if symbol in all_symbols[ex]]
        missing = [ex for ex in all_symbols if symbol not in all_symbols[ex]]

        # 只关注在 1-2 个交易所独有的
        if len(present) >= 3 or len(missing) == 0:
            continue

        present_names = ", ".join(EXCHANGES[ex]["name"] for ex in present)
        missing_names = ", ".join(EXCHANGES[ex]["name"] for ex in missing)
        exclusivity = f"{len(present)}/{len(all_symbols)}"

        if len(present) == 1:
            signal = "EXCLUSIVE - high premium potential"
        else:
            signal = "LIMITED - moderate premium"

        rows.append([
            symbol,
            present_names,
            missing_names,
            exclusivity,
            signal,
        ])

    # 按独有度排序（越少交易所有越前）
    rows.sort(key=lambda r: r[3])
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="New Listing Detection")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_new_listing()
    print(f"\n{'='*80}")
    print("  New Listing Detection")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} exclusive/limited listings")


if __name__ == "__main__":
    main()

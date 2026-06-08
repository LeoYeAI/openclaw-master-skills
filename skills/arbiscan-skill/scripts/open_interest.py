"""持仓量监控 — 跨所 OI 对比，发现异常堆积"""

from config import TOP_SYMBOLS, EXCHANGES
from fetcher import fetch_all_open_interest
from formatter import format_output


def scan_open_interest(symbols: list = None, top_n: int = 30) -> tuple:
    """扫描持仓量分布，找出 OI 集中度异常的币种"""
    if symbols is None:
        symbols = TOP_SYMBOLS[:top_n]  # OI 扫描默认 Top 30，节省时间

    headers = ["Symbol", "Total OI (USDT)", "Top Exchange", "Share%", "Status"]
    rows = []

    print(f"[Open Interest] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        oi_data = fetch_all_open_interest(symbol)
        if len(oi_data) < 2:
            continue

        total_oi = sum(oi_data.values())
        if total_oi <= 0:
            continue

        top_ex = max(oi_data, key=oi_data.get)
        top_share = oi_data[top_ex] / total_oi * 100

        if top_share > 60:
            status = "CONCENTRATED"
        elif top_share > 45:
            status = "MODERATE"
        else:
            status = "BALANCED"

        rows.append([
            f"{symbol}USDT",
            f"${total_oi:,.0f}",
            f"{EXCHANGES[top_ex]['name']} ({top_share:.1f}%)",
            f"{top_share:.1f}%",
            status,
        ])

    rows.sort(key=lambda r: float(r[3].rstrip('%')), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Open Interest Monitor")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    parser.add_argument("--top", type=int, default=30, help="扫描前 N 个币种")
    args = parser.parse_args()

    rows, headers = scan_open_interest(top_n=args.top)
    print(f"\n{'='*80}")
    print("  Open Interest Monitor")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nMonitoring {len(rows)} symbols")


if __name__ == "__main__":
    main()

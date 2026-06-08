"""成交量突变检测 — 发现量能异常放大的币"""

from config import TOP_SYMBOLS
from fetcher import fetch_all_24h_tickers
from formatter import format_output


def scan_volume_anomaly(symbols: list = None, top_n: int = 20) -> tuple:
    """扫描跨所成交量分布，找出某交易所量能异常集中的币种"""
    if symbols is None:
        symbols = TOP_SYMBOLS

    headers = ["Symbol", "Total Vol (USDT)", "Top Exchange", "Vol Share%", "24h Change%", "Signal"]
    rows = []

    print(f"[Volume Anomaly] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        tickers = fetch_all_24h_tickers(symbol)
        if len(tickers) < 2:
            continue

        # 汇总各所成交量
        volumes = {}
        change_pcts = {}
        for exchange, data in tickers.items():
            vol = data.get("volume_usdt", 0)
            if vol > 0:
                volumes[exchange] = vol
                change_pcts[exchange] = data.get("change_pct", 0)

        if len(volumes) < 2:
            continue

        total_vol = sum(volumes.values())
        if total_vol <= 0:
            continue

        top_ex = max(volumes, key=volumes.get)
        top_share = volumes[top_ex] / total_vol * 100
        avg_change = sum(change_pcts.values()) / len(change_pcts)

        # 判断信号
        if top_share > 70:
            signal = "VOLUME SPIKE"
        elif top_share > 50 and abs(avg_change) < 2:
            signal = "ACCUMULATION"
        elif abs(avg_change) > 10:
            signal = "MOMENTUM"
        else:
            signal = "NORMAL"

        if signal == "NORMAL":
            continue

        from config import EXCHANGES
        rows.append([
            f"{symbol}USDT",
            f"${total_vol:,.0f}",
            EXCHANGES[top_ex]["name"],
            f"{top_share:.1f}%",
            f"{avg_change:+.2f}%",
            signal,
        ])

    rows.sort(key=lambda r: float(r[3].rstrip('%')), reverse=True)
    return rows[:top_n], headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Volume Anomaly Detection")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    parser.add_argument("--top", type=int, default=20, help="显示前 N 个")
    args = parser.parse_args()

    rows, headers = scan_volume_anomaly(top_n=args.top)
    print(f"\n{'='*80}")
    print("  Volume Anomaly Detection")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} anomalies")


if __name__ == "__main__":
    main()

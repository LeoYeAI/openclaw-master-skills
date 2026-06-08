"""资金费率套利扫描"""

from config import TOP_SYMBOLS, EXCHANGES
from fetcher import fetch_all_funding_rates
from formatter import format_output, risk_level


def scan_funding_arbitrage(symbols: list = None, min_apy: float = 0) -> tuple:
    """
    扫描资金费率套利机会
    返回 (rows, headers)
    """
    if symbols is None:
        symbols = TOP_SYMBOLS

    headers = ["Symbol", "Long (低费率)", "Short (高费率)", "Rate Diff", "Est. APY%", "Risk", "Window"]
    rows = []

    print(f"[Funding Rate] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        rates = fetch_all_funding_rates(symbol)
        if len(rates) < 2:
            continue

        # 找最低和最高费率
        min_ex = min(rates, key=rates.get)
        max_ex = max(rates, key=rates.get)
        diff = rates[max_ex] - rates[min_ex]

        if diff <= 0:
            continue

        # 年化计算：rate_diff * (365 * 24 / interval_hours) * 100
        interval = EXCHANGES[min_ex]["funding_interval_hours"]
        apy = diff * (365 * 24 / interval) * 100

        if apy < min_apy:
            continue

        risk = risk_level(apy, symbol)
        rows.append([
            f"{symbol}USDT",
            f"{EXCHANGES[min_ex]['name']} {rates[min_ex]*100:.4f}%",
            f"{EXCHANGES[max_ex]['name']} {rates[max_ex]*100:.4f}%",
            f"{diff*100:.4f}%",
            f"{apy:.1f}%",
            risk,
            f"~{interval}h",
        ])

    # 按年化降序排列
    rows.sort(key=lambda r: float(r[4].rstrip('%')), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Funding Rate Arbitrage Scanner")
    parser.add_argument("--min-apy", type=float, default=0, help="最低年化过滤")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_funding_arbitrage(min_apy=args.min_apy)
    print(f"\n{'='*80}")
    print("  Funding Rate Arbitrage Opportunities")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} opportunities")


if __name__ == "__main__":
    main()

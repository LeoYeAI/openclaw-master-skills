"""期现基差套利扫描 — 同所 spot vs futures 价差"""

from config import TOP_SYMBOLS, EXCHANGES
from fetcher import fetch_all_spot_prices, fetch_all_futures_prices
from formatter import format_output, risk_level


def scan_basis_arbitrage(symbols: list = None, min_basis_pct: float = 0.05) -> tuple:
    """
    扫描期现基差套利机会
    返回 (rows, headers)
    """
    if symbols is None:
        symbols = TOP_SYMBOLS

    headers = ["Symbol", "Exchange", "Spot Price", "Futures Price", "Basis%", "Direction", "Risk"]
    rows = []

    print(f"[Basis Arb] 扫描 {len(symbols)} 个交易对...")
    for symbol in symbols:
        spot_prices = fetch_all_spot_prices(symbol)
        futures_prices = fetch_all_futures_prices(symbol)

        # 找同一交易所的期现价差
        common_exchanges = set(spot_prices.keys()) & set(futures_prices.keys())
        for exchange in common_exchanges:
            spot = spot_prices[exchange]
            futures = futures_prices[exchange]
            if spot == 0:
                continue

            basis_pct = (futures - spot) / spot * 100

            if abs(basis_pct) < min_basis_pct:
                continue

            direction = "Contango" if basis_pct > 0 else "Backwardation"
            risk = risk_level(abs(basis_pct) * 365, symbol)  # 粗略年化

            rows.append([
                f"{symbol}USDT",
                EXCHANGES[exchange]["name"],
                f"${spot:.2f}",
                f"${futures:.2f}",
                f"{basis_pct:.4f}%",
                direction,
                risk,
            ])

    rows.sort(key=lambda r: abs(float(r[4].rstrip('%'))), reverse=True)
    return rows, headers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Basis Arbitrage Scanner")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table")
    args = parser.parse_args()

    rows, headers = scan_basis_arbitrage()
    print(f"\n{'='*80}")
    print("  Basis Arbitrage (Spot vs Futures)")
    print(f"{'='*80}")
    print(format_output(rows, headers, args.format))
    print(f"\nFound {len(rows)} opportunities")


if __name__ == "__main__":
    main()

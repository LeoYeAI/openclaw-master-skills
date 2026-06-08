"""ArbiScan CLI 统一入口 — 12 种扫描"""

import argparse
import sys
import time
from datetime import datetime, timezone

from funding_arb import scan_funding_arbitrage
from basis_arb import scan_basis_arbitrage
from spot_spread import scan_spot_spread
from futures_spread import scan_futures_spread
from stablecoin_depeg import scan_stablecoin_depeg
from open_interest import scan_open_interest
from funding_extreme import scan_funding_extreme
from price_movers import scan_price_movers
from volume_anomaly import scan_volume_anomaly
from funding_history import scan_funding_history
from long_short_ratio import scan_long_short_ratio
from new_listing import scan_new_listing
from formatter import format_output


BANNER = """
    _          _     _ ____
   / \\   _ __ | |__ (_) ___|  ___ __ _ _ __
  / _ \\ | '__|| '_ \\| \\___ \\ / __/ _` | '_ \\
 / ___ \\| |   | |_) | |___) | (_| (_| | | | |
/_/   \\_\\_|   |_.__/|_|____/ \\___\\__,_|_| |_|

  Cross-Exchange Crypto Scanner & Monitor v0.2.0
  12 scan types. No trading. No API keys needed.
"""

# 扫描器注册表
SCANNERS = {
    # 套利类
    "funding": ("Funding Rate Arbitrage", scan_funding_arbitrage),
    "basis": ("Basis Arbitrage (Spot vs Futures)", scan_basis_arbitrage),
    "spread": ("Cross-Exchange Spot Spread", scan_spot_spread),
    "futures_spread": ("Cross-Exchange Futures Spread", scan_futures_spread),
    # 监控类
    "depeg": ("Stablecoin Depeg Monitor", scan_stablecoin_depeg),
    "open_interest": ("Open Interest Monitor", scan_open_interest),
    "funding_extreme": ("Funding Rate Extreme Alert", scan_funding_extreme),
    "price_movers": ("24h Price Movers", scan_price_movers),
    "volume_anomaly": ("Volume Anomaly Detection", scan_volume_anomaly),
    # 信号类
    "funding_history": ("Funding Rate History Trend", scan_funding_history),
    "long_short": ("Long/Short Ratio", scan_long_short_ratio),
    "new_listing": ("New Listing Detection", scan_new_listing),
}

SCAN_GROUPS = {
    "arbitrage": ["funding", "basis", "spread", "futures_spread"],
    "monitor": ["depeg", "open_interest", "funding_extreme", "price_movers", "volume_anomaly"],
    "signals": ["funding_history", "long_short", "new_listing"],
}


def run_scan(scan_type: str, fmt: str, min_apy: float):
    """运行指定类型的扫描"""
    if scan_type == "all":
        types_to_run = list(SCANNERS.keys())
    elif scan_type in SCAN_GROUPS:
        types_to_run = SCAN_GROUPS[scan_type]
    elif scan_type in SCANNERS:
        types_to_run = [scan_type]
    else:
        print(f"Unknown scan type: {scan_type}")
        print(f"Available: {', '.join(SCANNERS.keys())}")
        print(f"Groups: {', '.join(SCAN_GROUPS.keys())}, all")
        sys.exit(1)

    total_opps = 0
    for stype in types_to_run:
        title, scanner = SCANNERS[stype]
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}")

        if stype == "funding":
            rows, headers = scanner(min_apy=min_apy)
        else:
            rows, headers = scanner()

        print(format_output(rows, headers, fmt))
        print(f"  -> {len(rows)} results found\n")
        total_opps += len(rows)

    return total_opps


def main():
    all_types = list(SCANNERS.keys()) + list(SCAN_GROUPS.keys())
    parser = argparse.ArgumentParser(
        description="ArbiScan - Cross-Exchange Crypto Scanner & Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scan Types:
  Arbitrage:  funding, basis, spread, futures_spread
  Monitor:    depeg, open_interest, funding_extreme, price_movers, volume_anomaly
  Signals:    funding_history, long_short, new_listing

Groups:
  arbitrage   - run all arbitrage scans
  monitor     - run all monitoring scans
  signals     - run all signal scans
  all         - run everything

Examples:
  python scanner.py --all
  python scanner.py --type arbitrage
  python scanner.py --type funding --min-apy 10
  python scanner.py --type price_movers --format json
        """
    )
    parser.add_argument("--all", action="store_true", help="运行所有扫描类型")
    parser.add_argument("--type", choices=all_types, help="指定扫描类型或分组")
    parser.add_argument("--format", choices=["table", "markdown", "json"], default="table", help="输出格式")
    parser.add_argument("--min-apy", type=float, default=0, help="最低年化过滤（仅 funding 类型）")

    args = parser.parse_args()

    if not args.all and not args.type:
        parser.print_help()
        sys.exit(0)

    print(BANNER)
    print(f"  Scan started at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    scan_type = "all" if args.all else args.type
    start = time.time()
    total = run_scan(scan_type, args.format, args.min_apy)
    elapsed = time.time() - start

    print(f"{'='*80}")
    print(f"  Scan complete. {total} total results in {elapsed:.1f}s")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

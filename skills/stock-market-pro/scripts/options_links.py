#!/usr/bin/env python3
"""Print Unusual Whales links for a ticker.

This skill keeps options/flow analysis browser-first. This helper just prints
URLs so the agent/user can open them quickly.

Example:
- python3 scripts/options_links.py NVDA
"""

from __future__ import annotations

import argparse


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Unusual Whales links")
    p.add_argument("ticker", help="Ticker (e.g., NVDA, 000660.KS)")
    args = p.parse_args(argv)

    t = args.ticker
    print("Overview:")
    print(f"https://unusualwhales.com/stock/{t}/overview")
    print("Live options flow (ticker filter):")
    print(f"https://unusualwhales.com/live-options-flow?ticker_symbol={t}")
    print("Options flow history:")
    print(f"https://unusualwhales.com/stock/{t}/options-flow-history")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))

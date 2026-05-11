#!/usr/bin/env python3
"""
SEO-AGI Google Search Console data puller.
Retrieves query performance data and detects cannibalization.

Usage:
    python3 gsc_pull.py "<site_url>" [options]

Options:
    --keyword=KEYWORD       Filter queries containing this keyword
    --days=N                Lookback period (default: 90)
    --min-impressions=N     Minimum impressions threshold (default: 10)
    --output=FORMAT         Output: json|compact (default: compact)
    --cannibalization       Run cannibalization detection for the keyword
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.env import get_credentials
from lib.gsc_client import GSCClient


def parse_args():
    parser = argparse.ArgumentParser(description="SEO-AGI GSC Pull")
    parser.add_argument("site_url", help="GSC site URL (e.g., https://example.com)")
    parser.add_argument("--keyword", default=None, help="Keyword filter")
    parser.add_argument("--days", type=int, default=90, help="Lookback days")
    parser.add_argument("--min-impressions", type=int, default=10, help="Min impressions")
    parser.add_argument("--output", choices=["json", "compact"], default="compact")
    parser.add_argument("--cannibalization", action="store_true", help="Detect cannibalization")
    return parser.parse_args()


def format_compact(data: list[dict], mode: str = "performance") -> str:
    lines = []

    if mode == "cannibalization":
        lines.append("# Cannibalization Report")
        for item in data:
            lines.append(f"\nQuery: {item['query']} ({item['page_count']} pages, {item['total_impressions']} impressions)")
            for page in item["pages"]:
                lines.append(f"  pos {page['position']}: {page['page']} ({page['clicks']} clicks, {page['ctr']}% CTR)")
    else:
        lines.append("# Query Performance")
        lines.append(f"{'Query':<40} {'Clicks':>7} {'Impr':>7} {'CTR':>7} {'Pos':>5} Page")
        lines.append("-" * 110)
        for row in data[:50]:
            lines.append(
                f"{row['query'][:39]:<40} {row['clicks']:>7} {row['impressions']:>7} "
                f"{row['ctr']:>6.1f}% {row['position']:>5.1f} {row['page'][:50]}"
            )

    return "\n".join(lines)


def main():
    args = parse_args()
    creds = get_credentials()

    if not creds["has_gsc"]:
        print("ERROR: Google Search Console credentials not found.", file=sys.stderr)
        print("Add GSC_SERVICE_ACCOUNT_PATH to ~/.config/seo-agi/.env", file=sys.stderr)
        sys.exit(1)

    client = GSCClient(credentials_path=creds["gsc_service_account_path"])

    if args.cannibalization and args.keyword:
        data = client.detect_cannibalization(
            site_url=args.site_url,
            keyword=args.keyword,
            days=args.days,
        )
        if args.output == "json":
            print(json.dumps(data, indent=2))
        else:
            print(format_compact(data, mode="cannibalization"))
    else:
        data = client.query_performance(
            site_url=args.site_url,
            keyword=args.keyword,
            days=args.days,
            min_impressions=args.min_impressions,
        )
        if args.output == "json":
            print(json.dumps(data, indent=2))
        else:
            print(format_compact(data))


if __name__ == "__main__":
    main()

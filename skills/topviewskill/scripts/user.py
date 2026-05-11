#!/usr/bin/env python3
"""Query Topview account credit balance and usage history.

Usage:
    python user.py credit [--json]
    python user.py logs [--type TYPE] [--start TIME] [--end TIME] [--page N] [--size N] [--json]
"""

import argparse
import json as json_mod
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient

CREDIT_PATH = "/user/credit/detail"
LOGS_PATH = "/user/credit/logs"

TASK_TYPES = [
    "m2v",
    "common_task_image2video",
    "video_avatar",
    "product_avatar_image2video",
    "voice_clone",
    "product_anyfit",
    "pa_download_without_watermark",
    "pa2_replace_product_image",
    "pa2_image2video",
    "product_anyfit_v2_product_model",
]


def cmd_credit(client: TopviewClient, args):
    result = client.get(CREDIT_PATH)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        credit = result.get("credit", result)
        print(f"Credit balance: {credit}")


def cmd_logs(client: TopviewClient, args):
    params = {
        "pageNo": str(args.page),
        "pageSize": str(args.size),
    }
    if args.type:
        params["taskType"] = args.type
    if args.start:
        params["startTime"] = args.start
    if args.end:
        params["endTime"] = args.end

    result = client.get(LOGS_PATH, params=params)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    total = result.get("total", 0)
    data = result.get("data", [])
    page_no = result.get("pageNo", args.page)
    page_size = result.get("pageSize", args.size)

    if not args.quiet:
        print(
            f"Page {page_no} | {len(data)} items | {total} total",
            file=sys.stderr,
        )

    if not data:
        print("No records found.")
        return

    header = f"{'Date':<22} {'Type':<35} {'Cost':>8}  {'TaskId'}"
    print(header)
    print("-" * len(header))
    for entry in data:
        date = entry.get("date", "")[:19]
        task_type = entry.get("taskType", "")
        cost = entry.get("costCredit", 0)
        task_id = entry.get("taskId", "")
        print(f"{date:<22} {task_type:<35} {cost:>8}  {task_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Topview account credit management."
    )
    parser.add_argument("--json", action="store_true",
                        help="Output full JSON response")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress status messages on stderr")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("credit", help="Query credit balance")

    logs_p = sub.add_parser("logs", help="Query credit usage history")
    logs_p.add_argument("--type", default=None, choices=TASK_TYPES,
                        help="Filter by task type")
    logs_p.add_argument("--start", default=None,
                        help="UTC start time (yyyy-MM-dd HH:mm:ss)")
    logs_p.add_argument("--end", default=None,
                        help="UTC end time (yyyy-MM-dd HH:mm:ss)")
    logs_p.add_argument("--page", type=int, default=1,
                        help="Page number (default: 1)")
    logs_p.add_argument("--size", type=int, default=20,
                        help="Items per page (default: 20)")

    args = parser.parse_args()
    client = TopviewClient()

    if args.command == "credit":
        cmd_credit(client, args)
    elif args.command == "logs":
        cmd_logs(client, args)


if __name__ == "__main__":
    main()

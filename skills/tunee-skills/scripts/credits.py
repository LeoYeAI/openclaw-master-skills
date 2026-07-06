#!/usr/bin/env python3
"""
Tunee AI Music - Query remaining credits (Tunee points).
Prints API `data` as YAML to stdout for the agent to read.
"""

import argparse
import sys

import yaml

from utils import api_util


def main():
    parser = argparse.ArgumentParser(description="Tunee AI Music - Query remaining credits")
    parser.add_argument("--api-key", dest="api_key", default=None, help="API Key, or use env TUNEE_API_KEY")
    args = parser.parse_args()

    access_key = api_util.resolve_access_key(args.api_key)

    try:
        resp = api_util.fetch_credits(access_key)
    except api_util.TuneeAPIError as e:
        print(api_util.format_tunee_error(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Network request failed: {e}", file=sys.stderr)
        sys.exit(1)

    out = {"credits": resp.data}
    print(yaml.dump(out, allow_unicode=True, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()

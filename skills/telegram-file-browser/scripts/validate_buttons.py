#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from send_plan import build_message_payload


def load_plan(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", help="Path to plan JSON, or - to read from stdin")
    args = ap.parse_args()

    result = build_message_payload(load_plan(args.plan))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Standalone FIT parser CLI: parse_fit.py path/to/ride.fit [--summary-only]."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import fit_parser  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Parse a FIT file to JSON")
    p.add_argument("fit", help="Path to .fit file")
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args()

    out = fit_parser.parse(args.fit)
    if args.summary_only:
        out = {"summary": out["summary"]}
    json.dump(out, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

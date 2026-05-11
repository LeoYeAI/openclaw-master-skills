#!/usr/bin/env python3
"""
Generate a standard bug-fix report template.
Outputs Markdown to stdout or a file.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import textwrap

TEMPLATE = """
## Triage Summary
- Entry point:
- Final outcome:
- Classification:
- Severity:
- Evidence captured:
- Working hypothesis:
- Next step:

## Repro & Baseline Evidence
- Commands/steps:
- Observed behavior:

## Scope Discovery Summary
- Impacted modules:
- Impacted files (by type):
- Key symbols + references:

## Root Cause (1 sentence)

## Impact Analysis (5 layers)

## Fix Plan

## Fix Summary (minimal)

## Verification (matrix + evidence)

## Code Review Notes

## Similar Bug Hunt (query + results)

## Tooling Scripts
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a bug-fix report template as Markdown."
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write the template to a file instead of stdout.",
    )
    args = parser.parse_args()

    content = textwrap.dedent(TEMPLATE).strip() + "\n"

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Wrote template to {args.output}")
        return 0

    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

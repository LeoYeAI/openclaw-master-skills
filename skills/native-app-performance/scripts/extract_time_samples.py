#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export time-sample XML from a .trace file.")
    parser.add_argument("--trace", required=True, help="Path to .trace bundle")
    parser.add_argument("--output", required=True, help="Output XML path")
    args = parser.parse_args()

    trace = Path(args.trace)
    output = Path(args.output)

    if not trace.exists():
        raise SystemExit(f"trace not found: {trace}")

    # xctrace export needs an XPath into the trace table-of-contents. The schema
    # name 'time-sample' is stable for Time Profiler sample tables.
    xpath = '/trace-toc/run[@number="1"]/data/table[@schema="time-sample"]'

    cmd = [
        "xcrun",
        "xctrace",
        "export",
        "--input",
        str(trace),
        "--xpath",
        xpath,
        "--output",
        str(output),
    ]

    subprocess.check_call(cmd)

    if not output.exists():
        raise SystemExit(f"export failed: {output} missing")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

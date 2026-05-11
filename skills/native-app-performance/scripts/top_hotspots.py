#!/usr/bin/env python3
import argparse
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


def parse_text_vmsize(binary: Path) -> int:
    # otool -l provides __TEXT vmsize; we need it to cap the address range.
    out = subprocess.check_output(["otool", "-l", str(binary)], text=True)
    lines = out.splitlines()
    in_text = False
    for i, line in enumerate(lines):
        if line.strip() == "segname __TEXT":
            in_text = True
        if in_text and line.strip().startswith("vmsize"):
            _, size_hex = line.strip().split()
            return int(size_hex, 16)
        # Stop scanning once we leave the __TEXT section block
        if in_text and line.strip().startswith("segname") and line.strip() != "segname __TEXT":
            in_text = False
    raise SystemExit("Could not find __TEXT vmsize via otool -l")


def load_callstacks(samples_xml: Path) -> List[int]:
    root = ET.parse(samples_xml).getroot()

    # kperf-bt entries are referenced by id/ref; build a map first.
    bt_by_id: Dict[str, List[int]] = {}
    for bt in root.findall('.//kperf-bt'):
        bid = bt.get('id')
        text_addrs = bt.find('text-addresses')
        if bid and text_addrs is not None and text_addrs.text:
            # Addresses are space-separated decimal strings.
            addrs = [int(x) for x in text_addrs.text.strip().split() if x.strip().isdigit()]
            bt_by_id[bid] = addrs

    addrs: List[int] = []
    for row in root.findall('.//row'):
        bt = row.find('kperf-bt')
        if bt is None:
            continue
        ref = bt.get('ref')
        if ref and ref in bt_by_id:
            addrs.extend(bt_by_id[ref])
        else:
            bid = bt.get('id')
            if bid and bid in bt_by_id:
                addrs.extend(bt_by_id[bid])

    return addrs


def chunked(items: List[str], size: int) -> List[List[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def symbolicate(binary: Path, load_addr: str, addrs: List[int]) -> List[str]:
    # atos can take multiple addresses; chunk to avoid arg limits on large traces.
    addr_hex = [hex(a) for a in addrs]
    symbols: List[str] = []
    for chunk in chunked(addr_hex, 80):
        cmd = ["xcrun", "atos", "-o", str(binary), "-l", load_addr] + chunk
        symbols.extend(subprocess.check_output(cmd, text=True).splitlines())
    return symbols


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank top hotspots from Time Profiler samples.")
    parser.add_argument("--samples", required=True, help="time-sample XML from extract_time_samples.py")
    parser.add_argument("--binary", required=True, help="Path to app binary")
    parser.add_argument("--load-address", required=True, help="Runtime __TEXT load address (from vmmap)")
    parser.add_argument("--top", type=int, default=30, help="Top N symbols")
    args = parser.parse_args()

    samples_xml = Path(args.samples)
    binary = Path(args.binary)
    load_addr = args.load_address

    if not samples_xml.exists():
        raise SystemExit(f"samples not found: {samples_xml}")
    if not binary.exists():
        raise SystemExit(f"binary not found: {binary}")

    vmsize = parse_text_vmsize(binary)
    base = int(load_addr, 16)
    end = base + vmsize

    addrs = load_callstacks(samples_xml)
    counts = Counter(addrs)

    # Filter to app addresses only, using runtime load address + __TEXT size.
    app_counts = Counter({a: c for a, c in counts.items() if base <= a <= end})

    top = app_counts.most_common(args.top)
    if not top:
        print("No app frames found; check load address and binary match.")
        return 0

    addrs_only = [a for a, _ in top]
    symbols = symbolicate(binary, load_addr, addrs_only)

    print("address,count,symbol")
    for (addr, count), symbol in zip(top, symbols):
        print(f"{hex(addr)},{count},{symbol}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

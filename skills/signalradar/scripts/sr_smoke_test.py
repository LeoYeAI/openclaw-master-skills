#!/usr/bin/env python3
"""Smoke test for SignalRadar v0.5.0 runtime connectivity.

Runs:
1) signalradar.py doctor --output json → HEALTHY
2) signalradar.py run --dry-run --output json --yes → valid JSON with status field

Pass condition: both exit 0 and return valid output.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _find_cli_script() -> str:
    """Locate signalradar.py."""
    # Sibling in same directory
    here = Path(__file__).resolve().parent
    candidate = here / "signalradar.py"
    if candidate.is_file():
        return str(candidate)
    raise FileNotFoundError(f"signalradar.py not found in {here}")


def run_command(cmd: list[str], timeout_sec: int) -> tuple[bool, str]:
    """Run a command and return (ok, full_stdout)."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, check=False)
        if proc.returncode != 0:
            return False, ((proc.stderr or "") + (proc.stdout or ""))[-500:]
        return True, (proc.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="SignalRadar smoke test")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per command")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    cli = _find_cli_script()
    results: dict[str, dict[str, Any]] = {}
    all_ok = True

    # Test 1: doctor
    ok, stdout = run_command([sys.executable, cli, "doctor", "--output", "json"], args.timeout)
    entry: dict[str, Any] = {"status": "ok" if ok else "error"}
    if ok:
        try:
            payload = json.loads(stdout)
            if payload.get("status") != "HEALTHY":
                ok = False
                entry["error"] = f"doctor status: {payload.get('status')}"
        except json.JSONDecodeError as e:
            ok = False
            entry["error"] = f"invalid JSON: {e}"
    else:
        entry["error"] = stdout[-500:]
    results["doctor"] = entry
    if not ok:
        all_ok = False

    # Test 2: run --dry-run --yes --output json
    ok, stdout = run_command(
        [sys.executable, cli, "--yes", "run", "--dry-run", "--output", "json"],
        args.timeout + 30,
    )
    entry = {"status": "ok" if ok else "error"}
    if ok:
        try:
            payload = json.loads(stdout)
            st = payload.get("status", "")
            if st not in ("NO_REPLY", "HIT"):
                ok = False
                entry["error"] = f"unexpected run status: {st}"
        except json.JSONDecodeError as e:
            ok = False
            entry["error"] = f"invalid JSON: {e}"
    else:
        entry["error"] = stdout[-500:]
    results["run_dry"] = entry
    if not ok:
        all_ok = False

    out = {"ok": all_ok, "results": results}
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        label = "SMOKE_OK" if all_ok else "SMOKE_FAIL"
        parts = " ".join(f"{k}={v.get('status')}" for k, v in results.items())
        print(f"{label} {parts}")
        if not all_ok:
            for k, v in results.items():
                if v.get("error"):
                    print(f"  - {k}: {v['error']}")
    return 0 if all_ok else 3


if __name__ == "__main__":
    sys.exit(main())

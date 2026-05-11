#!/usr/bin/env python3
"""Prepublish gate for SignalRadar v0.5.3.

Verifies SignalRadar is in a publishable state:
1) Package hygiene (no internal docs, no personal paths)
2) doctor → HEALTHY
3) run --dry-run --yes --output json → valid output contract
4) Document consistency (negative + positive assertions)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _find_skill_dir() -> Path:
    """Locate the signalradar skill directory."""
    return Path(__file__).resolve().parent.parent


def _find_cli_script() -> str:
    return str(Path(__file__).resolve().parent / "signalradar.py")


def run_doctor(timeout_sec: int) -> tuple[bool, dict[str, Any]]:
    cli = _find_cli_script()
    cmd = [sys.executable, cli, "doctor", "--output", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, check=False)
        if proc.returncode != 0:
            return False, {"status": "error", "error": ((proc.stderr or "") + (proc.stdout or ""))[-500:]}
        payload = json.loads((proc.stdout or "").strip() or "{}")
        ok = str(payload.get("status", "")).upper() == "HEALTHY"
        return ok, {"status": "ok" if ok else "warn", "payload": payload}
    except Exception as exc:
        return False, {"status": "error", "error": str(exc)}


def run_dry(timeout_sec: int) -> tuple[bool, dict[str, Any]]:
    cli = _find_cli_script()
    cmd = [sys.executable, cli, "--yes", "run", "--dry-run", "--output", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, check=False)
        stdout = (proc.stdout or "").strip()
        # Parse JSON output — we accept any valid structured output
        # even if returncode != 0 (e.g. partial API errors)
        try:
            payload = json.loads(stdout or "{}")
        except json.JSONDecodeError:
            return False, {"status": "error", "error": f"invalid JSON output (rc={proc.returncode})"}
        st = str(payload.get("status", ""))
        # Frozen contract: status must be one of these
        if st not in ("NO_REPLY", "HIT", "ERROR"):
            return False, {"status": "error", "error": f"invalid run status: {st}"}
        # Check frozen fields exist
        for field in ("status", "request_id", "ts", "hits", "errors"):
            if field not in payload:
                return False, {"status": "error", "error": f"missing frozen field: {field}"}
        return True, {"status": "ok", "run_status": st}
    except subprocess.TimeoutExpired:
        return False, {"status": "error", "error": "timeout"}
    except Exception as exc:
        return False, {"status": "error", "error": str(exc)}


def check_package_hygiene() -> tuple[bool, dict[str, Any]]:
    """Check published skill directory for internal/private files."""
    skill_dir = _find_skill_dir()
    if not skill_dir.is_dir():
        return False, {"status": "error", "error": f"skill dir not found: {skill_dir}"}

    issues: list[str] = []

    # Disallowed directories
    for d in ["dev-docs", "session_logs"]:
        p = skill_dir / d
        if p.is_dir():
            files = list(p.glob("*.md"))
            if files:
                issues.append(f"directory '{d}/' contains {len(files)} files")

    # References internal docs check
    refs = skill_dir / "references"
    if refs.is_dir():
        for f in refs.iterdir():
            if not f.is_file():
                continue
            for pattern in ["devspec", "runbook", "checklist", "publishing_guide", "lesson"]:
                if pattern in f.name.lower():
                    issues.append(f"references/{f.name} looks like internal dev doc")

    # Sensitive path scan
    skip_dirs = {"__pycache__", ".git", "cache", "node_modules"}
    self_name = Path(__file__).name
    for root_path, dirs, filenames in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in filenames:
            if fname == self_name:
                continue
            if not fname.endswith((".py", ".sh", ".md", ".json")):
                continue
            fpath = Path(root_path) / fname
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = fpath.relative_to(skill_dir)
            for personal_prefix in ["/Users/", "/home/"]:
                if personal_prefix in content:
                    issues.append(f"{rel}: contains personal path ({personal_prefix})")

    if issues:
        return False, {"status": "fail", "issues": issues}
    return True, {"status": "ok"}


def check_doc_consistency() -> tuple[bool, dict[str, Any]]:
    """Check document consistency: negative assertions (old wording removed) + positive assertions."""
    skill_dir = _find_skill_dir()
    issues: list[str] = []

    def _file_contains(rel_path: str, needle: str) -> bool:
        fp = skill_dir / rel_path
        if not fp.exists():
            return False
        try:
            return needle in fp.read_text(encoding="utf-8")
        except OSError:
            return False

    # --- Negative assertions (must NOT contain old wording) ---
    if _file_contains("SKILL.md", "Do NOT create cron"):
        issues.append("SKILL.md still contains old 'Do NOT create cron' prohibition")
    if _file_contains("SKILL.md", "does not create scheduled tasks automatically"):
        issues.append("SKILL.md still contains old 'does not create scheduled tasks' wording")
    if _file_contains("CLAUDE.md", "Create cron jobs automatically"):
        issues.append("CLAUDE.md still contains old 'Create cron jobs automatically' prohibition")

    # --- Positive assertions (must contain new wording) ---
    if not _file_contains("SKILL.md", "schedule"):
        issues.append("SKILL.md missing 'schedule' keyword")
    if not _file_contains("SKILL.md", "auto-monitoring") and not _file_contains("SKILL.md", "automatically enables"):
        issues.append("SKILL.md missing auto-monitoring declaration")
    if not _file_contains("README.md", "schedule"):
        issues.append("README.md missing 'schedule' keyword")

    if issues:
        return False, {"status": "fail", "issues": issues}
    return True, {"status": "ok"}


def main() -> int:
    parser = argparse.ArgumentParser(description="SignalRadar prepublish gate")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per command")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    results: dict[str, dict[str, Any]] = {}
    all_ok = True

    # 1. Package hygiene
    ok, entry = check_package_hygiene()
    results["package_hygiene"] = entry
    if not ok:
        all_ok = False

    # 2. Doctor
    ok, entry = run_doctor(args.timeout)
    results["doctor"] = entry
    if not ok:
        all_ok = False

    # 3. Dry run
    ok, entry = run_dry(args.timeout)
    results["run_dry"] = entry
    if not ok:
        all_ok = False

    # 4. Document consistency
    ok, entry = check_doc_consistency()
    results["doc_consistency"] = entry
    if not ok:
        all_ok = False

    out: dict[str, Any] = {"ok": all_ok, "gate": "v0.5.3-prepublish", "results": results}
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        if all_ok:
            print("PREPUBLISH_PASS all checks ok")
        else:
            print("PREPUBLISH_FAIL")
            for k, v in results.items():
                if v.get("status") not in ("ok",):
                    print(f"  - {k}: {v.get('error') or v.get('issues') or v.get('status')}")
    return 0 if all_ok else 3


if __name__ == "__main__":
    sys.exit(main())

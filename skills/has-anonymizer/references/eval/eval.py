#!/usr/bin/env python3
"""Run scan → hide → restore on test cases and collect evidence for LLM judge.

Infrastructure checks only: command success, JSON validity, file existence,
leftover tags. All semantic evaluation (entity coverage, anonymization quality,
restoration fidelity) is left to the LLM judge reading results.json.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TAG_RE = re.compile(r"<[^<>]+>")

_EVAL_DIR = Path(__file__).resolve().parent
_SKILL_ROOT = _EVAL_DIR.parents[1]
_TEST_CASE_DIR = _EVAL_DIR / "test_case"


# ---------------------------------------------------------------------------
# CLI runner
# ---------------------------------------------------------------------------


@dataclass
class CmdResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    payload: Any | None
    error: str | None


def run_cmd(command: list[str], *, cwd: Path) -> CmdResult:
    """Run a command, parse stdout as JSON, return structured result."""
    proc = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, check=False
    )
    stdout = proc.stdout.strip()
    payload, error = None, None
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            error = str(exc)
    else:
        error = "empty stdout"
    return CmdResult(command, proc.returncode, proc.stdout, proc.stderr, payload, error)


# ---------------------------------------------------------------------------
# Single-case evaluation
# ---------------------------------------------------------------------------


def evaluate_case(
    case: dict[str, Any],
    has_cli: Path,
    case_dir: Path,
    skill_root: Path,
) -> dict[str, Any]:
    """Run scan/hide/restore and collect evidence. Only infrastructure checks."""

    text = case["text"]
    expected = case["expected_entities"]
    has_expected = any(len(v) > 0 for v in expected.values())
    type_args = sum((["--type", t] for t in case["types"]), [])

    (case_dir / "original.txt").write_text(text, encoding="utf-8")

    errors: list[str] = []

    # --- scan ---
    scan_cmd = [str(has_cli), "text", "scan", *type_args, "--text", text]
    scan = run_cmd(scan_cmd, cwd=skill_root)
    _save_cmd(case_dir / "scan.cmd.json", scan)

    scan_entities: dict[str, list[str]] = {}
    if scan.exit_code != 0:
        errors.append("scan_failed")
    elif scan.error:
        errors.append("scan_not_json")
    elif isinstance(scan.payload, dict):
        raw = scan.payload.get("entities", {})
        if isinstance(raw, dict):
            scan_entities = {
                str(k): [str(i) for i in v]
                for k, v in raw.items()
                if isinstance(v, list)
            }
        else:
            errors.append("scan_no_entities_field")

    # --- hide ---
    mapping_path = case_dir / "mapping.json"
    hide_cmd = [
        str(has_cli), "text", "hide", *type_args,
        "--text", text, "--mapping-output", str(mapping_path),
    ]
    hide = run_cmd(hide_cmd, cwd=skill_root)
    _save_cmd(case_dir / "hide.cmd.json", hide)

    hide_text = ""
    if isinstance(hide.payload, dict):
        hide_text = str(hide.payload.get("text", ""))

    if hide.exit_code != 0:
        errors.append("hide_failed")
    elif hide.error:
        errors.append("hide_not_json")
    elif not hide_text:
        errors.append("hide_no_text")

    mapping: dict[str, Any] = {}
    if not mapping_path.exists():
        if hide.exit_code == 0:
            errors.append("mapping_missing")
    else:
        try:
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        except Exception:
            errors.append("mapping_invalid")

    # --- restore ---
    restore_ran = False
    restore_text = ""
    leftover_tags: list[str] = []

    if hide.exit_code == 0 and hide_text:
        restore_cmd = [
            str(has_cli), "text", "restore",
            "--mapping", str(mapping_path), "--text", hide_text,
        ]
        restore = run_cmd(restore_cmd, cwd=skill_root)
        _save_cmd(case_dir / "restore.cmd.json", restore)
        restore_ran = True

        if restore.exit_code != 0:
            errors.append("restore_failed")
        elif restore.error:
            errors.append("restore_not_json")
        else:
            if isinstance(restore.payload, dict):
                restore_text = str(restore.payload.get("text", ""))
            if not restore_text:
                errors.append("restore_no_text")

        leftover_tags = TAG_RE.findall(restore_text)
        if leftover_tags:
            errors.append("restore_has_leftover_tags")
    elif has_expected:
        errors.append("restore_skipped")

    status = "error" if errors else "ok"

    return {
        "id": case["id"],
        "language": case["language"],
        "status": status,
        "errors": errors,
        "types": case["types"],
        "original_text": text,
        "expected_entities": expected,
        "scan_entities": scan_entities,
        "hide_text": hide_text,
        "mapping": mapping,
        "restore_ran": restore_ran,
        "restore_text": restore_text,
        "restore_leftover_tags": leftover_tags,
    }


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def _save_cmd(path: Path, result: CmdResult) -> None:
    """Save raw command execution details for debugging."""
    path.write_text(
        json.dumps(
            {
                "command": result.command,
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": result.error,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="eval",
        description=(
            "Run has text scan/hide/restore on test cases and collect evidence. "
            "Only infrastructure checks are applied; semantic evaluation is "
            "delegated to the LLM judge reading results.json."
        ),
    )
    parser.add_argument(
        "--cases",
        default=str(_TEST_CASE_DIR / "text_short_cases.json"),
        help="Path to the test case dataset JSON.",
    )
    parser.add_argument(
        "--has-cli",
        default=str(_SKILL_ROOT / "scripts" / "has.sh"),
        help="Path to the has CLI entry point.",
    )
    parser.add_argument(
        "--work-dir",
        default="/tmp/has-eval",
        help="Directory for artifacts and reports.",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        help="Run only specific case IDs (repeatable).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Run only the first N cases.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep existing work directory.",
    )
    args = parser.parse_args()

    cases_path = Path(args.cases).resolve()
    has_cli = Path(args.has_cli).resolve()
    work_dir = Path(args.work_dir).resolve()

    dataset = json.loads(cases_path.read_text(encoding="utf-8"))
    cases: list[dict[str, Any]] = dataset["cases"]

    if args.case_ids:
        ids = set(args.case_ids)
        cases = [c for c in cases if c["id"] in ids]
    if args.limit is not None:
        cases = cases[: args.limit]

    if not args.keep and work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    counts = {"ok": 0, "error": 0}
    results: list[dict[str, Any]] = []

    for i, case in enumerate(cases, 1):
        case_dir = work_dir / "cases" / case["id"]
        case_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"[{i}/{len(cases)}] {case['id']} ...",
            end="", flush=True, file=sys.stderr,
        )

        result = evaluate_case(case, has_cli, case_dir, _SKILL_ROOT)

        icon = "✓" if result["status"] == "ok" else "✗"
        print(f" {icon} {result['status']}", file=sys.stderr)
        if result["errors"]:
            print(f"       {result['errors']}", file=sys.stderr)

        counts[result["status"]] += 1
        results.append(result)
        _write_json(case_dir / "result.json", result)

    summary = {
        "dataset": str(cases_path),
        "work_dir": str(work_dir),
        "case_count": len(results),
        "counts": counts,
        "error_ids": [r["id"] for r in results if r["status"] == "error"],
    }

    _write_json(work_dir / "summary.json", summary)
    _write_json(work_dir / "results.json", results)

    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())

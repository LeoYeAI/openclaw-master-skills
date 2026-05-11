from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from common import abs_path, dump_json, dump_text


DISCOVERED_NPM_GATES = [
    "check:cws",
    "check:public",
    "check:public:visual",
    "test:e2e:reviewer",
    "test:e2e",
]


def load_package_scripts(repo_root: Path) -> dict[str, str]:
    package_json = repo_root / "package.json"
    if not package_json.exists():
        return {}
    return json.loads(package_json.read_text(encoding="utf-8")).get("scripts") or {}


def detect_package_runner(repo_root: Path) -> str:
    if (repo_root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (repo_root / "yarn.lock").exists():
        return "yarn"
    return "npm"


def discover_commands(repo_root: Path) -> list[list[str]]:
    commands: list[list[str]] = []
    scripts = load_package_scripts(repo_root)
    runner = detect_package_runner(repo_root)
    for script in DISCOVERED_NPM_GATES:
        if script in scripts:
            commands.append([runner, script])
    reviewer_gate = repo_root / "scripts" / "reviewer_gate.py"
    if reviewer_gate.exists():
        commands.append(["python3", "scripts/reviewer_gate.py", "--repo-root", ".", "--skip-codex"])
    return commands


def run_command(repo_root: Path, command: list[str], timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout_tail": result.stdout[-4000:],
            "stderr_tail": result.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": f"timed out after {timeout}s",
        }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Local CWS E2E Gates",
        "",
        f"Repo: `{report['repo_root']}`",
        f"Commands: **{len(report['commands'])}**",
        f"Blockers: **{len(report['blockers'])}**",
        "",
    ]
    for item in report["results"]:
        status = "pass" if item["returncode"] == 0 else f"fail ({item['returncode']})"
        lines.extend(
            [
                f"## `{shlex.join(item['command'])}`",
                "",
                f"Status: **{status}** in {item['duration_seconds']}s",
                "",
            ]
        )
    if report["blockers"]:
        lines.extend(["## Blockers", *[f"- {item}" for item in report["blockers"]]])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run discovered or explicit repo-local CWS E2E gates.")
    parser.add_argument("--repo-root", default=".", help="Target extension repo root.")
    parser.add_argument("--command", action="append", default=[], help="Explicit command string. Repeatable.")
    parser.add_argument("--timeout", type=int, default=900, help="Timeout per command in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Only print commands without running them.")
    parser.add_argument("--json-out", help="Optional JSON report output path.")
    parser.add_argument("--markdown-out", help="Optional Markdown report output path.")
    args = parser.parse_args()

    repo_root = abs_path(args.repo_root)
    commands = [shlex.split(command) for command in args.command] if args.command else discover_commands(repo_root)
    blockers: list[str] = []
    results: list[dict[str, Any]] = []
    if not commands:
        blockers.append("no local E2E/reviewer gates were discovered; pass --command explicitly")

    if not args.dry_run:
        for command in commands:
            result = run_command(repo_root, command, args.timeout)
            results.append(result)
            if result["returncode"] != 0:
                blockers.append(f"{shlex.join(command)} failed with exit code {result['returncode']}")

    report = {
        "ok": not blockers,
        "repo_root": str(repo_root),
        "commands": commands,
        "dry_run": args.dry_run,
        "results": results,
        "blockers": blockers,
    }
    if args.json_out:
        dump_json(args.json_out, report)
    if args.markdown_out:
        dump_text(args.markdown_out, render_markdown(report))
    print(json.dumps(report, indent=2, ensure_ascii=True))
    if blockers:
        sys.exit(1)


if __name__ == "__main__":
    main()

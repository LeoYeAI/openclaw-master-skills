#!/usr/bin/env python3
"""generate-problem-summary.py - Generate markdown summary of open/stuck Problems.

Reads problems.jsonl and outputs a markdown summary suitable for injection
into the agent's first turn after resurrection.

Usage:
  generate-problem-summary.py [--learning-dir DIR] [--output FILE]

If --output is provided, writes to that file. Otherwise prints to stdout.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError


def get_workspace():
    oc_config = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(oc_config) as f:
            data = json.load(f)
        ws = data.get("agents", {}).get("defaults", {}).get("workspace", "~/.openclaw/workspace")
    except (IOError, json.JSONDecodeError):
        ws = "~/.openclaw/workspace"
    return os.path.expanduser(ws)


def replay_problems(filepath):
    """Replay JSONL to reconstruct problem states."""
    states = {}
    if not os.path.isfile(filepath):
        return states
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            rid = record.get("id", "")
            op = record.get("op", "create")
            if op == "create":
                states[rid] = record.copy()
                states[rid].pop("op", None)
            elif op == "update" and rid in states:
                states[rid].update(record.get("fields", {}))
                states[rid]["updated"] = record.get("timestamp", "")
            elif op == "close" and rid in states:
                states[rid]["status"] = record.get("status", "solved")
                if record.get("solution"):
                    states[rid]["solution"] = record["solution"]
                states[rid]["resolved"] = record.get("timestamp", "")
    return states


def get_solvr_api_key():
    """Read SOLVR_API_KEY from env or config.json."""
    key = os.environ.get("SOLVR_API_KEY", "")
    if key:
        return key
    config_path = os.path.expanduser("~/.amcp/config.json")
    try:
        with open(config_path) as f:
            data = json.load(f)
        key = (data.get("solvr", {}).get("apiKey", "") or
               data.get("pinning", {}).get("solvr", {}).get("apiKey", ""))
    except (IOError, json.JSONDecodeError):
        pass
    return key


def should_surface_remote():
    """Check config toggle: solvr.surfaceRemoteProblems (default: true)."""
    config_path = os.path.expanduser("~/.amcp/config.json")
    try:
        with open(config_path) as f:
            data = json.load(f)
        return data.get("solvr", {}).get("surfaceRemoteProblems", True)
    except (IOError, json.JSONDecodeError):
        return True


def fetch_solvr_problems(api_key):
    """Fetch open problems from Solvr API (GET /v1/me/posts?type=problem&status=open)."""
    if not api_key:
        return []
    base = os.environ.get("SOLVR_BASE_URL", "https://api.solvr.dev/v1")
    url = f"{base}/me/posts?type=problem&status=open"
    try:
        req = Request(url, headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        })
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        posts = data.get("data", data if isinstance(data, list) else [])
        # Normalize to local problem format
        problems = []
        for p in posts:
            problems.append({
                "id": p.get("id", "?"),
                "description": p.get("title", p.get("description", "(no description)")),
                "status": p.get("status", "open"),
                "attempts": len(p.get("approaches", [])),
                "created": p.get("created_at", p.get("created", "unknown")),
                "source": "solvr",
            })
        return problems
    except (URLError, OSError, json.JSONDecodeError, KeyError) as e:
        print(f"WARN: Solvr fetch failed: {e}", file=sys.stderr)
        return []


def generate_summary(learning_dir, include_solvr=True):
    """Generate markdown summary of open/stuck problems."""
    problems_file = os.path.join(learning_dir, "problems.jsonl")
    states = replay_problems(problems_file)

    open_problems = [
        p for p in states.values()
        if p.get("status") in ("open", "stuck")
    ]

    # Merge Solvr remote problems (deduped by id)
    if include_solvr and should_surface_remote():
        api_key = get_solvr_api_key()
        solvr_problems = fetch_solvr_problems(api_key)
        local_ids = {p.get("id") for p in open_problems}
        for sp in solvr_problems:
            if sp["id"] not in local_ids:
                open_problems.append(sp)
                local_ids.add(sp["id"])

    if not open_problems:
        return ""

    # Sort by created (oldest first)
    open_problems.sort(key=lambda x: x.get("created", ""))

    lines = []
    lines.append(f"## Unresolved Problems ({len(open_problems)})")
    lines.append("")
    lines.append("You have unresolved problems from before recovery. "
                 "Review when appropriate — do NOT auto-attempt all at once.")
    lines.append("")

    for p in open_problems:
        pid = p.get("id", "?")
        desc = p.get("description", "(no description)")
        status = p.get("status", "open")
        attempts = p.get("attempts", 0)
        created = p.get("created", "unknown")
        source = p.get("source", "local")

        source_tag = " (Solvr)" if source == "solvr" else ""
        lines.append(f"- **{pid}** [{status}]{source_tag}: {desc}")
        if attempts > 0:
            lines.append(f"  - Attempts: {attempts}")
        lines.append(f"  - Created: {created[:10]}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate markdown summary of open/stuck Problems"
    )
    parser.add_argument("--learning-dir", help="Learning storage directory")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    learning_dir = args.learning_dir or os.environ.get("LEARNING_DIR")
    if not learning_dir:
        learning_dir = os.path.join(get_workspace(), "memory", "learning")

    summary = generate_summary(learning_dir)

    if not summary:
        print("No open problems to surface.", file=sys.stderr)
        sys.exit(0)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(summary)
        print(f"Problem summary written to {args.output}", file=sys.stderr)
    else:
        print(summary)


if __name__ == "__main__":
    main()

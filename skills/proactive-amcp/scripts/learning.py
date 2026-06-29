#!/usr/bin/env python3
"""learning.py - Problem and Learning entity CRUD operations.

Append-only JSONL storage for Problem and Learning entities.
Each operation appends a record to the JSONL file; get/list replays
the log to reconstruct current state.

Usage:
  learning.py problem create --description "..." [--blocker] [--source SOURCE]
  learning.py problem update --id ID [--field KEY=VALUE ...]
  learning.py problem get --id ID
  learning.py problem list [--status STATUS]
  learning.py problem close --id ID --status STATUS [--solution "..."]

  learning.py learning create --insight "..." [--source-problem ID] [--tags TAG,TAG]
  learning.py learning verify --id ID [--human-verified]
  learning.py learning get --id ID
  learning.py learning list [--confidence LEVEL] [--tag TAG]
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone

# ============================================================
# Paths — dynamic, overridable via env
# ============================================================

def get_workspace():
    """Get OpenClaw workspace path."""
    oc_config = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(oc_config) as f:
            data = json.load(f)
        ws = data.get("agents", {}).get("defaults", {}).get("workspace", "~/.openclaw/workspace")
    except (IOError, json.JSONDecodeError):
        ws = "~/.openclaw/workspace"
    return os.path.expanduser(ws)


def get_learning_dir():
    """Get learning storage directory."""
    env_dir = os.environ.get("LEARNING_DIR")
    if env_dir:
        return os.path.expanduser(env_dir)
    return os.path.join(get_workspace(), "memory", "learning")


LEARNING_DIR = get_learning_dir()
PROBLEMS_FILE = os.path.join(LEARNING_DIR, "problems.jsonl")
LEARNINGS_FILE = os.path.join(LEARNING_DIR, "learnings.jsonl")
STATS_FILE = os.path.join(LEARNING_DIR, "stats.json")

# ============================================================
# Helpers
# ============================================================

def ensure_dir():
    os.makedirs(LEARNING_DIR, exist_ok=True)


def gen_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def append_record(filepath, record):
    ensure_dir()
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def replay_jsonl(filepath, entity_id=None):
    """Replay JSONL to reconstruct entity state(s).

    Returns dict: {id: merged_state}
    """
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
            if entity_id and rid != entity_id:
                continue

            op = record.get("op", "create")
            if op == "create":
                states[rid] = record.copy()
                states[rid].pop("op", None)
            elif op == "update" and rid in states:
                fields = record.get("fields", {})
                states[rid].update(fields)
                states[rid]["updated"] = record.get("timestamp", now_iso())
            elif op == "close" and rid in states:
                states[rid]["status"] = record.get("status", "solved")
                if record.get("solution"):
                    states[rid]["solution"] = record["solution"]
                states[rid]["resolved"] = record.get("timestamp", now_iso())
                states[rid]["updated"] = record.get("timestamp", now_iso())
            elif op == "verify" and rid in states:
                states[rid]["confidence"] = "verified"
                states[rid]["verified_at"] = record.get("timestamp", now_iso())
                states[rid]["human_verified"] = record.get("human_verified", True)
                states[rid]["updated"] = record.get("timestamp", now_iso())

    return states


def load_stats():
    if os.path.isfile(STATS_FILE):
        try:
            with open(STATS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "total_problems": 0,
        "total_solved": 0,
        "solved_post_recovery": 0,
        "total_learnings": 0,
        "last_updated": None
    }


def save_stats(stats):
    ensure_dir()
    stats["last_updated"] = now_iso()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)
        f.write("\n")


def trigger_smart_checkpoint(trigger_type="learning"):
    """Trigger smart checkpoint after learning capture."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    checkpoint_script = os.path.join(script_dir, "checkpoint.sh")

    if os.path.isfile(checkpoint_script) and os.access(checkpoint_script, os.X_OK):
        try:
            subprocess.run(
                [checkpoint_script, "--trigger", trigger_type, "--quiet"],
                capture_output=True,
                timeout=60
            )
        except Exception:
            pass  # Don't fail learning capture if checkpoint fails


# ============================================================
# Problem operations
# ============================================================

def create_problem(description, blocker=False, source="manual"):
    pid = gen_id("prob")
    record = {
        "op": "create",
        "id": pid,
        "type": "problem",
        "description": description,
        "blocker": blocker,
        "source": source,
        "status": "open",
        "attempts": 0,
        "created": now_iso(),
        "updated": now_iso(),
        "timestamp": now_iso()
    }
    append_record(PROBLEMS_FILE, record)

    stats = load_stats()
    stats["total_problems"] = stats.get("total_problems", 0) + 1
    save_stats(stats)

    result = record.copy()
    result.pop("op", None)
    print(json.dumps(result, indent=2))
    return pid


def update_problem(pid, fields):
    # Verify problem exists
    states = replay_jsonl(PROBLEMS_FILE, pid)
    if pid not in states:
        print(f"ERROR: Problem {pid} not found", file=sys.stderr)
        sys.exit(1)

    record = {
        "op": "update",
        "id": pid,
        "fields": fields,
        "timestamp": now_iso()
    }
    append_record(PROBLEMS_FILE, record)

    # Return updated state
    states = replay_jsonl(PROBLEMS_FILE, pid)
    print(json.dumps(states.get(pid, {}), indent=2))


def get_problem(pid):
    states = replay_jsonl(PROBLEMS_FILE, pid)
    if pid not in states:
        print(f"ERROR: Problem {pid} not found", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(states[pid], indent=2))


def list_problems(status_filter=None):
    states = replay_jsonl(PROBLEMS_FILE)
    results = []
    for pid, state in states.items():
        if status_filter and state.get("status") != status_filter:
            continue
        results.append(state)

    # Sort by created timestamp (newest first)
    results.sort(key=lambda x: x.get("created", ""), reverse=True)
    print(json.dumps(results, indent=2))


def close_problem(pid, status, solution=None):
    # Verify problem exists and is open
    states = replay_jsonl(PROBLEMS_FILE, pid)
    if pid not in states:
        print(f"ERROR: Problem {pid} not found", file=sys.stderr)
        sys.exit(1)
    if states[pid].get("status") in ("solved", "abandoned"):
        print(f"WARN: Problem {pid} already {states[pid]['status']}", file=sys.stderr)

    record = {
        "op": "close",
        "id": pid,
        "status": status,
        "timestamp": now_iso()
    }
    if solution:
        record["solution"] = solution
    append_record(PROBLEMS_FILE, record)

    if status == "solved":
        stats = load_stats()
        stats["total_solved"] = stats.get("total_solved", 0) + 1
        save_stats(stats)

    # Return closed state
    states = replay_jsonl(PROBLEMS_FILE, pid)
    print(json.dumps(states.get(pid, {}), indent=2))


# ============================================================
# Learning operations
# ============================================================

def create_learning(insight, source_problem=None, tags=None):
    lid = gen_id("learn")
    record = {
        "op": "create",
        "id": lid,
        "type": "learning",
        "insight": insight,
        "confidence": "tentative",
        "tags": tags or [],
        "created": now_iso(),
        "updated": now_iso(),
        "timestamp": now_iso()
    }
    if source_problem:
        record["source_problem"] = source_problem

    append_record(LEARNINGS_FILE, record)

    stats = load_stats()
    stats["total_learnings"] = stats.get("total_learnings", 0) + 1
    save_stats(stats)

    # If source_problem provided, close it as solved
    if source_problem:
        prob_states = replay_jsonl(PROBLEMS_FILE, source_problem)
        if source_problem in prob_states:
            if prob_states[source_problem].get("status") not in ("solved", "abandoned"):
                close_record = {
                    "op": "close",
                    "id": source_problem,
                    "status": "solved",
                    "solution": insight,
                    "timestamp": now_iso()
                }
                append_record(PROBLEMS_FILE, close_record)
                stats = load_stats()
                stats["total_solved"] = stats.get("total_solved", 0) + 1
                save_stats(stats)

    result = record.copy()
    result.pop("op", None)
    print(json.dumps(result, indent=2))
    return lid


def verify_learning(lid, human_verified=True):
    states = replay_jsonl(LEARNINGS_FILE, lid)
    if lid not in states:
        print(f"ERROR: Learning {lid} not found", file=sys.stderr)
        sys.exit(1)

    record = {
        "op": "verify",
        "id": lid,
        "human_verified": human_verified,
        "timestamp": now_iso()
    }
    append_record(LEARNINGS_FILE, record)

    stats = load_stats()
    stats["verified_learnings"] = stats.get("verified_learnings", 0) + 1
    save_stats(stats)

    states = replay_jsonl(LEARNINGS_FILE, lid)
    print(json.dumps(states.get(lid, {}), indent=2))


def get_learning(lid):
    states = replay_jsonl(LEARNINGS_FILE, lid)
    if lid not in states:
        print(f"ERROR: Learning {lid} not found", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(states[lid], indent=2))


def list_learnings(confidence_filter=None, tag_filter=None):
    states = replay_jsonl(LEARNINGS_FILE)
    results = []
    for lid, state in states.items():
        if confidence_filter and state.get("confidence") != confidence_filter:
            continue
        if tag_filter and tag_filter not in state.get("tags", []):
            continue
        results.append(state)

    results.sort(key=lambda x: x.get("created", ""), reverse=True)
    print(json.dumps(results, indent=2))


def check_unverified(days=7):
    """Check for unverified learnings older than N days. Used by heartbeat."""
    states = replay_jsonl(LEARNINGS_FILE)
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)
    warnings = []

    for lid, state in states.items():
        if state.get("confidence") != "tentative":
            continue
        created = state.get("created", "")
        try:
            created_dt = datetime.fromisoformat(created)
            if created_dt < cutoff:
                warnings.append({
                    "id": lid,
                    "insight": state.get("insight", ""),
                    "created": created,
                    "days_old": (datetime.now(timezone.utc) - created_dt).days
                })
        except (ValueError, TypeError):
            continue

    if warnings:
        print(f"WARNING: {len(warnings)} unverified learning(s) older than {days} days:",
              file=sys.stderr)
        for w in warnings:
            print(f"  - {w['id']}: \"{w['insight'][:60]}\" ({w['days_old']}d old)",
                  file=sys.stderr)
    print(json.dumps(warnings, indent=2))


# ============================================================
# CLI argument parsing
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        prog="learning.py",
        description="Problem and Learning entity CRUD operations"
    )
    subparsers = parser.add_subparsers(dest="entity", required=True)

    # --- Problem subcommand ---
    prob = subparsers.add_parser("problem", help="Problem operations")
    prob_sub = prob.add_subparsers(dest="action", required=True)

    # problem create
    pc = prob_sub.add_parser("create", help="Create a new problem")
    pc.add_argument("--description", "-d", required=True, help="Problem description")
    pc.add_argument("--blocker", action="store_true", help="Mark as blocker")
    pc.add_argument("--source", default="manual", help="Source (manual, command, self-detect, skill)")

    # problem update
    pu = prob_sub.add_parser("update", help="Update a problem")
    pu.add_argument("--id", required=True, help="Problem ID (prob_...)")
    pu.add_argument("--field", action="append", help="Field to update (KEY=VALUE)", default=[])

    # problem get
    pg = prob_sub.add_parser("get", help="Get a problem by ID")
    pg.add_argument("--id", required=True, help="Problem ID")

    # problem list
    pl = prob_sub.add_parser("list", help="List problems")
    pl.add_argument("--status", choices=["open", "stuck", "solved", "abandoned"], help="Filter by status")

    # problem close
    pcl = prob_sub.add_parser("close", help="Close a problem")
    pcl.add_argument("--id", required=True, help="Problem ID")
    pcl.add_argument("--status", required=True, choices=["solved", "abandoned"], help="Close status")
    pcl.add_argument("--solution", help="Solution description")

    # --- Learning subcommand ---
    learn = subparsers.add_parser("learning", help="Learning operations")
    learn_sub = learn.add_subparsers(dest="action", required=True)

    # learning create
    lc = learn_sub.add_parser("create", help="Create a new learning")
    lc.add_argument("--insight", "-i", required=True, help="What was learned")
    lc.add_argument("--source-problem", help="Problem ID this learning solves")
    lc.add_argument("--tags", help="Comma-separated tags")

    # learning verify
    lv = learn_sub.add_parser("verify", help="Verify a learning")
    lv.add_argument("--id", required=True, help="Learning ID (learn_...)")
    lv.add_argument("--human-verified", action="store_true", default=True, help="Human verified (default: true)")

    # learning get
    lg = learn_sub.add_parser("get", help="Get a learning by ID")
    lg.add_argument("--id", required=True, help="Learning ID")

    # learning list
    ll = learn_sub.add_parser("list", help="List learnings")
    ll.add_argument("--confidence", choices=["tentative", "verified"], help="Filter by confidence")
    ll.add_argument("--tag", help="Filter by tag")

    # learning check-unverified
    lcu = learn_sub.add_parser("check-unverified", help="Check for stale unverified learnings")
    lcu.add_argument("--days", type=int, default=7, help="Days threshold (default: 7)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.entity == "problem":
        if args.action == "create":
            create_problem(args.description, args.blocker, args.source)
        elif args.action == "update":
            fields = {}
            for f in args.field:
                if "=" in f:
                    k, v = f.split("=", 1)
                    fields[k] = v
            update_problem(args.id, fields)
        elif args.action == "get":
            get_problem(args.id)
        elif args.action == "list":
            list_problems(args.status)
        elif args.action == "close":
            close_problem(args.id, args.status, args.solution)

    elif args.entity == "learning":
        if args.action == "create":
            tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
            create_learning(args.insight, args.source_problem, tags)
            # Smart checkpoint after learning capture
            trigger_smart_checkpoint("learning")
        elif args.action == "verify":
            verify_learning(args.id, args.human_verified)
        elif args.action == "get":
            get_learning(args.id)
        elif args.action == "list":
            list_learnings(args.confidence, args.tag)
        elif args.action == "check-unverified":
            check_unverified(args.days)


if __name__ == "__main__":
    main()

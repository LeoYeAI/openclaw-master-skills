#!/usr/bin/env python3
"""learning-report.py - Generate human-readable learning metrics report.

Reads problems.jsonl, learnings.jsonl, and stats.json to produce a
report with: total problems, solve rate, avg attempts, self-improvement rate.

Usage:
  learning-report.py [--output FILE] [--learning-dir DIR] [--json]

Environment:
  LEARNING_DIR  Override learning storage directory
"""

import argparse, json, os, sys
from collections import Counter


def get_learning_dir():
    env_dir = os.environ.get("LEARNING_DIR")
    if env_dir:
        return os.path.expanduser(env_dir)
    oc_config = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(oc_config) as f:
            ws = json.load(f).get("agents", {}).get("defaults", {}).get("workspace", "~/.openclaw/workspace")
    except (IOError, json.JSONDecodeError):
        ws = "~/.openclaw/workspace"
    return os.path.join(os.path.expanduser(ws), "memory", "learning")


def replay_jsonl(filepath):
    """Replay JSONL to reconstruct entity states -> {id: state}."""
    states = {}
    if not os.path.isfile(filepath):
        return states
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            rid, op = rec.get("id", ""), rec.get("op", "create")
            ts = rec.get("timestamp", "")
            if op == "create":
                states[rid] = rec.copy()
                states[rid].pop("op", None)
            elif op == "update" and rid in states:
                states[rid].update(rec.get("fields", {}))
                states[rid]["updated"] = ts
            elif op == "close" and rid in states:
                states[rid]["status"] = rec.get("status", "solved")
                if rec.get("solution"):
                    states[rid]["solution"] = rec["solution"]
                states[rid]["resolved"] = states[rid]["updated"] = ts
            elif op == "verify" and rid in states:
                states[rid].update(confidence="verified", verified_at=ts,
                                   human_verified=rec.get("human_verified", True), updated=ts)
    return states


def compute_metrics(learning_dir):
    """Compute detailed metrics from JSONL stores."""
    problems = replay_jsonl(os.path.join(learning_dir, "problems.jsonl"))
    learnings = replay_jsonl(os.path.join(learning_dir, "learnings.jsonl"))

    stats = {}
    stats_file = os.path.join(learning_dir, "stats.json")
    if os.path.isfile(stats_file):
        try:
            with open(stats_file) as f:
                stats = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    by_status, by_source, total_attempts, solved = Counter(), Counter(), 0, 0
    for p in problems.values():
        st = p.get("status", "open")
        by_status[st] += 1
        total_attempts += p.get("attempts", 0)
        if st == "solved":
            solved += 1
            by_source[p.get("source", "unknown")] += 1

    by_confidence = Counter(l.get("confidence", "tentative") for l in learnings.values())
    total = len(problems)
    solved_post = stats.get("solved_post_recovery", 0)
    total_solved = stats.get("total_solved", solved)

    return {
        "total_problems": total, "total_learnings": len(learnings),
        "problems_by_status": dict(by_status),
        "learnings_by_confidence": dict(by_confidence),
        "problems_solved_by_source": dict(by_source),
        "solve_rate": round(solved / total * 100, 1) if total else 0,
        "avg_attempts_to_solve": round(total_attempts / solved, 1) if solved else 0,
        "solved_post_recovery": solved_post, "total_solved": total_solved,
        "self_improvement_rate": round(solved_post / total_solved * 100, 1) if total_solved else 0,
    }


def format_report(m):
    """Format metrics as human-readable markdown report."""
    sections = [
        "# Learning Report\n",
        "## Summary\n",
        f"- **Total problems:** {m['total_problems']}",
        f"- **Total learnings:** {m['total_learnings']}",
        f"- **Solve rate:** {m['solve_rate']}%",
        f"- **Avg attempts to solve:** {m['avg_attempts_to_solve']}",
        f"- **Self-improvement rate:** {m['self_improvement_rate']}% "
        f"({m['solved_post_recovery']}/{m['total_solved']} solved post-recovery)\n",
    ]
    for title, data in [("Problems by Status", m["problems_by_status"]),
                        ("Learnings by Confidence", m["learnings_by_confidence"]),
                        ("Problems Solved by Source", m["problems_solved_by_source"])]:
        sections.append(f"## {title}\n")
        if data:
            sections.extend(f"- {k}: {v}" for k, v in sorted(data.items()))
        else:
            sections.append("- (none)")
    sections.append("")
    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Generate learning metrics report")
    parser.add_argument("--output", help="Write report to file (default: stdout)")
    parser.add_argument("--learning-dir", help="Override learning directory")
    parser.add_argument("--json", action="store_true", help="Output raw JSON metrics")
    args = parser.parse_args()

    metrics = compute_metrics(args.learning_dir or get_learning_dir())
    output = json.dumps(metrics, indent=2) + "\n" if args.json else format_report(metrics)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()

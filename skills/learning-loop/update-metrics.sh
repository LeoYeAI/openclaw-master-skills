#!/bin/bash
# Learning Loop - Metrics Updater
# Calculates current week's metrics and writes to metrics.json
# Usage: bash update-metrics.sh [workspace-dir]
# Returns: 0 on success, 1 on configuration error, 2 on data corruption, 3 on lock contention
# Schedule: Daily/Weekly cron
# Dependencies: events.jsonl, rules.json, lessons.json
# Side Effects: Updates metrics.json (with file locking), writes to parse-errors.jsonl

set -o pipefail

SCRIPT_NAME="update-metrics.sh"
WORKSPACE="${1:-$(pwd)}"
LEARNING_DIR="$WORKSPACE/memory/learning"
EVENTS_FILE="$LEARNING_DIR/events.jsonl"
RULES_FILE="$LEARNING_DIR/rules.json"
LESSONS_FILE="$LEARNING_DIR/lessons.json"
METRICS_FILE="$LEARNING_DIR/metrics.json"

# ============================================================================
# INPUT VALIDATION
# ============================================================================

# Check workspace exists and is writable
if [[ ! -d "$WORKSPACE" ]]; then
    echo "ERROR: Workspace does not exist: $WORKSPACE"
    exit 1
fi

if [[ ! -w "$WORKSPACE" ]]; then
    echo "ERROR: Workspace is not writable: $WORKSPACE"
    exit 1
fi

# Prevent system directories
if [[ "$WORKSPACE" =~ ^/(etc|bin|sbin|usr|System|Library|Applications) ]]; then
    echo "ERROR: Cannot use system directory as workspace: $WORKSPACE"
    exit 1
fi

# Check required files exist
if [[ ! -f "$EVENTS_FILE" ]]; then
    echo "WARNING: events.jsonl not found at $EVENTS_FILE"
    echo "Creating empty metrics.json..."
fi

# ============================================================================
# FILE LOCKING SETUP
# ============================================================================

LOCK_FILE="$LEARNING_DIR/.lockfile"
exec 200>"$LOCK_FILE"
if ! flock -w 10 200; then
    echo "ERROR: Could not acquire lock on $LOCK_FILE"
    exit 3
fi

python3 - "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYTHON'
import json, os, sys, fcntl
from datetime import datetime, date, timedelta
from collections import Counter

learning_dir = sys.argv[1]
script_name = sys.argv[2]

events_path = os.path.join(learning_dir, "events.jsonl")
rules_path = os.path.join(learning_dir, "rules.json")
lessons_path = os.path.join(learning_dir, "lessons.json")
metrics_path = os.path.join(learning_dir, "metrics.json")
parse_errors = []

# Load files
events = []
try:
    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
                    # Log parse error
                    parse_errors.append({
                        "ts": datetime.now().isoformat(),
                        "error": str(e),
                        "line": line[:200],
                        "script": script_name
                    })
except FileNotFoundError:
    pass

# Write parse errors if any
if parse_errors:
    errors_file = os.path.join(learning_dir, "parse-errors.jsonl")
    with open(errors_file, "a") as ef:
        for err in parse_errors:
            ef.write(json.dumps(err) + "\n")
    print(f"⚠️  {len(parse_errors)} parse errors logged to parse-errors.jsonl")

# Load rules with lock
try:
    with open(rules_path) as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules = json.load(f).get("rules", [])
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError):
    rules = []

# Load lessons with lock
try:
    with open(lessons_path) as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        lessons = json.load(f).get("lessons", [])
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError):
    lessons = []

# Load existing metrics
try:
    with open(metrics_path) as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        metrics = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError):
    metrics = {"version": "1.0.0", "started": str(date.today()), "weekly": [], "totals": {}}

# Calculate current week
today = date.today()
week_start = today - timedelta(days=today.weekday())
week_label = today.strftime("%Y-W%V")

# Filter events from this week
week_start_iso = week_start.isoformat()
week_events = [e for e in events if e.get("ts", "") >= week_start_iso]

# Count by type
type_counts = Counter(e.get("type") for e in week_events)
mistakes = type_counts.get("mistake", 0)
successes = type_counts.get("success", 0)
debug_sessions = type_counts.get("debug_session", 0)
feedback = type_counts.get("feedback", 0)
discoveries = type_counts.get("discovery", 0)

# Check for repeated mistakes (same category with existing rule)
rule_cats = {r["category"] for r in rules}
mistake_events = [e for e in week_events if e.get("type") == "mistake"]
repeated = sum(1 for m in mistake_events if m.get("category") in rule_cats)

# Count violations
total_violations = sum(r.get("violations", 0) for r in rules)

# Lessons applied
lessons_applied = sum(l.get("times_applied", 0) for l in lessons)
lessons_saved = sum(l.get("times_saved", 0) for l in lessons)
lessons_promoted = sum(1 for l in lessons if l.get("promoted_to_rule"))

# Feedback signals
positive_feedback = len([e for e in week_events if e.get("type") == "feedback" and e.get("sentiment", "") == "positive"])
negative_feedback = len([e for e in week_events if e.get("type") == "feedback" and e.get("sentiment", "") == "negative"])

# Calculate satisfaction score (-1.0 to 1.0)
total_feedback = positive_feedback + negative_feedback
satisfaction = round((positive_feedback - negative_feedback) / total_feedback, 2) if total_feedback > 0 else None

# Build weekly entry
week_entry = {
    "week": week_label,
    "generated": datetime.now().isoformat(),
    "events": {
        "total": len(week_events),
        "mistakes": mistakes,
        "successes": successes,
        "debug_sessions": debug_sessions,
        "feedback": feedback,
        "discoveries": discoveries
    },
    "regressions": repeated,
    "rules_active": len(rules),
    "lessons_total": len(lessons),
    "lessons_promoted": lessons_promoted,
    "total_violations": total_violations,
    "satisfaction": satisfaction
}

# Check if this week already has an entry
existing_weeks = [w["week"] for w in metrics.get("weekly", [])]
if week_label in existing_weeks:
    for i, w in enumerate(metrics["weekly"]):
        if w["week"] == week_label:
            metrics["weekly"][i] = week_entry
            break
    print(f"Updated metrics for {week_label}")
else:
    metrics["weekly"].append(week_entry)
    print(f"Added metrics for {week_label}")

# Update totals
metrics["totals"] = {
    "events": len(events),
    "lessons": len(lessons),
    "rules": len(rules),
    "total_violations": total_violations,
    "total_saves": lessons_saved,
    "total_applied": lessons_applied,
    "promoted": lessons_promoted
}

# Write with file locking
try:
    with open(metrics_path, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(metrics, f, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except Exception as e:
    print(f"ERROR: Failed to write metrics.json: {e}")
    sys.exit(2)

# Print summary
print(f"\n{'='*40}")
print(f"Week: {week_label}")
print(f"Events this week: {len(week_events)}")
print(f"  Mistakes: {mistakes} | Successes: {successes} | Debug: {debug_sessions}")
print(f"  Feedback: {feedback} | Discoveries: {discoveries}")
print(f"Regressions: {repeated}")
print(f"Rules: {len(rules)} active")
print(f"Lessons: {len(lessons)} total, {lessons_promoted} promoted")
print(f"Satisfaction: {satisfaction if satisfaction is not None else 'N/A (no feedback events)'}")
print(f"{'='*40}")

PYTHON

exit_code=$?

# Release lock
exec 200>&-

exit $exit_code

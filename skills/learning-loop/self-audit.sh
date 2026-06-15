#!/bin/bash
# Learning Loop - Self Audit
# Evaluates whether the learning loop itself is working effectively
# and generates improvement recommendations FOR THE LOOP ITSELF
# Usage: bash self-audit.sh [workspace-dir]
# Returns: 0 on success, 1 on configuration error
# Schedule: Weekly cron
# Dependencies: All learning loop files
# Side Effects: Writes to parse-errors.jsonl

set -o pipefail

SCRIPT_NAME="self-audit.sh"
WORKSPACE="${1:-$(pwd)}"
LEARNING_DIR="$WORKSPACE/memory/learning"

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

echo "Learning Loop - Self Audit"
echo "========================="
echo ""

python3 - "$WORKSPACE" "$SCRIPT_NAME" "$LEARNING_DIR" << 'PYTHON'
import json, os, sys, fcntl
from datetime import datetime, date, timedelta
from collections import Counter

workspace = sys.argv[1]
script_name = sys.argv[2]
learning_dir = sys.argv[3]

issues = []
score = 0
max_score = 0
parse_errors = []

def check(name, passed, detail="", weight=1):
    global score, max_score
    max_score += weight
    if passed:
        score += weight
        print(f"  ✅ {name}: {detail}")
    else:
        print(f"  ❌ {name}: {detail}")
        issues.append(f"{name}: {detail}")

print("## File Health\n")

# Check all required files exist
required = ["events.jsonl", "rules.json", "lessons.json", "pre-action-checklist.md", "BOOT.md", "metrics.json"]
for f in required:
    path = os.path.join(learning_dir, f)
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    check(f, exists and size > 0, f"exists ({size}b)" if exists and size > 0 else "MISSING or empty")

print(f"\n## Event Quality\n")

# Check events
events = []
events_path = os.path.join(learning_dir, "events.jsonl")
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
    
    # Write parse errors if any
    if parse_errors:
        errors_file = os.path.join(learning_dir, "parse-errors.jsonl")
        with open(errors_file, "a") as ef:
            for err in parse_errors:
                ef.write(json.dumps(err) + "\n")
        print(f"  ⚠️  {len(parse_errors)} parse errors logged to parse-errors.jsonl")
        
except FileNotFoundError:
    pass

check("Event count", len(events) >= 5, f"{len(events)} events (target: 5+)")

# Event type diversity
types = Counter(e.get("type") for e in events)
check("Type diversity", len(types) >= 3, f"{len(types)} types: {dict(types)}")

# Category diversity
cats = Counter(e.get("category") for e in events)
check("Category coverage", len(cats) >= 3, f"{len(cats)} categories: {dict(cats)}")

# Event freshness (events in last 7 days)
recent = 0
cutoff = (datetime.now() - timedelta(days=7)).isoformat()
for e in events:
    ts = e.get("ts", "")
    if ts > cutoff:
        recent += 1
check("Event freshness", recent >= 3, f"{recent} events in last 7 days")

# Check for events with all required fields
required_fields = {"ts", "type", "category", "problem", "solution"}
complete = sum(1 for e in events if required_fields.issubset(e.keys()))
check("Event completeness", complete == len(events), f"{complete}/{len(events)} fully complete")

print(f"\n## Rule Quality\n")

# Check rules
rules = []
rules_path = os.path.join(learning_dir, "rules.json")
try:
    with open(rules_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules = json.load(f).get("rules", [])
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError):
    pass

check("Rule count", len(rules) >= 5, f"{len(rules)} rules (target: 5+)")

# Rule type distribution
rule_types = Counter(r.get("type") for r in rules)
check("Rule type variety", len(rule_types) >= 2, f"{dict(rule_types)}")

# Rules with sources
sourced = sum(1 for r in rules if r.get("source_lesson"))
check("Rules from lessons", sourced > 0, f"{sourced}/{len(rules)} traced to lessons", weight=2)

print(f"\n## Lesson Quality\n")

# Check lessons
lessons = []
lessons_path = os.path.join(learning_dir, "lessons.json")
try:
    with open(lessons_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        lessons = json.load(f).get("lessons", [])
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError):
    pass

check("Lesson count", len(lessons) >= 5, f"{len(lessons)} lessons")

# Promotion rate
promoted = sum(1 for l in lessons if l.get("promoted_to_rule"))
check("Promotion rate", promoted > 0, f"{promoted}/{len(lessons)} promoted to rules")

# Application tracking
applied = sum(1 for l in lessons if l.get("times_applied", 0) > 0)
target = len(lessons) * 0.5 if lessons else 1
check("Lessons applied", applied >= target, f"{applied}/{len(lessons)} applied at least once")

print(f"\n## Enforcement Chain\n")

# Check enforcement layers
# Layer 1: AGENTS.md mentions learning loop
agents_md = os.path.join(workspace, "AGENTS.md")
agents_has_loop = False
if os.path.exists(agents_md):
    with open(agents_md) as f:
        content = f.read()
    agents_has_loop = "learning" in content.lower() and "rules.json" in content
check("Boot sequence (AGENTS.md)", agents_has_loop, "Learning loop in boot instructions")

# Layer 2: Check HEARTBEAT.md mentions learning
heartbeat = os.path.join(workspace, "HEARTBEAT.md")
hb_has_loop = False
if os.path.exists(heartbeat):
    with open(heartbeat) as f:
        content = f.read()
    hb_has_loop = "learning" in content.lower()
check("Heartbeat check", hb_has_loop, "Learning loop in heartbeat rotation")

# Layer 3: Weekly directory exists (cron output)
weekly_dir = os.path.join(learning_dir, "weekly")
has_reports = os.path.exists(weekly_dir) and len(os.listdir(weekly_dir)) > 0
check("Weekly reports", has_reports, f"{'Reports exist' if has_reports else 'No reports yet'}")

print(f"\n## Loop Effectiveness\n")

# Meta check: is the loop learning about itself?
loop_events = [e for e in events if "learning" in str(e.get("tags", [])) or "loop" in str(e.get("tags", []))]
check("Meta-learning", len(loop_events) > 0, f"{len(loop_events)} events about the loop itself")

# Regression check: repeated mistakes
mistakes = [e for e in events if e.get("type") == "mistake"]
mistake_cats = Counter(m.get("category") for m in mistakes)
repeated = {cat: count for cat, count in mistake_cats.items() if count >= 2}
check("No repeated mistakes", len(repeated) == 0, f"Repeated in: {dict(repeated)}" if repeated else "No categories with 2+ mistakes")

# Guard check: are guards being used?
guard_log = os.path.join(learning_dir, "guard-log.jsonl")
guard_entries = []
if os.path.exists(guard_log):
    with open(guard_log) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    guard_entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    # Log guard log parse errors too
                    parse_errors.append({
                        "ts": datetime.now().isoformat(),
                        "error": str(e),
                        "line": line[:200],
                        "script": script_name + "/guard-log"
                    })
guard_recent = [g for g in guard_entries if g.get("ts", "") >= cutoff]
saves_logged = sum(1 for g in guard_entries if g.get("save_logged"))
check("Guard checks active", len(guard_recent) >= 3, f"{len(guard_recent)} checks in last 7 days (target: 3+)")
check("Saves being tracked", saves_logged > 0, f"{saves_logged}/{len(guard_entries)} guards logged saves", weight=2)

# Write any accumulated parse errors
if parse_errors:
    errors_file = os.path.join(learning_dir, "parse-errors.jsonl")
    with open(errors_file, "a") as ef:
        for err in parse_errors:
            ef.write(json.dumps(err) + "\n")

# Outcome measurement: ratio of saves to violations
total_saves = sum(l.get("times_saved", 0) for l in lessons)
total_violations = sum(r.get("violations", 0) for r in rules)
if total_violations > 0:
    save_ratio = total_saves / (total_saves + total_violations)
    check("Save:violation ratio", save_ratio >= 0.5, f"{total_saves} saves vs {total_violations} violations ({save_ratio:.0%} prevention rate)", weight=2)
else:
    check("Save:violation ratio", True, "No violations (perfect)", weight=2)

print(f"\n{'='*40}")
print(f"## Score: {score}/{max_score} ({score/max_score*100:.0f}%)")
print(f"{'='*40}")

if score/max_score >= 0.9:
    grade = "A - Excellent"
elif score/max_score >= 0.75:
    grade = "B - Good, minor gaps"
elif score/max_score >= 0.6:
    grade = "C - Working but needs attention"
else:
    grade = "D - Significant gaps"
print(f"Grade: {grade}\n")

if issues:
    print("## Issues to Fix")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

# Generate self-improvement recommendations
print("\n## Self-Improvement Recommendations")
recs = 0
if len(events) < 10:
    recs += 1
    print(f"  {recs}. Capture more events - target 10+ per week for meaningful patterns")
if not has_reports:
    recs += 1
    print(f"  {recs}. Run detect-patterns.sh to generate first weekly report")
if len(loop_events) == 0:
    recs += 1
    print(f"  {recs}. Add meta-learning events - log when the loop itself helps or fails")
if score/max_score < 0.9:
    recs += 1
    print(f"  {recs}. Fix {len(issues)} issue(s) above to reach 90%+ score")
if recs == 0:
    print("  System is healthy. Focus on accumulating real usage data.")

PYTHON

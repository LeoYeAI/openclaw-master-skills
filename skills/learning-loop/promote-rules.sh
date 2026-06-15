#!/bin/bash
# Learning Loop - Rule Promotion Pipeline
# Checks lessons.json for entries ready to be promoted to rules.json
# Promotion criteria: times_applied >= 3 AND confidence_score >= 0.9 AND not already promoted
# Usage: bash promote-rules.sh [workspace-dir] [--dry-run]
# Returns: 0 on success, 1 on configuration error, 2 on data corruption
# Schedule: Daily/Weekly cron
# Dependencies: rules.json, lessons.json
# Side Effects: Updates rules.json and lessons.json (with file locking)

set -o pipefail

SCRIPT_NAME="promote-rules.sh"
WORKSPACE=""
DRY_RUN=""

# Parse args: workspace dir and --dry-run in any order
for arg in "$@"; do
    if [ "$arg" = "--dry-run" ]; then
        DRY_RUN="--dry-run"
    elif [ -z "$WORKSPACE" ]; then
        WORKSPACE="$arg"
    fi
done

WORKSPACE="${WORKSPACE:-$(pwd)}"
LEARNING_DIR="$WORKSPACE/memory/learning"
RULES_FILE="$LEARNING_DIR/rules.json"
LESSONS_FILE="$LEARNING_DIR/lessons.json"

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

echo "Learning Loop - Rule Promotion Pipeline"
echo "======================================="
echo ""

if [ ! -f "$LESSONS_FILE" ]; then
    echo "No lessons.json found at $LESSONS_FILE"
    echo "Run init.sh first, then capture some events and extract lessons."
    exit 0
fi

if [ ! -f "$RULES_FILE" ]; then
    echo "No rules.json found at $RULES_FILE"
    echo "Run init.sh first."
    exit 1
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

python3 - "$RULES_FILE" "$LESSONS_FILE" "$DRY_RUN" "$SCRIPT_NAME" "$LEARNING_DIR" << 'PYTHON'
import json, sys, fcntl, os
from datetime import date, datetime

rules_path = sys.argv[1]
lessons_path = sys.argv[2]
dry_run = sys.argv[3] == "--dry-run" if len(sys.argv) > 3 else False
script_name = sys.argv[4]
learning_dir = sys.argv[5]

try:
    # Acquire lock for reading rules
    with open(rules_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    # Acquire lock for reading lessons
    with open(lessons_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        lessons_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading files: {e}")
    sys.exit(1)

rules = rules_data.get("rules", [])
lessons = lessons_data.get("lessons", [])

# Find candidates: confidence_score >= 0.9 AND times_applied >= 3, or legacy: times_applied >= 3
candidates = [l for l in lessons if not l.get("promoted_to_rule") and l.get("times_applied", 0) >= 3 and l.get("confidence_score", 1.0) >= 0.9]

if not candidates:
    print("No lessons ready for promotion.")
    print(f"\nLesson status:")
    for l in lessons:
        status = f"promoted -> {l['promoted_to_rule']}" if l.get("promoted_to_rule") else f"applied {l.get('times_applied', 0)}x (need 3)"
        print(f"  {l['id']}: {status}")
    sys.exit(0)

print(f"Found {len(candidates)} candidate(s) for promotion:\n")

# Generate new rule IDs
existing_ids = []
for r in rules:
    rid = r.get("id", "")
    if rid.startswith("R-"):
        try:
            existing_ids.append(int(rid.split("-")[1]))
        except (ValueError, IndexError):
            pass
next_id = max(existing_ids) + 1 if existing_ids else 1

promoted = []
for lesson in candidates:
    rule_id = f"R-{next_id:03d}"
    
    # Determine rule type from lesson text
    rule_text = lesson.get("lesson", "")
    lower = rule_text.lower()
    if any(w in lower for w in ["always", "must", "stop", "immediately"]):
        rule_type = "MUST"
    elif any(w in lower for w in ["never", "don't", "avoid"]):
        rule_type = "NEVER"
    elif any(w in lower for w in ["check", "verify", "search"]):
        rule_type = "CHECK"
    else:
        rule_type = "PREFER"
    
    today_str = str(date.today())
    new_rule = {
        "id": rule_id,
        "type": rule_type,
        "category": lesson.get("category", "general"),
        "rule": rule_text,
        "reason": lesson.get("context", f"Promoted from lesson {lesson['id']}"),
        "created": today_str,
        "source_lesson": lesson["id"],
        "violations": 0,
        "last_checked": today_str,
        "last_validated": today_str,
        "validation_count": 0,
        "confidence_score": lesson.get("confidence_score", 0.9)
    }
    
    print(f"  {lesson['id']} -> {rule_id} [{rule_type}]")
    print(f"  Rule: {rule_text}")
    print(f"  Applied: {lesson.get('times_applied', 0)}x, Saved: {lesson.get('times_saved', 0)}x")
    print()
    
    if not dry_run:
        rules.append(new_rule)
        lesson["promoted_to_rule"] = rule_id
        promoted.append((lesson["id"], rule_id))
    
    next_id += 1

if dry_run:
    print("[DRY RUN] No changes written.")
else:
    # Write rules.json with locking
    rules_data["rules"] = rules
    rules_data["updated"] = str(date.today())
    try:
        with open(rules_path, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(rules_data, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        print(f"ERROR: Failed to write rules.json: {e}")
        sys.exit(2)
    
    # Write lessons.json with locking
    lessons_data["lessons"] = lessons
    lessons_data["updated"] = str(date.today())
    try:
        with open(lessons_path, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(lessons_data, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        print(f"ERROR: Failed to write lessons.json: {e}")
        sys.exit(2)
    
    print(f"Promoted {len(promoted)} lesson(s) to rules.")
    for lid, rid in promoted:
        print(f"  {lid} -> {rid}")

PYTHON

exit_code=$?

# Release lock
exec 200>&-

exit $exit_code

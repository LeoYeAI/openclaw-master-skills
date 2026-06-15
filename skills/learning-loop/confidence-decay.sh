#!/bin/bash
# Learning Loop - Confidence Decay Calculator (v1.4.0)
# Applies Ebbinghaus-inspired exponential decay to rule/lesson confidence scores
# Rules that haven't been validated recently lose confidence over time
# Usage: bash confidence-decay.sh [workspace-dir] [--dry-run]
# Returns: 0 on success, 1 on configuration error, 2 on data corruption, 3 on lock contention
# Schedule: Weekly cron
# Dependencies: rules.json, lessons.json
# Side Effects: Updates rules.json and lessons.json (with file locking)

set -o pipefail

SCRIPT_NAME="confidence-decay.sh"
VERSION="1.4.0"

WORKSPACE=""
DRY_RUN=""

# Parse args
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

echo "Learning Loop - Confidence Decay Calculator v$VERSION"
echo "======================================================"
echo ""

if [ ! -f "$RULES_FILE" ]; then
    echo "ERROR: rules.json not found at $RULES_FILE"
    echo "Run init.sh first."
    exit 1
fi

if [ ! -f "$LESSONS_FILE" ]; then
    echo "WARNING: lessons.json not found at $LESSONS_FILE"
    echo "Continuing with rules only."
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

python3 - "$RULES_FILE" "$LESSONS_FILE" "$DRY_RUN" "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYTHON'
import json, sys, math, fcntl, os
from datetime import datetime, date, timedelta

rules_path = sys.argv[1]
lessons_path = sys.argv[2]
dry_run = sys.argv[3] == "--dry-run" if len(sys.argv) > 3 else False
learning_dir = sys.argv[4]
script_name = sys.argv[5]

today = date.today()
today_str = str(today)

def decay_score(score, last_validated, model="ebbinghaus"):
    """
    Calculate decayed confidence score based on days since last validation.
    
    Models:
    - ebbinghaus: Exponential decay with floor at 0.3
      Formula: max(0.3, score * exp(-0.05 * days))
    - linear: Linear decay with floor at 0.3
      Formula: max(0.3, score - (0.01 * days))
    """
    if not last_validated:
        return score
    
    try:
        last_val_date = datetime.strptime(last_validated, "%Y-%m-%d").date()
        days = (today - last_val_date).days
    except (ValueError, TypeError):
        # Invalid date format, don't decay
        return score
    
    if days <= 0:
        return score
    
    if model == "ebbinghaus":
        # Exponential decay with floor at 0.3
        # After ~30 days, score decays to about 22% of original
        # After ~60 days, score decays to about 5% of original
        decay_factor = math.exp(-0.05 * days)
        return max(0.3, score * decay_factor)
    elif model == "linear":
        # Linear decay: loses 1% per day, floor at 0.3
        return max(0.3, score - (0.01 * days))
    else:
        return score

# ============================================================================
# PROCESS RULES
# ============================================================================

try:
    with open(rules_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"ERROR: Could not load rules.json: {e}")
    sys.exit(1)

rules = rules_data.get("rules", [])
rules_updated = 0
rules_flagged = []

print("Processing rules...")
print("-" * 60)

for rule in rules:
    rule_id = rule.get("id", "unknown")
    
    # Ensure required fields exist (backfill for older rules)
    if "last_validated" not in rule:
        rule["last_validated"] = rule.get("created", today_str)
    if "validation_count" not in rule:
        rule["validation_count"] = 0
    if "confidence_score" not in rule:
        rule["confidence_score"] = 0.9  # Default starting confidence
    
    old_score = rule["confidence_score"]
    last_validated = rule["last_validated"]
    
    # Calculate decay
    new_score = decay_score(old_score, last_validated, model="ebbinghaus")
    new_score = round(new_score, 2)
    
    if new_score != old_score:
        rule["confidence_score"] = new_score
        rules_updated += 1
        
        # Calculate days since validation for reporting
        try:
            last_val_date = datetime.strptime(last_validated, "%Y-%m-%d").date()
            days_since = (today - last_val_date).days
        except:
            days_since = "unknown"
        
        print(f"  {rule_id}: {old_score:.2f} → {new_score:.2f} ({days_since} days since validation)")
    
    # Flag rules below 0.5 confidence for review
    if new_score < 0.5:
        rule["review_flagged"] = True
        rules_flagged.append({
            "id": rule_id,
            "confidence": new_score,
            "last_validated": last_validated,
            "rule": rule.get("rule", "")[:60]
        })
    else:
        rule["review_flagged"] = False

print(f"\nUpdated {rules_updated} rule(s)")

# ============================================================================
# PROCESS LESSONS
# ============================================================================

lessons_updated = 0
lessons_flagged = []

if lessons_path and os.path.exists(lessons_path):
    try:
        with open(lessons_path, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            lessons_data = json.load(f)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"WARNING: Could not load lessons.json: {e}")
        lessons_data = None
    
    if lessons_data:
        lessons = lessons_data.get("lessons", [])
        
        print("\nProcessing lessons...")
        print("-" * 60)
        
        for lesson in lessons:
            lesson_id = lesson.get("id", "unknown")
            
            # Ensure required fields exist (backfill for older lessons)
            if "last_validated" not in lesson:
                lesson["last_validated"] = lesson.get("created", today_str)
            if "validation_count" not in lesson:
                lesson["validation_count"] = 0
            if "confidence_score" not in lesson:
                lesson["confidence_score"] = lesson.get("confidence", 0.5)
                if isinstance(lesson["confidence_score"], str):
                    # Convert string confidence to numeric
                    confidence_map = {"testing": 0.5, "proven": 0.9, "high": 0.8, "medium": 0.6, "low": 0.4}
                    lesson["confidence_score"] = confidence_map.get(lesson["confidence_score"].lower(), 0.5)
            
            old_score = lesson["confidence_score"]
            last_validated = lesson["last_validated"]
            
            # Calculate decay
            new_score = decay_score(old_score, last_validated, model="ebbinghaus")
            new_score = round(new_score, 2)
            
            if new_score != old_score:
                lesson["confidence_score"] = new_score
                lessons_updated += 1
                
                # Calculate days since validation for reporting
                try:
                    last_val_date = datetime.strptime(last_validated, "%Y-%m-%d").date()
                    days_since = (today - last_val_date).days
                except:
                    days_since = "unknown"
                
                print(f"  {lesson_id}: {old_score:.2f} → {new_score:.2f} ({days_since} days since validation)")
            
            # Flag lessons below 0.5 confidence for review
            if new_score < 0.5 and not lesson.get("promoted_to_rule"):
                lesson["review_flagged"] = True
                lessons_flagged.append({
                    "id": lesson_id,
                    "confidence": new_score,
                    "last_validated": last_validated,
                    "lesson": lesson.get("lesson", "")[:60]
                })
            else:
                lesson["review_flagged"] = False
        
        print(f"\nUpdated {lessons_updated} lesson(s)")

# ============================================================================
# SAVE CHANGES
# ============================================================================

if dry_run:
    print("\n[DRY RUN] No changes written.")
else:
    # Save rules with locking
    rules_data["updated"] = today_str
    try:
        with open(rules_path, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(rules_data, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        print(f"\n✓ Saved {len(rules)} rules")
    except Exception as e:
        print(f"ERROR: Failed to write rules.json: {e}")
        sys.exit(2)
    
    # Save lessons with locking
    if lessons_path and os.path.exists(lessons_path) and lessons_data:
        lessons_data["updated"] = today_str
        try:
            with open(lessons_path, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(lessons_data, f, indent=2)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            print(f"✓ Saved {len(lessons_data.get('lessons', []))} lessons")
        except Exception as e:
            print(f"ERROR: Failed to write lessons.json: {e}")
            sys.exit(2)

# ============================================================================
# GENERATE STALE RULES REPORT
# ============================================================================

print("\n" + "=" * 60)
print("STALE RULES REPORT")
print("=" * 60)

if rules_flagged:
    print(f"\n⚠️  {len(rules_flagged)} rule(s) flagged for review (confidence < 0.5):")
    for r in sorted(rules_flagged, key=lambda x: x["confidence"]):
        print(f"\n  {r['id']}: {r['rule']}")
        print(f"    Confidence: {r['confidence']:.2f}")
        print(f"    Last validated: {r['last_validated']}")
else:
    print("\n✅ No rules flagged for review. All rules have confidence ≥ 0.5")

if lessons_flagged:
    print(f"\n⚠️  {len(lessons_flagged)} lesson(s) flagged for review (confidence < 0.5):")
    for l in sorted(lessons_flagged, key=lambda x: x["confidence"]):
        print(f"\n  {l['id']}: {l['lesson']}")
        print(f"    Confidence: {l['confidence']:.2f}")
        print(f"    Last validated: {l['last_validated']}")
else:
    print("\n✅ No lessons flagged for review. All lessons have confidence ≥ 0.5")

print("\n" + "=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)

if rules_flagged or lessons_flagged:
    print("\n1. Review flagged items above - are they still valid?")
    print("2. If valid: Reset confidence by validating the rule/lesson again")
    print("3. If invalid: Deprecate or remove the rule/lesson")
    print("4. Consider running this script weekly to catch stale rules early")
else:
    print("\n• No action needed. Confidence scores are healthy.")
    print("• Continue running this script weekly to maintain confidence accuracy.")

# Summary statistics
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total rules: {len(rules)}")
print(f"Rules updated: {rules_updated}")
print(f"Rules flagged: {len(rules_flagged)}")
if lessons_path and os.path.exists(lessons_path) and lessons_data:
    print(f"Total lessons: {len(lessons_data.get('lessons', []))}")
    print(f"Lessons updated: {lessons_updated}")
    print(f"Lessons flagged: {len(lessons_flagged)}")
print(f"Decay model: Ebbinghaus (exponential, floor at 0.3)")
print(f"Decay rate: ~5% per day")

PYTHON

exit_code=$?

# Release lock
exec 200>&-

exit $exit_code

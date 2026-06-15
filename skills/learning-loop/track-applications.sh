#!/bin/bash
# Learning Loop - Lesson Application Tracker
# Scans events.jsonl for success events that match existing lessons/rules,
# indicating the lesson was successfully applied.
# Usage: bash track-applications.sh [workspace-dir]
# Returns: 0 on success, 1 on configuration error
# Schedule: Daily cron
# Dependencies: events.jsonl, lessons.json, rules.json
# Side Effects: Updates lessons.json (with file locking), writes to parse-errors.jsonl

set -o pipefail

SCRIPT_NAME="track-applications.sh"
WORKSPACE="${1:-$(pwd)}"
LEARNING_DIR="$WORKSPACE/memory/learning"
EVENTS_FILE="$LEARNING_DIR/events.jsonl"
LESSONS_FILE="$LEARNING_DIR/lessons.json"
RULES_FILE="$LEARNING_DIR/rules.json"

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
    echo "ERROR: events.jsonl not found at $EVENTS_FILE"
    exit 1
fi

if [[ ! -f "$LESSONS_FILE" ]]; then
    echo "ERROR: lessons.json not found at $LESSONS_FILE"
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

python3 - "$EVENTS_FILE" "$LESSONS_FILE" "$RULES_FILE" "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYTHON'
import json, sys, re, fcntl, os
from datetime import date, datetime

events_file = sys.argv[1]
lessons_file = sys.argv[2]
rules_file = sys.argv[3]
learning_dir = sys.argv[4]
script_name = sys.argv[5]
today = str(date.today())

# Load events with error handling
try:
    with open(events_file) as f:
        events = []
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
                    # Log parse error
                    error_entry = {
                        "ts": datetime.now().isoformat(),
                        "error": str(e),
                        "line": line[:200],
                        "script": script_name
                    }
                    errors_file = os.path.join(learning_dir, "parse-errors.jsonl")
                    with open(errors_file, "a") as ef:
                        ef.write(json.dumps(error_entry) + "\n")
except FileNotFoundError:
    print("No events file.")
    sys.exit(0)

# Load lessons with file locking
try:
    with open(lessons_file, "r+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        lessons_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"No lessons file or invalid: {e}")
    sys.exit(1)

# Load rules (read-only, but use lock for consistency)
try:
    with open(rules_file) as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        rules = rules_data.get('rules', [])
except (FileNotFoundError, json.JSONDecodeError):
    rules_data = None
    rules = []

lessons = lessons_data.get('lessons', [])

# Success and discovery events indicate a lesson was applied or knowledge was used
positive_events = [e for e in events if e.get('type') in ('success', 'discovery')]

print(f"Scanning {len(positive_events)} success/discovery events against {len(lessons)} lessons\n")

updates = 0

for lesson in lessons:
    l_cat = lesson.get('category', '')
    l_tags = set(lesson.get('tags', []))
    l_text = lesson.get('lesson', '').lower()
    l_words = set(re.findall(r'\w{3,}', l_text))
    
    matching_events = 0
    
    for e in positive_events:
        e_cat = e.get('category', '')
        e_tags = set(e.get('tags', []))
        e_solution = (e.get('solution', '') or '').lower()
        e_words = set(re.findall(r'\w{3,}', e_solution))
        
        # Score the match
        score = 0.0
        
        # Category match
        if e_cat == l_cat:
            score += 0.3
        
        # Tag overlap
        tag_overlap = e_tags & l_tags
        if tag_overlap:
            score += 0.2 * min(len(tag_overlap), 3)
        
        # Word overlap between lesson text and event solution
        word_overlap = l_words & e_words
        if word_overlap:
            score += 0.1 * min(len(word_overlap), 5)
        
        if score >= 0.5:
            matching_events += 1
    
    if matching_events > 0:
        old_applied = lesson.get('times_applied', 0)
        new_applied = max(old_applied, matching_events)
        
        if new_applied > old_applied:
            lesson['times_applied'] = new_applied
            updates += 1
            print(f"  {lesson['id']}: times_applied {old_applied} -> {new_applied} ({lesson['lesson'][:60]})")
        
        # Update confidence score based on application count
        if new_applied >= 5:
            lesson['confidence_score'] = min(lesson.get('confidence_score', 0.5) + 0.05, 1.0)
        elif new_applied >= 3:
            lesson['confidence_score'] = min(lesson.get('confidence_score', 0.5) + 0.1, 1.0)

# Save with file locking
if updates > 0:
    lessons_data['updated'] = today
    try:
        with open(lessons_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(lessons_data, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        print(f"\nUpdated {updates} lessons")
    except Exception as e:
        print(f"ERROR: Failed to write lessons.json: {e}")
        sys.exit(2)
else:
    print("No updates needed - application counts are current")

# Summary
print(f"\nLesson application summary:")
for l in sorted(lessons, key=lambda x: -x.get('times_applied', 0)):
    applied = l.get('times_applied', 0)
    conf = l.get('confidence_score', 0)
    promoted = l.get('promoted_to_rule', '')
    status = f"-> {promoted}" if promoted else f"(conf: {conf:.2f}, need 3+apps & 0.9+conf)"
    print(f"  {l['id']}: {applied}x applied {status} - {l['lesson'][:50]}")

PYTHON

exit_code=$?

# Release lock
exec 200>&-

exit $exit_code

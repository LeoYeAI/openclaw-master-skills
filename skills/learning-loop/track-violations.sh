#!/bin/bash
# Learning Loop - Violation Auto-Tracker
# Scans events.jsonl for mistakes that match existing rule categories
# and auto-increments violation counts on the matching rules.
# Also links events to specific rules when tags overlap.
# Usage: bash track-violations.sh [workspace-dir]
# Returns: 0 on success, 1 on configuration error
# Schedule: Daily cron
# Dependencies: events.jsonl, rules.json
# Side Effects: Updates rules.json (with file locking), writes to parse-errors.jsonl

set -o pipefail

SCRIPT_NAME="track-violations.sh"
WORKSPACE="${1:-$(pwd)}"
LEARNING_DIR="$WORKSPACE/memory/learning"
EVENTS_FILE="$LEARNING_DIR/events.jsonl"
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

if [[ ! -f "$RULES_FILE" ]]; then
    echo "ERROR: rules.json not found at $RULES_FILE"
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

python3 - "$EVENTS_FILE" "$RULES_FILE" "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYTHON'
import json, sys, re, fcntl, os
from datetime import date, datetime

events_file = sys.argv[1]
rules_file = sys.argv[2]
learning_dir = sys.argv[3]
script_name = sys.argv[4]
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
    print("No events file found.")
    sys.exit(0)

# Load rules with file locking
try:
    with open(rules_file, "r+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        rules_data = json.load(f)
        rules = rules_data['rules']
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"No rules file found or invalid: {e}")
    sys.exit(1)

# Build rule lookup: category -> list of rules
# Also build keyword index from rule text for fuzzy matching
rule_by_cat = {}
for r in rules:
    cat = r['category']
    if cat not in rule_by_cat:
        rule_by_cat[cat] = []
    rule_by_cat[cat].append(r)

# Find mistake events
mistakes = [e for e in events if e.get('type') in ('mistake', 'bug-fix')]

print(f"Scanning {len(mistakes)} mistake/bug-fix events against {len(rules)} rules\n")

violations_found = 0
linked = []

for m in mistakes:
    m_cat = m.get('category', '')
    m_tags = set(m.get('tags', []))
    m_problem = (m.get('problem', '') or '').lower()
    m_ts = m.get('ts', '')
    
    # Check if any rules in this category match
    matching_rules = rule_by_cat.get(m_cat, [])
    
    for r in matching_rules:
        rule_text = r['rule'].lower()
        rule_id = r['id']
        
        # Score the match: category match + keyword overlap
        score = 0.5  # Base score for category match
        
        # Check for keyword overlap between event and rule
        rule_words = set(re.findall(r'\w+', rule_text))
        problem_words = set(re.findall(r'\w+', m_problem))
        tag_overlap = m_tags & rule_words
        word_overlap = problem_words & rule_words
        
        if tag_overlap:
            score += 0.2 * len(tag_overlap)
        if word_overlap:
            score += 0.1 * min(len(word_overlap), 5)
        
        if score >= 0.9:  # Threshold for counting as violation (tight to avoid false positives)
            # Check if this violation was already counted
            # (simple heuristic: don't double-count same timestamp)
            last_violation = r.get('_last_violation_ts', '')
            if m_ts != last_violation:
                r['violations'] = r.get('violations', 0) + 1
                r['last_checked'] = today
                r['_last_violation_ts'] = m_ts
                violations_found += 1
                linked.append({
                    'rule': rule_id,
                    'event_ts': m_ts,
                    'score': round(score, 2),
                    'problem': m_problem[:80]
                })

# Clean temp fields
for r in rules:
    r.pop('_last_violation_ts', None)

# Save with file locking
if violations_found > 0:
    rules_data['updated'] = today
    try:
        with open(rules_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(rules_data, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        print(f"ERROR: Failed to write rules.json: {e}")
        sys.exit(2)

# Report
print(f"Violations found: {violations_found}")
if linked:
    print("\nLinked violations:")
    for v in linked:
        print(f"  {v['rule']} (score {v['score']}): {v['problem']}")

# Summary
print(f"\nRule violation counts:")
for r in sorted(rules, key=lambda x: x.get('violations', 0), reverse=True):
    v = r.get('violations', 0)
    if v > 0:
        print(f"  {r['id']} ({r['category']}): {v} violations - {r['rule'][:60]}")

PYTHON

exit_code=$?

# Release lock (automatic on exit, but explicit is cleaner)
exec 200>&-

exit $exit_code

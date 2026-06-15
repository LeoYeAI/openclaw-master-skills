#!/bin/bash
# Learning Loop - Pattern Detector
# Analyzes events.jsonl for recurring patterns, potential rule promotions,
# regressions, and anomalies. Outputs a weekly report.
# Usage: bash detect-patterns.sh [workspace-dir] [days-back]
# Returns: 0 on success, 1 on configuration error, 2 on data corruption
# Schedule: Weekly cron
# Dependencies: events.jsonl, rules.json, lessons.json
# Side Effects: Writes to weekly/ directory, updates parse-errors.jsonl

set -o pipefail

SCRIPT_NAME="detect-patterns.sh"
WORKSPACE="${1:-$(pwd)}"
DAYS_BACK="${2:-7}"
LEARNING_DIR="$WORKSPACE/memory/learning"
EVENTS_FILE="$LEARNING_DIR/events.jsonl"
RULES_FILE="$LEARNING_DIR/rules.json"
LESSONS_FILE="$LEARNING_DIR/lessons.json"
WEEKLY_DIR="$LEARNING_DIR/weekly"

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
    echo "Run init.sh first to initialize the learning loop."
    exit 1
fi

# Create weekly directory if needed
mkdir -p "$WEEKLY_DIR"

WEEK=$(date +%Y-W%V)
REPORT="$WEEKLY_DIR/$WEEK.md"

echo "# Learning Loop - Pattern Detection Report" > "$REPORT"
echo "_Generated: $(date +%Y-%m-%d\ %H:%M)_" >> "$REPORT"
echo "_Period: Last $DAYS_BACK days_" >> "$REPORT"
echo "" >> "$REPORT"

# Count total events
if [ -f "$EVENTS_FILE" ]; then
    TOTAL_EVENTS=$(wc -l < "$EVENTS_FILE" | tr -d ' ')
else
    TOTAL_EVENTS=0
fi

echo "## Overview" >> "$REPORT"
echo "- Total events: $TOTAL_EVENTS" >> "$REPORT"

if [ "$TOTAL_EVENTS" -eq 0 ]; then
    echo "" >> "$REPORT"
    echo "No events captured yet. Start logging debugging sessions, mistakes, and successes." >> "$REPORT"
    cat "$REPORT"
    exit 0
fi

# Count by type
echo "- By type:" >> "$REPORT"
for TYPE in mistake success debug_session feedback discovery; do
    COUNT=$(grep -c "\"type\":\"$TYPE\"" "$EVENTS_FILE" 2>/dev/null || echo 0)
    COUNT=$(echo "$COUNT" | tr -d '[:space:]')
    if [ "$COUNT" -gt 0 ] 2>/dev/null; then
        echo "  - $TYPE: $COUNT" >> "$REPORT"
    fi
done

# Count by category
echo "- By category:" >> "$REPORT"
python3 - "$EVENTS_FILE" "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYCAT' >> "$REPORT"
import json, sys, os
from datetime import datetime
from collections import Counter

events_file = sys.argv[1]
learning_dir = sys.argv[2]
script_name = sys.argv[3]

cats = Counter()
parse_errors = []

try:
    with open(events_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
                cats[evt.get("category", "unknown")] += 1
            except json.JSONDecodeError as e:
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
        print(f"  ⚠️  {len(parse_errors)} parse errors logged to parse-errors.jsonl", file=sys.stderr)
    
    for cat, count in cats.most_common():
        print(f"  - {cat}: {count}")
except FileNotFoundError:
    print("  - (no events file)")
PYCAT

# Count rules
if [ -f "$RULES_FILE" ]; then
    RULE_COUNT=$(python3 -c "import json; print(len(json.load(open('$RULES_FILE')).get('rules',[])))" 2>/dev/null || echo "?")
else
    RULE_COUNT=0
fi
echo "- Active rules: $RULE_COUNT" >> "$REPORT"

# Count lessons
if [ -f "$LESSONS_FILE" ]; then
    LESSON_COUNT=$(python3 -c "import json; print(len(json.load(open('$LESSONS_FILE')).get('lessons',[])))" 2>/dev/null || echo "0")
else
    LESSON_COUNT=0
fi
echo "- Captured lessons: $LESSON_COUNT" >> "$REPORT"
echo "" >> "$REPORT"

# Pattern detection: find repeated tags
echo "## Tag Clusters (potential patterns)" >> "$REPORT"
python3 - "$EVENTS_FILE" "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYTAGS' >> "$REPORT"
import json, sys, os
from datetime import datetime
from collections import Counter

events_file = sys.argv[1]
learning_dir = sys.argv[2]
script_name = sys.argv[3]

tags = Counter()
parse_errors = []

try:
    with open(events_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
                for tag in evt.get("tags", []):
                    tags[tag] += 1
            except json.JSONDecodeError as e:
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
    
    clusters = [(tag, count) for tag, count in tags.most_common() if count >= 2]
    if clusters:
        for tag, count in clusters:
            marker = " **[PATTERN]**" if count >= 3 else ""
            print(f"- `{tag}`: {count} occurrences{marker}")
    else:
        print("No tag clusters found (need 2+ occurrences)")
except FileNotFoundError:
    print("No events file found")
PYTAGS
echo "" >> "$REPORT"

# Rule promotion candidates: lessons with 3+ applications not yet promoted
echo "## Rule Promotion Candidates" >> "$REPORT"
if [ -f "$LESSONS_FILE" ]; then
    python3 - "$LESSONS_FILE" << 'PYPROMO' >> "$REPORT"
import json, sys, fcntl, os
from datetime import date

lessons_path = sys.argv[1]

try:
    # Acquire lock for reading
    with open(lessons_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        lessons_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    lessons = lessons_data.get("lessons", [])
    candidates = [l for l in lessons if l.get("times_applied", 0) >= 3 and not l.get("promoted_to_rule")]
    if candidates:
        for l in candidates:
            print(f"- **{l['id']}**: {l['lesson']}")
            print(f"  - Applied {l['times_applied']}x, saved {l.get('times_saved', 0)}x")
            print(f"  - Category: {l['category']}/{l.get('subcategory', 'general')}")
    else:
        print("No lessons ready for rule promotion (need 3+ applications without existing rule)")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Could not read lessons file: {e}")
PYPROMO
else
    echo "No lessons.json found. Run init.sh to create it." >> "$REPORT"
fi
echo "" >> "$REPORT"

# Regression detection: events matching existing rules (enhanced)
echo "## Regression Check" >> "$REPORT"
python3 - "$RULES_FILE" "$EVENTS_FILE" "$DAYS_BACK" "$LEARNING_DIR" "$SCRIPT_NAME" << 'PYREGRESS' >> "$REPORT"
import json, sys, os, fcntl
from datetime import datetime, timedelta

rules_file = sys.argv[1]
events_file = sys.argv[2]
days_back = int(sys.argv[3])
learning_dir = sys.argv[4]
script_name = sys.argv[5]

cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
parse_errors = []

try:
    # Acquire lock for reading rules
    with open(rules_file, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules = json.load(f).get("rules", [])
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    # Read events with error handling
    events = []
    with open(events_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
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
    
    # Find recent mistakes that match rule categories
    rule_cats = {r["category"] for r in rules}
    mistakes = [e for e in events if e.get("type") == "mistake" and e.get("ts", "") >= cutoff]
    
    regressions = []
    for m in mistakes:
        if m.get("category") in rule_cats:
            # Find if there's a rule that was supposed to prevent this
            matching_rules = [r for r in rules if r["category"] == m.get("category")]
            for r in matching_rules:
                created = r.get("created", "")
                if created and created < m.get("ts", "")[:10]:
                    days_since_fix = (datetime.now() - datetime.strptime(created, "%Y-%m-%d")).days
                    regressions.append({
                        "event": m,
                        "rule": r,
                        "days_since_fix": days_since_fix,
                        "likely_cause": "context_drift" if days_since_fix > 60 else "rule_violation"
                    })
    
    if regressions:
        for r in regressions:
            m = r["event"]
            rule = r["rule"]
            print(f"- **REGRESSION** in {m['category']}: {m.get('problem', 'unknown')}")
            print(f"  - Timestamp: {m.get('ts', 'unknown')}")
            print(f"  - Rule violated: {rule['id']} (created {r['days_since_fix']} days ago)")
            print(f"  - Likely cause: {r['likely_cause']}")
    else:
        print("No regressions detected. Rules are holding.")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Could not check regressions: {e}")
PYREGRESS
echo "" >> "$REPORT"

# Anomaly Detection (NEW v1.4.0)
echo "## Anomaly Detection" >> "$REPORT"
python3 - "$EVENTS_FILE" "$DAYS_BACK" "$SCRIPT_NAME" "$LEARNING_DIR" << 'PYANOMALY' >> "$REPORT"
import json, sys, os
from datetime import datetime, timedelta
from statistics import mean, stdev
from collections import defaultdict

events_file = sys.argv[1]
days_back = int(sys.argv[2])
script_name = sys.argv[3]
learning_dir = sys.argv[4]

# Parse events
events = []
parse_errors = []
try:
    with open(events_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
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
except FileNotFoundError:
    print("No events file found for anomaly detection.")
    sys.exit(0)

# Calculate daily counts over rolling 7-day window
daily_counts = defaultdict(int)
cutoff = datetime.now() - timedelta(days=days_back)

for e in events:
    ts = e.get("ts", "")
    if ts:
        try:
            event_date = datetime.fromisoformat(ts.replace("Z", "+00:00").replace("+00:00", ""))
            if event_date >= cutoff:
                day_key = event_date.strftime("%Y-%m-%d")
                daily_counts[day_key] += 1
        except:
            pass

if len(daily_counts) < 3:
    print("Not enough data for anomaly detection (need 3+ days).")
    sys.exit(0)

# Z-score analysis
counts = list(daily_counts.values())
avg = mean(counts)
std = stdev(counts) if len(counts) > 1 else 0

if std == 0:
    print("No variance in daily counts - no anomalies detected.")
    sys.exit(0)

anomalies = []
for day, count in sorted(daily_counts.items()):
    z_score = (count - avg) / std
    if abs(z_score) > 2.5:  # 99% confidence threshold
        anomalies.append({
            "day": day,
            "count": count,
            "z_score": round(z_score, 2),
            "severity": "high" if abs(z_score) > 3 else "medium",
            "direction": "spike" if z_score > 0 else "drop"
        })

if anomalies:
    print(f"⚠️  Detected {len(anomalies)} anomaly/anomalies:")
    for a in anomalies:
        emoji = "📈" if a["direction"] == "spike" else "📉"
        print(f"- {emoji} **{a['day']}**: {a['count']} events (z-score: {a['z_score']}, {a['severity']})")
else:
    print("✅ No anomalies detected. Event volume is within normal range.")
    print(f"   Daily average: {avg:.1f}, std dev: {std:.1f}")
PYANOMALY
echo "" >> "$REPORT"

# Self-audit summary
echo "## Self-Audit (Meta-Learning)" >> "$REPORT"
python3 - "$WORKSPACE" "$SCRIPT_NAME" "$LEARNING_DIR" << 'PYSELF' >> "$REPORT"
import json, os, sys, fcntl
from datetime import datetime

workspace = sys.argv[1]
script_name = sys.argv[2]
learning_dir = sys.argv[3]

events_file = os.path.join(learning_dir, "events.jsonl")

checks = []
parse_errors = []

# Check 1: Are events being captured regularly?
try:
    with open(events_file) as f:
        events = []
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
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
        
        if len(events) == 0:
            checks.append("- ❌ No events captured. The loop is not running.")
        elif len(events) < 3:
            checks.append(f"- ⚠️ Only {len(events)} events. Capture rate is low.")
        else:
            checks.append(f"- ✅ {len(events)} events captured. Capture is active.")
        
        # Check for event diversity
        types = set(e.get("type") for e in events)
        if len(types) < 2:
            checks.append(f"- ⚠️ Only event type(s): {', '.join(types)}. Capture more event types.")
        else:
            checks.append(f"- ✅ Event type diversity: {', '.join(sorted(types))}")

except FileNotFoundError:
    checks.append("- ❌ events.jsonl not found. System not initialized.")

# Check 2: Are rules being loaded?
rules_path = os.path.join(learning_dir, "rules.json")
try:
    with open(rules_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules = json.load(f).get("rules", [])
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    checks.append(f"- ✅ {len(rules)} rules in rules.json")
except (FileNotFoundError, json.JSONDecodeError):
    checks.append("- ❌ rules.json not found or invalid")

# Check 3: Are lessons being created?
lessons_path = os.path.join(learning_dir, "lessons.json")
try:
    with open(lessons_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        lessons = json.load(f).get("lessons", [])
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    checks.append(f"- ✅ {len(lessons)} lessons in lessons.json")
    unpromoted = [l for l in lessons if not l.get("promoted_to_rule")]
    checks.append(f"- ℹ️ {len(unpromoted)} lessons not yet promoted to rules")
except (FileNotFoundError, json.JSONDecodeError):
    checks.append("- ⚠️ lessons.json not found - run init.sh to create it")

# Check 4: Metrics freshness
metrics_path = os.path.join(learning_dir, "metrics.json")
try:
    with open(metrics_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        metrics = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    checks.append(f"- ✅ Metrics tracking since {metrics.get('started', 'unknown')}")
except (FileNotFoundError, json.JSONDecodeError):
    checks.append("- ⚠️ metrics.json missing or invalid")

for c in checks:
    print(c)
PYSELF
echo "" >> "$REPORT"

# Recommendations
echo "## Recommendations" >> "$REPORT"
echo "_Auto-generated action items:_" >> "$REPORT"
python3 - "$EVENTS_FILE" "$LESSONS_FILE" "$RULES_FILE" "$SCRIPT_NAME" "$LEARNING_DIR" << 'PYREC' >> "$REPORT"
import json, sys, os
from datetime import datetime

events_file = sys.argv[1]
lessons_file = sys.argv[2]
rules_file = sys.argv[3]
script_name = sys.argv[4]
learning_dir = sys.argv[5]

events = []
lessons = []
rules = []
parse_errors = []

try:
    with open(events_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
                    parse_errors.append({
                        "ts": datetime.now().isoformat(),
                        "error": str(e),
                        "line": line[:200],
                        "script": script_name
                    })
except (FileNotFoundError, json.JSONDecodeError):
    pass

try:
    with open(lessons_file) as f:
        lessons = json.load(f).get("lessons", [])
except (FileNotFoundError, json.JSONDecodeError):
    pass

try:
    with open(rules_file) as f:
        rules = json.load(f).get("rules", [])
except (FileNotFoundError, json.JSONDecodeError):
    pass

# Write parse errors if any
if parse_errors:
    errors_file = os.path.join(learning_dir, "parse-errors.jsonl")
    with open(errors_file, "a") as ef:
        for err in parse_errors:
            ef.write(json.dumps(err) + "\n")

recs = []
n = 0

unpromoted_high_apply = [l for l in lessons if l.get("times_applied", 0) >= 3 and not l.get("promoted_to_rule")]
if unpromoted_high_apply:
    n += 1
    recs.append(f"{n}. **Promote {len(unpromoted_high_apply)} lesson(s) to rules** - they have 3+ successful applications")

low_apply = [l for l in lessons if l.get("times_applied", 0) == 0]
if low_apply:
    n += 1
    recs.append(f"{n}. **Review {len(low_apply)} unapplied lessons** - are they still relevant?")

if len(events) > 0 and len(lessons) > 0 and len(lessons) < len(events) * 0.5:
    n += 1
    recs.append(f"{n}. **Extract more lessons** - {len(events)} events but only {len(lessons)} lessons ({len(lessons)/len(events)*100:.0f}% coverage)")

if len(events) == 0:
    n += 1
    recs.append(f"{n}. **Start capturing events** - the loop needs data to work")

if len(lessons) == 0 and len(events) >= 3:
    n += 1
    recs.append(f"{n}. **Extract lessons from events** - you have {len(events)} events but no structured lessons yet")

if not recs:
    recs.append("No urgent recommendations. System is healthy.")

for r in recs:
    print(f"- {r}")
PYREC

echo "" >> "$REPORT"
echo "---" >> "$REPORT"
echo "_Report saved to: $REPORT_" >> "$REPORT"

cat "$REPORT"

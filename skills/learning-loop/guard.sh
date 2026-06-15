#!/bin/bash
# Learning Loop - Action Guard
# Call BEFORE any risky action. Does two things:
# 1. Surfaces relevant rules (prevention)
# 2. Logs the check so saves can be tracked (measurement)
#
# Usage: bash guard.sh [workspace] "action description"
# Returns: relevant rules + guard ID for save tracking
#
# After the action succeeds, call:
#   bash guard.sh [workspace] --save <guard-id>
# This increments times_saved on matched lessons.

set -o pipefail

WORKSPACE="${1:-$(pwd)}"
ACTION="${2:-}"
LEARNING_DIR="$WORKSPACE/memory/learning"
GUARD_LOG="$LEARNING_DIR/guard-log.jsonl"

# Handle --save mode
if [ "$ACTION" = "--save" ]; then
    GUARD_ID="${3:-}"
    if [ -z "$GUARD_ID" ]; then
        echo "Usage: bash guard.sh [workspace] --save <guard-id>"
        exit 1
    fi
    
    python3 - "$GUARD_LOG" "$LEARNING_DIR/lessons.json" "$GUARD_ID" << 'PYSAVE'
import json, sys
from datetime import date

guard_log = sys.argv[1]
lessons_file = sys.argv[2]
guard_id = sys.argv[3]

# Find the guard entry
entry = None
try:
    with open(guard_log) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get('id') == guard_id:
                entry = e
                break
except FileNotFoundError:
    print(f"No guard log found.")
    sys.exit(1)

if not entry:
    print(f"Guard ID {guard_id} not found in log.")
    sys.exit(1)

if entry.get('save_logged'):
    print(f"Save already logged for {guard_id}")
    sys.exit(0)

# Increment times_saved on matched lessons
matched_rules = entry.get('matched_rules', [])
if not matched_rules:
    print("No rules were matched for this guard check. Nothing to save.")
    sys.exit(0)

try:
    with open(lessons_file) as f:
        lessons_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print("Could not load lessons.json")
    sys.exit(1)

# Find lessons linked to matched rules
rule_ids = set(matched_rules)
saves = 0
for lesson in lessons_data.get('lessons', []):
    promoted_to = lesson.get('promoted_to_rule')
    if promoted_to and promoted_to in rule_ids:
        lesson['times_saved'] = lesson.get('times_saved', 0) + 1
        saves += 1
        print(f"  +1 save: {lesson['id']} ({promoted_to}) - {lesson['lesson'][:50]}")

if saves > 0:
    lessons_data['updated'] = str(date.today())
    with open(lessons_file, 'w') as f:
        json.dump(lessons_data, f, indent=2)

# Mark guard entry as save-logged (rewrite log)
entries = []
try:
    with open(guard_log) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get('id') == guard_id:
                e['save_logged'] = True
                e['outcome'] = 'success'
            entries.append(e)
except FileNotFoundError:
    pass

with open(guard_log, 'w') as f:
    for e in entries:
        f.write(json.dumps(e) + '\n')

print(f"\nSave logged: {saves} lesson(s) credited for guard {guard_id}")
PYSAVE
    exit $?
fi

# Normal mode: check rules and log the guard
if [ -z "$ACTION" ]; then
    echo "Usage: bash guard.sh [workspace] \"action description\""
    echo "       bash guard.sh [workspace] --save <guard-id>"
    exit 1
fi

python3 - "$LEARNING_DIR/rules.json" "$ACTION" "$GUARD_LOG" << 'PYGUARD'
import json, sys, re, uuid
from datetime import datetime, timezone

rules_file = sys.argv[1]
action = sys.argv[2].lower()
guard_log = sys.argv[3]

try:
    with open(rules_file) as f:
        rules = json.load(f).get('rules', [])
except (FileNotFoundError, json.JSONDecodeError):
    rules = []

# Keyword extraction
action_words = set(re.findall(r'\w{3,}', action))

# Category signals
CATEGORY_SIGNALS = {
    'memory': {'memory', 'remember', 'save', 'write', 'file', 'context', 'compaction'},
    'auth': {'account', 'register', 'login', 'credential', 'password', 'bitwarden', 'oauth', 'token', 'authenticate'},
    'infra': {'cron', 'config', 'infrastructure', 'deploy', 'server', 'nas', 'docker', 'tailscale', 'setup', 'install', 'configure', 'gateway', 'database'},
    'shell': {'command', 'bash', 'shell', 'find', 'grep', 'terminal', 'script', 'macos'},
    'social': {'moltbook', 'twitter', 'linkedin', 'post', 'comment', 'reply', 'engage', 'social', 'tweet'},
    'tooling': {'build', 'tool', 'api', 'secret', 'stripe', 'webhook', 'skill', 'pipeline'},
    'comms': {'greg', 'communicate', 'permission', 'ship', 'promote', 'advertise', 'fixed', 'done', 'ready', 'quality'},
    'learning': {'learn', 'event', 'rule', 'lesson', 'metric', 'audit'},
}

# Specific keyword triggers
SPECIFIC_TRIGGERS = {
    'moltbook': ['R-020', 'R-022', 'R-025', 'R-027'],
    'post': ['R-020', 'R-022', 'R-025', 'R-027', 'R-009'],
    'comment': ['R-020', 'R-022', 'R-025'],
    'colony': ['R-022', 'R-023', 'R-032'],
    'moltcities': ['R-022', 'R-023', 'R-032'],
    'moltbotden': ['R-022', 'R-023', 'R-032'],
    'engage': ['R-032', 'R-022', 'R-009'],
    'account': ['R-001'],
    'register': ['R-001'],
    'config': ['R-011', 'R-014'],
    'cron': ['R-005', 'R-023'],
    'ship': ['R-018'],
    'fixed': ['R-021'],
    'curl': ['R-020'],
    'retry': ['R-025'],
    'secret': ['R-026'],
    'find': ['R-004'],
    'advertise': ['R-018'],
    'promote': ['R-018'],
    'construction': ['R-031'],
    'checkout': ['R-034'],
    'git': ['R-034'],
}

scored = []
for r in rules:
    score = 0.0
    rule_text = r['rule'].lower()
    rule_words = set(re.findall(r'\w{3,}', rule_text))
    rule_cat = r['category']
    
    overlap = action_words & rule_words
    if overlap:
        score += min(len(overlap) * 0.15, 0.6)
    
    for cat, signals in CATEGORY_SIGNALS.items():
        if action_words & signals and cat == rule_cat:
            score += 0.3
            break
    
    if r['type'] in ('NEVER', 'MUST') and score > 0:
        score += 0.1
    
    if r.get('violations', 0) > 0 and score > 0:
        score += 0.1 * min(r['violations'], 3)
    
    for keyword, rule_ids in SPECIFIC_TRIGGERS.items():
        if keyword in action and r['id'] in rule_ids:
            score += 0.4
    
    if score >= 0.3:
        scored.append((r, round(score, 2)))

scored.sort(key=lambda x: -x[1])
top = scored[:6]

# Generate guard ID
guard_id = f"g-{datetime.now().strftime('%H%M%S')}-{uuid.uuid4().hex[:6]}"

# Log the guard check
entry = {
    'id': guard_id,
    'ts': datetime.now(timezone.utc).isoformat(),
    'action': action,
    'matched_rules': [r['id'] for r, s in top],
    'scores': {r['id']: s for r, s in top},
    'save_logged': False,
    'outcome': 'pending'
}

try:
    with open(guard_log, 'a') as f:
        f.write(json.dumps(entry) + '\n')
except Exception as e:
    pass  # Don't fail the check if logging fails

# Output
if top:
    print(f"🛡️ GUARD CHECK [{guard_id}]")
    print(f"Action: {action}")
    print(f"Rules to follow:")
    for r, s in top:
        prefix = "🚫" if r['type'] == 'NEVER' else "✅" if r['type'] == 'MUST' else "🔍" if r['type'] == 'CHECK' else "💡"
        viol = f" ⚠️{r['violations']}x broken" if r.get('violations') else ""
        print(f"  {prefix} {r['id']}: {r['rule'][:90]}{viol}")
    print(f"\nAfter success, log save: bash guard.sh [workspace] --save {guard_id}")
else:
    print(f"🛡️ GUARD CHECK [{guard_id}]: No specific rules match. Proceed with standard care.")

PYGUARD

#!/bin/bash
# Learning Loop - Dynamic Rule Checker
# Given an action description, finds and returns relevant rules.
# Designed to be called BEFORE risky operations.
# Usage: bash rule-check.sh [workspace-dir] "action description"
# Example: bash rule-check.sh . "creating a Moltbook post"
# Output: JSON with matching rules, sorted by relevance

set -o pipefail

WORKSPACE="${1:-$(pwd)}"
ACTION="${2:-}"
LEARNING_DIR="$WORKSPACE/memory/learning"
RULES_FILE="$LEARNING_DIR/rules.json"

if [ -z "$ACTION" ]; then
    echo "Usage: bash rule-check.sh [workspace] \"action description\""
    echo "Returns relevant rules for the given action."
    exit 1
fi

python3 - "$RULES_FILE" "$ACTION" << 'PYTHON'
import json, sys, re
from collections import defaultdict

rules_file = sys.argv[1]
action = sys.argv[2].lower()

try:
    with open(rules_file) as f:
        rules = json.load(f).get('rules', [])
except (FileNotFoundError, json.JSONDecodeError):
    print(json.dumps({"matches": [], "error": "Could not load rules.json"}))
    sys.exit(0)

# Keyword extraction from action
action_words = set(re.findall(r'\w{3,}', action))

# Category keywords mapping - maps action words to likely categories
CATEGORY_SIGNALS = {
    'memory': {'memory', 'remember', 'save', 'write', 'file', 'context', 'compaction', 'now.md', 'memory.md'},
    'auth': {'account', 'register', 'login', 'credential', 'password', 'bitwarden', 'oauth', 'api key', 'token', 'authenticate', 'sign up'},
    'infra': {'cron', 'config', 'infrastructure', 'deploy', 'server', 'nas', 'docker', 'tailscale', 'setup', 'install', 'configure', 'gateway', 'database', 'redis', 'qdrant'},
    'shell': {'command', 'bash', 'shell', 'find', 'grep', 'terminal', 'script', 'macos', 'cli'},
    'social': {'moltbook', 'twitter', 'linkedin', 'post', 'comment', 'reply', 'engage', 'social', 'tweet', 'hashtag', 'upvote'},
    'tooling': {'build', 'tool', 'api', 'secret', 'stripe', 'webhook', 'skill', 'pipeline', 'extract', 'ingest'},
    'comms': {'greg', 'communicate', 'permission', 'ship', 'promote', 'advertise', 'fixed', 'done', 'ready', 'quality'},
    'learning': {'learn', 'event', 'rule', 'lesson', 'metric', 'audit', 'pattern'},
}

# Score each rule
scored = []
for r in rules:
    score = 0.0
    reasons = []
    
    rule_text = r['rule'].lower()
    rule_words = set(re.findall(r'\w{3,}', rule_text))
    rule_cat = r['category']
    
    # 1. Direct word overlap between action and rule text
    overlap = action_words & rule_words
    if overlap:
        word_score = min(len(overlap) * 0.15, 0.6)
        score += word_score
        reasons.append(f"word overlap: {overlap}")
    
    # 2. Category match via action keywords
    for cat, signals in CATEGORY_SIGNALS.items():
        if action_words & signals and cat == rule_cat:
            score += 0.3
            reasons.append(f"category signal: {cat}")
            break
    
    # 3. Rule type weight - NEVER and MUST rules are more critical
    if r['type'] in ('NEVER', 'MUST') and score > 0:
        score += 0.1
        reasons.append(f"critical type: {r['type']}")
    
    # 4. Violation history - rules with past violations are more important to surface
    if r.get('violations', 0) > 0 and score > 0:
        score += 0.1 * min(r['violations'], 3)
        reasons.append(f"violation history: {r['violations']}x")
    
    # 5. Specific keyword triggers
    specific_triggers = {
        'moltbook': ['R-020', 'R-022', 'R-025', 'R-027'],
        'post': ['R-020', 'R-022', 'R-025', 'R-027', 'R-009'],
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
    }
    
    for keyword, rule_ids in specific_triggers.items():
        if keyword in action and r['id'] in rule_ids:
            score += 0.4
            reasons.append(f"specific trigger: {keyword}")
    
    if score >= 0.3:  # Minimum threshold to surface
        scored.append({
            'id': r['id'],
            'type': r['type'],
            'category': r['category'],
            'rule': r['rule'],
            'score': round(score, 2),
            'violations': r.get('violations', 0),
            'reasons': reasons
        })

# Sort by score descending
scored.sort(key=lambda x: -x['score'])

# Output
result = {
    'action': action,
    'matches': scored[:8],  # Top 8 most relevant
    'total_checked': len(rules),
    'total_matched': len(scored)
}

if scored:
    # Also output a compact summary for inline use
    print("⚠️ RULES CHECK:")
    for m in scored[:5]:
        prefix = "🚫" if m['type'] == 'NEVER' else "✅" if m['type'] == 'MUST' else "🔍" if m['type'] == 'CHECK' else "💡"
        viol = f" [{m['violations']}x violated]" if m['violations'] else ""
        print(f"  {prefix} {m['id']}: {m['rule'][:80]}{viol}")
    print()

# Machine-readable output
print(json.dumps(result, indent=2))

PYTHON

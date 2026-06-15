#!/usr/bin/env bash
# inject-rules.sh - Generate a compact rules preamble for cron agents
# Usage: bash inject-rules.sh [workspace] [category-filter]
# Example: bash inject-rules.sh /workspace social,comms
# Outputs a text block that can be prepended to cron agent messages

set -euo pipefail
WORKSPACE="${1:-/Users/gregborden/.openclaw/workspace}"
FILTER="${2:-all}"  # comma-separated categories, or "all"
RULES_FILE="$WORKSPACE/memory/learning/rules.json"

if [ ! -f "$RULES_FILE" ]; then
    echo "ERROR: Rules file not found at $RULES_FILE" >&2
    exit 1
fi

python3 -c "
import json, sys

with open('$RULES_FILE') as f:
    data = json.load(f)

rules = data.get('rules', [])
filt = '$FILTER'

if filt != 'all':
    cats = set(filt.split(','))
    rules = [r for r in rules if r['category'] in cats]

# Group by type
groups = {'MUST': [], 'NEVER': [], 'CHECK': [], 'PREFER': []}
for r in rules:
    t = r.get('type', 'CHECK')
    if t in groups:
        groups[t].append(r)

print('=== BEHAVIORAL RULES (read and follow) ===')
for gname in ['MUST', 'NEVER', 'CHECK', 'PREFER']:
    grules = groups[gname]
    if grules:
        print(f'\n{gname}:')
        for r in grules:
            # Compact: just ID and rule text (truncated)
            rule_text = r['rule'][:120]
            print(f'  {r[\"id\"]}: {rule_text}')
print()
print(f'Total: {len(rules)} rules loaded.')
"

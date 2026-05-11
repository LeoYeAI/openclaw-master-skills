#!/bin/bash
# scan_closure.sh - Check for task completion vs open items
# Returns: 3=mostly closed, 2=balanced, 1=accumulating, 0=overwhelmed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="closure"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

time_sat=$(calc_time_satisfaction "$NEED")

POS_PATTERN="(completed|done|finished|resolved|closed|checked off|\[x\]|✅|✓)"
NEG_PATTERN="(TODO|PENDING|\[ \]|waiting for|need to|should do|to follow up|open question|unresolved|blocked)"

pos_signals=0
neg_signals=0
scan_lines_in_file "$MEMORY_DIR/$TODAY.md" "$POS_PATTERN" "$NEG_PATTERN"
scan_lines_in_file "$MEMORY_DIR/$YESTERDAY.md" "$POS_PATTERN" "$NEG_PATTERN"

net=$((pos_signals - neg_signals))

if [[ $neg_signals -gt $pos_signals ]] && [[ $neg_signals -gt 5 ]]; then
    event_sat=0
elif [[ $net -ge 3 ]]; then
    event_sat=3
elif [[ $net -ge 0 ]]; then
    event_sat=2
elif [[ $neg_signals -gt 3 ]]; then
    event_sat=1
else
    event_sat=$time_sat
fi

smart_satisfaction "$NEED" "$event_sat"

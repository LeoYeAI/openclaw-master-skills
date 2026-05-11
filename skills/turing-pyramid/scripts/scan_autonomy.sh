#!/bin/bash
# scan_autonomy.sh - Check for autonomous decision-making
# Returns: 3=highly autonomous, 2=some agency, 1=dependent, 0=blocked

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="autonomy"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

time_sat=$(calc_time_satisfaction "$NEED")

POS_PATTERN="(decided|chose|initiated|explored|my idea|self-directed|proactive|on my own|took initiative|my decision|independently|without asking)"
NEG_PATTERN="(blocked|waiting for permission|can't without|need approval|dependent on|not allowed|restricted|forbidden|must ask first)"

pos_signals=0
neg_signals=0
scan_lines_in_file "$MEMORY_DIR/$TODAY.md" "$POS_PATTERN" "$NEG_PATTERN"
scan_lines_in_file "$MEMORY_DIR/$YESTERDAY.md" "$POS_PATTERN" "$NEG_PATTERN"

net=$((pos_signals - neg_signals))

if [[ $neg_signals -gt $pos_signals ]] && [[ $neg_signals -gt 2 ]]; then
    event_sat=0
elif [[ $net -ge 3 ]]; then
    event_sat=3
elif [[ $net -ge 1 ]]; then
    event_sat=2
elif [[ $pos_signals -eq 0 ]] && [[ $neg_signals -gt 0 ]]; then
    event_sat=1
else
    event_sat=$time_sat
fi

smart_satisfaction "$NEED" "$event_sat"

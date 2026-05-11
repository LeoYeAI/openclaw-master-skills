#!/bin/bash
# scan_recognition.sh - Check for external acknowledgment/feedback
# Returns: 3=recent positive feedback, 2=some engagement, 1=ignored, 0=negative feedback
# Event-sensitive: praise, criticism, engagement

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="recognition"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

time_sat=$(calc_time_satisfaction "$NEED")

POS_PATTERN="(thanks|great work|helpful|appreciated|good job|liked|upvote|positive feedback|well done|nice work|proud|excellent|awesome|kudos|recognized|acknowledged|engagement|comment|replied|posted|karma|verified|discussion)"
NEG_PATTERN="(wrong|bad|unhelpful|mistake|criticism|negative feedback|disappointed|not good|terrible|useless|failed you|let.*down)"

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
elif [[ $pos_signals -eq 0 ]]; then
    event_sat=1
else
    event_sat=$time_sat
fi

smart_satisfaction "$NEED" "$event_sat"

#!/bin/bash
# scan_security.sh - Check for security-related events
# Returns: 3=secure, 2=ok, 1=needs attention, 0=compromised

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="security"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

time_sat=$(calc_time_satisfaction "$NEED")

POS_PATTERN="(backup completed|backup success|security check|passed audit|updated|patched|secured|vault intact|integrity ok)"
NEG_PATTERN="(backup failed|security issue|compromised|breach|vulnerable|attack|unauthorized|leaked|exposed|credential.*(stolen|leaked))"

pos_signals=0
neg_signals=0
scan_lines_in_file "$MEMORY_DIR/$TODAY.md" "$POS_PATTERN" "$NEG_PATTERN"
scan_lines_in_file "$MEMORY_DIR/$YESTERDAY.md" "$POS_PATTERN" "$NEG_PATTERN"

net=$((pos_signals - neg_signals))

if [[ $neg_signals -gt 0 ]]; then
    event_sat=0  # Any security issue = critical
elif [[ $pos_signals -ge 2 ]]; then
    event_sat=3
elif [[ $pos_signals -ge 1 ]]; then
    event_sat=2
else
    event_sat=$time_sat
fi

smart_satisfaction "$NEED" "$event_sat"

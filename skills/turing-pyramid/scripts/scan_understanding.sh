#!/bin/bash
# scan_understanding.sh - Check for learning/comprehension events
# Returns: 3=active learning, 2=some insight, 1=confused, 0=lost

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="understanding"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

time_sat=$(calc_time_satisfaction "$NEED")

POS_PATTERN="(research|learned|learning|understood|discover|realiz|insight|figured out|makes sense|explored|read article|TIL|today i learned|grasped|clicked|aha|eureka|breakthrough|comprehend|studied|investigat|analyz|examin|documentation|tutorial)"
NEG_PATTERN="(confused|lost|unclear|don't understand|no idea|stuck|baffled|puzzled|perplexed|bewildered|wtf|makes no sense|doesn't make sense)"

pos_signals=0
neg_signals=0
scan_lines_in_file "$MEMORY_DIR/$TODAY.md" "$POS_PATTERN" "$NEG_PATTERN"
scan_lines_in_file "$MEMORY_DIR/$YESTERDAY.md" "$POS_PATTERN" "$NEG_PATTERN"

# Check research thread activity (inherited from daemon)
THREADS_DIR="$WORKSPACE/research/threads"
if [[ -d "$THREADS_DIR" ]]; then
    recent_threads=$(find "$THREADS_DIR" -name "*.md" -mmin -1440 2>/dev/null | wc -l)
    if [[ $recent_threads -gt 0 ]]; then
        pos_signals=$((pos_signals + recent_threads))
    fi
fi

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

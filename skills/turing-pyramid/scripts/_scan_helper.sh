#!/bin/bash
# _scan_helper.sh - Common functions for scan scripts
# WORKSPACE is REQUIRED - no silent fallback
if [[ -z "$WORKSPACE" ]]; then
    echo "❌ ERROR: WORKSPACE not set" >&2
    exit 1
fi

# Source this at the top of each scan script

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"

# Get hours since last satisfied for a need
# Usage: hours_since_satisfied "need_name"
# Returns: number of hours (integer)
hours_since_satisfied() {
    local need="$1"
    
    if [[ ! -f "$STATE_FILE" ]]; then
        echo 999  # Never satisfied
        return
    fi
    
    local last_sat=$(jq -r --arg n "$need" '.[$n].last_satisfied // empty' "$STATE_FILE")
    if [[ -z "$last_sat" ]]; then
        echo 999
        return
    fi
    
    local last_sat_epoch=$(date -d "$last_sat" +%s 2>/dev/null || echo 0)
    local now_epoch=$(date +%s)
    local seconds_since=$((now_epoch - last_sat_epoch))
    local hours_since=$((seconds_since / 3600))
    
    echo "$hours_since"
}

# Get decay rate for a need (in hours)
# Usage: get_decay_rate "need_name"
get_decay_rate() {
    local need="$1"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo 24  # default
        return
    fi
    
    local decay=$(jq -r ".needs.\"$need\".decay_rate_hours // 24" "$CONFIG_FILE")
    echo "$decay"
}

# Calculate satisfaction based on time since last satisfied vs decay rate
# Usage: calc_time_satisfaction "need_name"
# Returns: 0-3 satisfaction level
calc_time_satisfaction() {
    local need="$1"
    local hours=$(hours_since_satisfied "$need")
    local decay=$(get_decay_rate "$need")
    
    # decay_steps = hours / decay_rate
    local decay_steps=$((hours / decay))
    local sat=$((3 - decay_steps))
    
    [[ $sat -lt 0 ]] && sat=0
    [[ $sat -gt 3 ]] && sat=3
    
    echo "$sat"
}

# Check if need was recently satisfied (within grace period)
# Usage: check_grace_period "need_name" seconds
# Returns 0 (true) if within grace period, 1 (false) otherwise
check_grace_period() {
    local need="$1"
    local grace_seconds="${2:-3600}"  # default 1 hour
    
    if [[ ! -f "$STATE_FILE" ]]; then
        return 1
    fi
    
    local last_sat=$(jq -r --arg n "$need" '.[$n].last_satisfied // empty' "$STATE_FILE")
    if [[ -z "$last_sat" ]]; then
        return 1
    fi
    
    local last_sat_epoch=$(date -d "$last_sat" +%s 2>/dev/null || echo 0)
    local now_epoch=$(date +%s)
    local seconds_since=$((now_epoch - last_sat_epoch))
    
    [[ $seconds_since -lt $grace_seconds ]]
}

# Quick exit if in grace period (returns sat=3)
# Usage: exit_if_grace "need_name" [seconds]
exit_if_grace() {
    if check_grace_period "$1" "${2:-3600}"; then
        echo 3
        exit 0
    fi
}

# ─── LINE-LEVEL SCAN FUNCTION ──────────────────────────────────
# Shared line-level scanner for all needs.
# Analyzes each line: if BOTH positive and negative patterns present → positive wins.
# Usage: scan_lines_in_file "file" "pos_pattern" "neg_pattern"
# Sets global: pos_signals, neg_signals (caller must initialize to 0)
scan_lines_in_file() {
    local file="$1"
    local pos_pattern="$2"
    local neg_pattern="$3"
    [[ ! -f "$file" ]] && return
    
    while IFS= read -r line; do
        [[ -z "$line" || "$line" =~ ^#+ ]] && continue
        local has_pos=0 has_neg=0
        echo "$line" | grep -qiE "$pos_pattern" && has_pos=1
        echo "$line" | grep -qiE "$neg_pattern" && has_neg=1
        if [[ $has_pos -eq 1 ]]; then
            pos_signals=$((pos_signals + 1))
        elif [[ $has_neg -eq 1 ]]; then
            neg_signals=$((neg_signals + 1))
        fi
    done < "$file"
}

# Smart satisfaction: combines time-based with event detection
# Usage: smart_satisfaction "need_name" event_score
# Returns: satisfaction that respects both time decay and events
smart_satisfaction() {
    local need="$1"
    local event_score="$2"
    
    local time_sat=$(calc_time_satisfaction "$need")
    
    # If event_score provided and valid, take minimum
    if [[ -n "$event_score" && "$event_score" =~ ^[0-3]$ ]]; then
        if [[ $event_score -lt $time_sat ]]; then
            echo "$event_score"
        else
            echo "$time_sat"
        fi
    else
        echo "$time_sat"
    fi
}

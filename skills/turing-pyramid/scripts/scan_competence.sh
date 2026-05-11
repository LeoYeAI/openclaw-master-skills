#!/bin/bash
# scan_competence.sh - Check for effective skill use
# Returns: 3=highly effective, 2=competent, 1=struggling, 0=failing
# Event-sensitive: successes, failures
#
# Scan methods (configured in scan-config.json):
#   line-level (default): per-line analysis, positive context overrides negative
#   agent-spawn: uses sessions_spawn with cheap model for classification
#   external-model: direct API call to inference service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="competence"
MEMORY_DIR="$WORKSPACE/memory"
ASSETS_DIR="$SCRIPT_DIR/../assets"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Read scan method from config
SCAN_CONFIG="$ASSETS_DIR/scan-config.json"
scan_method="line-level"
if [[ -f "$SCAN_CONFIG" ]]; then
    scan_method=$(jq -r '.scan_method // "line-level"' "$SCAN_CONFIG")
fi

# Positive and negative patterns
POS_PATTERN="(completed|solved|built|fixed|succeeded|worked|done|shipped|implemented|achieved|nailed|crushed it|got it working|published|drafted|compiled|created|upgraded|improved|resolved|delivered)"
NEG_PATTERN="(failed|error|couldn't|stuck|broken|bug|crash|doesn't work|not working|can't figure|struggling|syntax error)"

# ─── LINE-LEVEL SCAN ───────────────────────────────────────────
# Logic: analyze each line independently.
# If a line has BOTH positive and negative words → counts as positive (e.g. "fixed a bug")
# If a line has ONLY negative words → counts as negative
# If a line has ONLY positive words → counts as positive

scan_line_level() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    while IFS= read -r line; do
        # Skip empty lines and headers
        [[ -z "$line" || "$line" =~ ^#+ ]] && continue
        
        local has_pos=0
        local has_neg=0
        
        echo "$line" | grep -qiE "$POS_PATTERN" && has_pos=1
        echo "$line" | grep -qiE "$NEG_PATTERN" && has_neg=1
        
        if [[ $has_pos -eq 1 ]]; then
            # Positive context wins (handles "fixed bug", "error resolved", etc.)
            competence_signals=$((competence_signals + 1))
        elif [[ $has_neg -eq 1 ]]; then
            # Pure negative — no positive context
            failure_signals=$((failure_signals + 1))
        fi
    done < "$file"
}

# ─── AGENT SPAWN SCAN ──────────────────────────────────────────
# Placeholder: agent-spawn requires OpenClaw sessions_spawn
# Called by the agent itself, not by bash. Agent reads scan-config.json
# and decides to spawn a sub-agent for classification.
# Falls back to line-level if called from bash directly.

# ─── EXTERNAL MODEL SCAN ───────────────────────────────────────
# Placeholder: external-model requires API key and endpoint.
# Falls back to line-level if not configured.

# ─── MAIN ──────────────────────────────────────────────────────

competence_signals=0
failure_signals=0

case "$scan_method" in
    agent-spawn|external-model)
        # These methods require runtime support beyond bash.
        # If called from bash directly, fall back to line-level.
        # The agent can override by reading scan-config.json and
        # handling classification itself before calling this script.
        scan_line_level "$MEMORY_DIR/$TODAY.md"
        scan_line_level "$MEMORY_DIR/$YESTERDAY.md"
        ;;
    line-level|*)
        scan_line_level "$MEMORY_DIR/$TODAY.md"
        scan_line_level "$MEMORY_DIR/$YESTERDAY.md"
        ;;
esac

# Calculate net competence
net=$((competence_signals - failure_signals))

# Calculate event satisfaction
if [[ $failure_signals -gt $competence_signals ]] && [[ $failure_signals -gt 3 ]]; then
    event_sat=0  # Failing
elif [[ $net -ge 3 ]]; then
    event_sat=3  # Highly effective
elif [[ $net -ge 1 ]]; then
    event_sat=2  # Competent
elif [[ $competence_signals -eq 0 ]] && [[ $failure_signals -gt 0 ]]; then
    event_sat=1  # Struggling
else
    event_sat=$time_sat  # Default to time-based
fi

smart_satisfaction "$NEED" "$event_sat"

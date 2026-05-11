#!/bin/bash
# Turing Pyramid — Mark Need as Satisfied + Apply Cross-Need Impact
# Usage: ./mark-satisfied.sh <need> [impact] [--reason "..."]
# Impact: float 0.0-3.0 (default 3.0)
# Reason: required for audit trail (what action was taken)

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
CROSS_IMPACT_FILE="$SKILL_DIR/assets/cross-need-impact.json"
AUDIT_FILE="$SKILL_DIR/assets/audit.log"

# Acquire exclusive lock on state file to prevent race conditions
exec 200>"$STATE_FILE.lock"
if ! flock -n 200; then
    # Another process has the lock, wait for it
    flock 200
fi

# Parse arguments
NEED=""
IMPACT="3.0"
REASON=""
FOLLOWUP_WHAT=""
FOLLOWUP_IN=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --reason)
            REASON="$2"
            shift 2
            ;;
        --reason=*)
            REASON="${1#*=}"
            shift
            ;;
        --followup)
            FOLLOWUP_WHAT="$2"
            shift 2
            ;;
        --followup=*)
            FOLLOWUP_WHAT="${1#*=}"
            shift
            ;;
        --in)
            FOLLOWUP_IN="$2"
            shift 2
            ;;
        --in=*)
            FOLLOWUP_IN="${1#*=}"
            shift
            ;;
        *)
            if [[ -z "$NEED" ]]; then
                NEED="$1"
            elif [[ "$IMPACT" == "3.0" ]]; then
                IMPACT="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$NEED" ]]; then
    echo "Usage: $0 <need> [impact] --reason \"what was done\""
    echo "Example: $0 connection 1.5 --reason \"replied to Moltbook comments\""
    exit 1
fi

# Reason is required for audit transparency
if [[ -z "$REASON" ]]; then
    echo "⚠️  Warning: No --reason provided. Audit trail will show 'no reason given'."
    echo "   Better: $0 $NEED $IMPACT --reason \"description of action taken\""
    REASON="(no reason given)"
fi

# Scrub sensitive patterns from reason before logging
scrub_sensitive() {
    local text="$1"
    # Remove potential secrets/tokens (patterns)
    text=$(echo "$text" | sed -E '
        s/[a-zA-Z0-9_-]{20,}/[REDACTED]/g;
        s/[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}/[CARD]/g;
        s/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[EMAIL]/g;
        s/(password|secret|token|key|api_key|apikey)[=: ]+[^ ]+/\1=[REDACTED]/gi;
        s/Bearer [^ ]+/Bearer [REDACTED]/g;
    ')
    echo "$text"
}

REASON_SCRUBBED=$(scrub_sensitive "$REASON")

NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CALLER="${TURING_CALLER:-manual}"

# Validate impact is numeric and in range
if ! [[ "$IMPACT" =~ ^-?[0-9]*\.?[0-9]+$ ]]; then
    echo "❌ Invalid impact value: $IMPACT (must be numeric)"
    exit 1
fi

# Clamp impact to 0-3 range
if (( $(echo "$IMPACT < 0" | bc -l) )); then
    echo "⚠️  Impact $IMPACT clamped to 0"
    IMPACT="0"
fi
if (( $(echo "$IMPACT > 3" | bc -l) )); then
    echo "⚠️  Impact $IMPACT clamped to 3.0"
    IMPACT="3.0"
fi

# Validate need exists (needs are at root level in state file)
if ! jq -e --arg need "$NEED" '.[$need]' "$STATE_FILE" > /dev/null 2>&1; then
    echo "❌ Unknown need: $NEED"
    echo "Valid needs:"
    jq -r 'keys | .[] | select(. != "_meta")' "$STATE_FILE"
    exit 1
fi

# Read current satisfaction
CURRENT_SAT=$(jq -r --arg need "$NEED" '.[$need].satisfaction // 2.0' "$STATE_FILE")

# Calculate new satisfaction: current + impact, clamped to floor(0.5) and ceiling(3.0)
NEW_SAT=$(echo "scale=4; $CURRENT_SAT + $IMPACT" | bc -l)
if (( $(echo "$NEW_SAT < 0.5" | bc -l) )); then
    NEW_SAT="0.50"
fi
if (( $(echo "$NEW_SAT > 3.0" | bc -l) )); then
    NEW_SAT="3.00"
fi

# Update state: satisfaction, last_satisfied, last_decay_check, impact, last_action_at
jq --arg need "$NEED" --arg now "$NOW_ISO" --argjson impact "$IMPACT" --argjson sat "$NEW_SAT" '
  .[$need].satisfaction = $sat |
  .[$need].last_satisfied = $now |
  .[$need].last_decay_check = $now |
  .[$need].last_impact = $impact |
  .[$need].last_action_at = $now
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

echo "✅ $NEED marked as satisfied (impact: $IMPACT)"
echo "   satisfaction: $CURRENT_SAT → $NEW_SAT"
echo "   last_satisfied = $NOW_ISO"
echo "   reason: $REASON"

# Track high-impact actions for spontaneity Layer B (boredom noise)
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
HIGH_THRESHOLD=$(jq -r ".needs.\"$NEED\".spontaneous.noise_override.high_impact_threshold // empty" "$CONFIG_FILE" 2>/dev/null)
if [[ -z "$HIGH_THRESHOLD" ]]; then
    HIGH_THRESHOLD=$(jq -r '.settings.spontaneity.noise.high_impact_threshold // 2.0' "$CONFIG_FILE" 2>/dev/null)
fi
HIGH_THRESHOLD="${HIGH_THRESHOLD:-2.0}"

if (( $(echo "$IMPACT >= $HIGH_THRESHOLD" | bc -l) )); then
    jq --arg need "$NEED" --arg now "$NOW_ISO" \
       '.[$need].last_high_action_at = $now' \
       "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "   📊 High-impact action recorded (boredom noise reset)"
fi

# Write to audit log (append-only transparency, sensitive data scrubbed)
AUDIT_ENTRY=$(jq -cn \
    --arg ts "$NOW_ISO" \
    --arg need "$NEED" \
    --argjson impact "$IMPACT" \
    --arg old_sat "$CURRENT_SAT" \
    --arg new_sat "$NEW_SAT" \
    --arg reason "$REASON_SCRUBBED" \
    --arg caller "$CALLER" \
    '{timestamp: $ts, need: $need, impact: $impact, old_sat: $old_sat, new_sat: $new_sat, reason: $reason, caller: $caller}')
echo "$AUDIT_ENTRY" >> "$AUDIT_FILE"

# Apply cross-need impacts (on_action)
if [[ -f "$CROSS_IMPACT_FILE" ]]; then
    FLOOR=$(jq -r '.settings.floor // 0.5' "$CROSS_IMPACT_FILE")
    CEILING=$(jq -r '.settings.ceiling // 3.0' "$CROSS_IMPACT_FILE")
    
    # Get all impacts where source = this need and on_action is set
    IMPACTS=$(jq -r --arg need "$NEED" '
        .impacts[] | 
        select(.source == $need and .on_action != null) |
        "\(.target):\(.on_action)"
    ' "$CROSS_IMPACT_FILE")
    
    if [[ -n "$IMPACTS" ]]; then
        echo ""
        echo "📊 Cross-need impacts (on_action):"
        
        while IFS=: read -r TARGET DELTA; do
            [[ -z "$TARGET" ]] && continue
            
            # Get current satisfaction of target (root level)
            CURRENT_TARGET=$(jq -r --arg t "$TARGET" '.[$t].satisfaction // 2.0' "$STATE_FILE")
            
            # Calculate new satisfaction with floor/ceiling
            NEW_TARGET=$(echo "$CURRENT_TARGET + $DELTA" | bc -l)
            
            # Apply floor
            if (( $(echo "$NEW_TARGET < $FLOOR" | bc -l) )); then
                NEW_TARGET="$FLOOR"
            fi
            # Apply ceiling
            if (( $(echo "$NEW_TARGET > $CEILING" | bc -l) )); then
                NEW_TARGET="$CEILING"
            fi
            
            # Format to 2 decimal places
            NEW_TARGET=$(printf "%.2f" "$NEW_TARGET")
            
            # Update target satisfaction (root level)
            jq --arg t "$TARGET" --argjson sat "$NEW_TARGET" '
                .[$t].satisfaction = $sat
            ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
            
            if (( $(echo "$DELTA > 0" | bc -l) )); then
                echo "   → $TARGET: +$DELTA (now: $NEW_TARGET)"
            else
                echo "   → $TARGET: $DELTA (now: $NEW_TARGET)"
            fi
            
        done <<< "$IMPACTS"
    fi
fi

# Create follow-up if requested
if [[ -n "$FOLLOWUP_WHAT" && -n "$FOLLOWUP_IN" ]]; then
    echo ""
    echo "📌 Creating follow-up..."
    bash "$SKILL_DIR/scripts/create-followup.sh" \
        --what "$FOLLOWUP_WHAT" \
        --in "$FOLLOWUP_IN" \
        --need "$NEED" \
        --source auto \
        --parent "$REASON"
fi

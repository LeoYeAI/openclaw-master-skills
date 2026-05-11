#!/bin/bash
# Turing Pyramid — Apply Cross-Need Deprivation Effects
# Called at start of cycle to propagate deprivation penalties

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
CROSS_IMPACT_FILE="$SKILL_DIR/assets/cross-need-impact.json"

if [[ ! -f "$CROSS_IMPACT_FILE" ]]; then
    exit 0
fi

FLOOR=$(jq -r '.settings.floor // 0.5' "$CROSS_IMPACT_FILE")
THRESHOLD=$(jq -r '.settings.deprivation_threshold // 1.0' "$CROSS_IMPACT_FILE")
APPLIED=0

# Check each need for deprivation state
for NEED in $(jq -r 'keys[] | select(. != "_meta")' "$STATE_FILE"); do
    SAT=$(jq -r --arg n "$NEED" '.[$n].satisfaction // 2.0' "$STATE_FILE")
    
    # Check if below threshold (deprived)
    if (( $(echo "$SAT <= $THRESHOLD" | bc -l) )); then
        # Get deprivation impacts for this need
        IMPACTS=$(jq -r --arg need "$NEED" '
            .impacts[] | 
            select(.source == $need and .on_deprivation != null and .on_deprivation < 0) |
            "\(.target):\(.on_deprivation)"
        ' "$CROSS_IMPACT_FILE")
        
        while IFS=: read -r TARGET DELTA; do
            [[ -z "$TARGET" ]] && continue
            
            # Check if we already applied this deprivation recently (prevent stacking)
            LAST_DEP=$(jq -r --arg t "$TARGET" --arg s "$NEED" '
                .[$t].deprivation_applied[$s] // "1970-01-01T00:00:00Z"
            ' "$STATE_FILE")
            
            LAST_DEP_EPOCH=$(date -d "$LAST_DEP" +%s 2>/dev/null || echo 0)
            NOW_EPOCH=$(date +%s)
            HOURS_SINCE=$(( (NOW_EPOCH - LAST_DEP_EPOCH) / 3600 ))
            
            # Only apply deprivation every 4 hours max
            if (( HOURS_SINCE < 4 )); then
                continue
            fi
            
            CURRENT_TARGET=$(jq -r --arg t "$TARGET" '.[$t].satisfaction // 2.0' "$STATE_FILE")
            NEW_SAT=$(echo "$CURRENT_TARGET + $DELTA" | bc -l)
            
            # Apply floor - never go below
            if (( $(echo "$NEW_SAT < $FLOOR" | bc -l) )); then
                NEW_SAT="$FLOOR"
            fi
            
            NEW_SAT=$(printf "%.2f" "$NEW_SAT")
            NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
            
            # Update target satisfaction and record deprivation
            jq --arg t "$TARGET" --argjson sat "$NEW_SAT" --arg s "$NEED" --arg now "$NOW_ISO" '
                .[$t].satisfaction = $sat |
                .[$t].deprivation_applied[$s] = $now
            ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
            
            if [[ "$APPLIED" -eq 0 ]]; then
                echo "⚠️  Deprivation cascades:"
                APPLIED=1
            fi
            echo "   $NEED (sat=$SAT) → $TARGET: $DELTA (now: $NEW_SAT)"
            
        done <<< "$IMPACTS"
    fi
done

if [[ "$APPLIED" -eq 0 ]] && [[ -n "$DEBUG" ]]; then
    echo "   (no deprivation effects active)"
fi

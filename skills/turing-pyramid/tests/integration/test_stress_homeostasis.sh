#!/usr/bin/env bash
# Stress Test: Homeostasis Recovery
# Simulates 300 cycles starting from sat=0, verifies system recovers

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
TEST_STATE="/tmp/pyramid-stress-test-$$.json"
CYCLES="${1:-50}"
MODE="${2:-day}"  # day or night

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔺 Turing Pyramid Stress Test"
echo "=============================="
echo "Mode: $MODE | Cycles: $CYCLES"
echo ""

# Get decay multiplier
if [[ "$MODE" == "night" ]]; then
    DECAY_MULT=0.5
else
    DECAY_MULT=1.0
fi

# Initialize crisis state (sat=0 for all needs)
NEEDS=$(jq -r '.needs | keys[]' "$CONFIG_FILE")
echo "{" > "$TEST_STATE"
first=true
for need in $NEEDS; do
    [[ "$first" == "true" ]] || echo "," >> "$TEST_STATE"
    first=false
    cat >> "$TEST_STATE" << EOF
  "$need": {
    "satisfaction": 0.0,
    "deprivation": 3,
    "last_satisfied": "1970-01-01T00:00:00Z",
    "last_decay_check": "$(date -Iseconds)"
  }
EOF
done
echo "}" >> "$TEST_STATE"

# Tracking variables
declare -A floor_streak
declare -A dep3_streak
declare -A sat_history
action_streak=0
max_action_streak=0
total_actions=0
cycle_sats=()

for need in $NEEDS; do
    floor_streak[$need]=0
    dep3_streak[$need]=0
    sat_history[$need]=""
done

# Simulate cycles
echo "Running $CYCLES cycles..."

for ((cycle=1; cycle<=CYCLES; cycle++)); do
    actions_this_cycle=0
    
    for need in $NEEDS; do
        # Read current state
        sat=$(jq -r ".[\"$need\"].satisfaction" "$TEST_STATE")
        dep=$(jq -r ".[\"$need\"].deprivation" "$TEST_STATE")
        importance=$(jq -r ".needs.\"$need\".importance" "$CONFIG_FILE")
        decay_rate=$(jq -r ".needs.\"$need\".decay_rate_hours" "$CONFIG_FILE")
        
        # Simulate decay (scaled: 1 cycle = 30 min equivalent)
        # decay_delta = (0.5 hours / decay_rate) * multiplier
        decay_delta=$(echo "scale=4; (0.5 / $decay_rate) * $DECAY_MULT" | bc -l)
        sat=$(echo "scale=2; $sat - $decay_delta" | bc -l)
        
        # Floor at 0.5
        if (( $(echo "$sat < 0.5" | bc -l) )); then
            sat="0.50"
        fi
        
        # Calculate tension: importance × deprivation (matches production)
        tension=$(echo "scale=0; $importance * $dep / 1" | bc)
        
        # Calculate deprivation based on satisfaction
        if (( $(echo "$sat < 1" | bc -l) )); then
            dep=3
        elif (( $(echo "$sat < 2" | bc -l) )); then
            dep=2
        else
            dep=1
        fi
        
        # Simulate action selection (simplified: if tension > 5, take action)
        if [[ $tension -gt 5 ]]; then
            # Mock action: apply random impact 0.5-2.0
            impact=$(echo "scale=2; 0.5 + ($RANDOM % 150) / 100" | bc -l)
            sat=$(echo "scale=2; $sat + $impact" | bc -l)
            ((actions_this_cycle++)) || true
            ((total_actions++)) || true
        fi
        
        # Ceiling at 3.0
        if (( $(echo "$sat > 3" | bc -l) )); then
            sat="3.00"
        fi
        
        # Track floor streak
        if (( $(echo "$sat <= 0.5" | bc -l) )); then
            ((floor_streak[$need]++)) || true
        else
            floor_streak[$need]=0
        fi
        
        # Track dep=3 streak
        if [[ $dep -eq 3 ]]; then
            ((dep3_streak[$need]++)) || true
        else
            dep3_streak[$need]=0
        fi
        
        # Store sat for averaging
        sat_history[$need]+="$sat "
        
        # Update state
        jq --arg n "$need" --arg s "$sat" --argjson d "$dep" \
            '.[$n].satisfaction = ($s | tonumber) | .[$n].deprivation = $d' \
            "$TEST_STATE" > "${TEST_STATE}.tmp" && mv "${TEST_STATE}.tmp" "$TEST_STATE"
    done
    
    # Track action streaks
    if [[ $actions_this_cycle -eq 0 ]]; then
        ((action_streak++)) || true
        if [[ $action_streak -gt $max_action_streak ]]; then
            max_action_streak=$action_streak
        fi
    else
        action_streak=0
    fi
    
    # Progress indicator
    if (( cycle % 50 == 0 )); then
        echo -n "."
    fi
done

echo ""
echo ""
echo "=============================="
echo "📊 Results"
echo "=============================="

# Analyze results
PASS=true
LAST_100_START=$((CYCLES - 100))
if [[ $LAST_100_START -lt 0 ]]; then
    LAST_100_START=0
fi

# Check each need
for need in $NEEDS; do
    # Get last 100 sats
    sats=(${sat_history[$need]:-})
    if [[ ${#sats[@]} -eq 0 || -z "${sats[0]}" ]]; then
        avg="0.00"
    else
        last_100=("${sats[@]: -100}")
        sum=0
        for s in "${last_100[@]}"; do
            sum=$(echo "$sum + $s" | bc -l)
        done
        avg=$(echo "scale=2; $sum / ${#last_100[@]}" | bc -l)
    fi
    
    # Get final state
    final_sat=$(jq -r ".[\"$need\"].satisfaction" "$TEST_STATE")
    
    echo "$need: final_sat=$final_sat, avg_last100=$avg"
    
    # Check homeostasis (avg >= 1.5)
    if (( $(echo "$avg < 1.5" | bc -l) )); then
        echo -e "  ${RED}FAIL: avg < 1.5${NC}"
        PASS=false
    fi
done

echo ""
echo "Action rate: $total_actions actions over $CYCLES cycles"
echo "Max no-action streak: $max_action_streak cycles"

if [[ $max_action_streak -gt 20 ]]; then
    echo -e "${RED}FAIL: Action paralysis detected (>20 consecutive no-action cycles)${NC}"
    PASS=false
fi

# Cleanup
rm -f "$TEST_STATE" "${TEST_STATE}.tmp" "${TEST_STATE}.lock"

echo ""
if [[ "$PASS" == "true" ]]; then
    echo -e "${GREEN}✅ STRESS TEST PASSED${NC}"
    exit 0
else
    echo -e "${RED}❌ STRESS TEST FAILED${NC}"
    exit 1
fi

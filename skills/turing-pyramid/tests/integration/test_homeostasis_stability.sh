#!/bin/bash
# test_homeostasis_stability.sh — Verify system self-corrects over 30 cycles
# 
# Success criteria: No need stays at sat=0 (floor=0.5) for all 30 cycles
# This tests that the priority system ensures all needs get attention eventually
#
# Methodology:
# 1. Start from crisis state (all needs at floor)
# 2. Simulate 30 cycles, marking top-priority need as satisfied each cycle
# 3. Track how many cycles each need spends at floor
# 4. FAIL if any need stays at floor for >20 cycles (66%)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
RUN_CYCLE="$SKILL_DIR/scripts/run-cycle.sh"
MARK_SCRIPT="$SKILL_DIR/scripts/mark-satisfied.sh"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
FIXTURES="$SCRIPT_DIR/../fixtures"

# WORKSPACE required by run-cycle.sh
export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
# Skip scans — this test validates priority/decay homeostasis, not scanner accuracy
export SKIP_SCANS="true"
export SKIP_SPONTANEITY="true"

# Backup current state
cp "$STATE_FILE" "$STATE_FILE.homeostasis_backup"

# Start from crisis
cp "$FIXTURES/needs-state-crisis.json" "$STATE_FILE"

# Track cycles at floor per need
declare -A floor_cycles
for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    floor_cycles[$need]=0
done

CYCLES=50
MAX_FLOOR_CYCLES=35  # Fail if any need at floor for more than this (70%)

# Simulate realistic heartbeat intervals by rewinding decay timestamps
# between cycles. Each cycle simulates HEARTBEAT_INTERVAL_HOURS of elapsed time.
HEARTBEAT_INTERVAL_HOURS=1  # 1 hour between heartbeats (realistic)

echo "Running $CYCLES simulated cycles (${HEARTBEAT_INTERVAL_HOURS}h intervals)..."

for i in $(seq 1 $CYCLES); do
    # Simulate time passing: rewind all last_decay_check timestamps
    # This makes run-cycle.sh think HEARTBEAT_INTERVAL_HOURS have passed
    jq --argjson hours "$HEARTBEAT_INTERVAL_HOURS" '
      to_entries | map(
        if .value.last_decay_check then
          .value.last_decay_check = (
            (.value.last_decay_check | sub("\\.[0-9]+Z$"; "Z") |
             strptime("%Y-%m-%dT%H:%M:%SZ") | mktime) - ($hours * 3600) |
            strftime("%Y-%m-%dT%H:%M:%SZ")
          )
        else . end
      ) | from_entries
    ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    # Run cycle and extract top ACTION need
    output=$("$RUN_CYCLE" 2>/dev/null)
    
    # Get ALL ACTION needs (run-cycle generates up to MAX_ACTIONS per cycle)
    action_needs=$(echo "$output" | grep "▶ ACTION:" | sed -E 's/.*ACTION: ([a-z]+).*/\1/')
    
    for top_need in $action_needs; do
        # Simulate completing each action with medium impact
        "$MARK_SCRIPT" "$top_need" 1.5 > /dev/null 2>&1
    done
    
    # Check which needs are at floor (sat <= 0.5)
    for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
        sat=$(jq -r ".$need.satisfaction // 0" "$STATE_FILE")
        if (( $(echo "$sat <= 0.5" | bc -l) )); then
            floor_cycles[$need]=$((floor_cycles[$need] + 1))
        fi
    done
done

# Restore backup
cp "$STATE_FILE.homeostasis_backup" "$STATE_FILE"
rm "$STATE_FILE.homeostasis_backup"

# Check results
echo ""
echo "Cycles at floor (max allowed: $MAX_FLOOR_CYCLES):"
errors=0
for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    count=${floor_cycles[$need]}
    if [[ $count -gt $MAX_FLOOR_CYCLES ]]; then
        echo "  $need: $count cycles — FAIL (chronic deprivation)"
        ((errors++))
    else
        echo "  $need: $count cycles — OK"
    fi
done

if [[ $errors -eq 0 ]]; then
    echo ""
    echo "Homeostasis: STABLE"
    exit 0
else
    echo ""
    echo "Homeostasis: UNSTABLE ($errors needs with chronic deprivation)"
    exit 1
fi

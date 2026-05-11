#!/bin/bash
# test_full_cycle.sh — Verify run-cycle.sh produces valid output with correct values

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
RUN_CYCLE="$SKILL_DIR/scripts/run-cycle.sh"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
FIXTURES="$SCRIPT_DIR/../fixtures"

export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"

errors=0

# Backup current state
cp "$STATE_FILE" "$STATE_FILE.test_backup"

# Use healthy fixture for predictable state
cp "$FIXTURES/needs-state-healthy.json" "$STATE_FILE"

# Update timestamps to now to avoid decay artifacts
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    jq --arg n "$need" --arg t "$now" '.[$n].last_decay_check = $t | .[$n].last_satisfied = $t' \
        "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
done

# Run cycle and capture output
output=$("$RUN_CYCLE" 2>&1)

# -------------------------------------------
# Test 1: Output structure
# -------------------------------------------
echo "Test 1: Output structure"

if ! echo "$output" | grep -q "Turing Pyramid"; then
    echo "  Missing header — FAIL"
    ((errors++))
else
    echo "  Header present — OK"
fi

if ! echo "$output" | grep -q "Current tensions:"; then
    echo "  Missing tensions section — FAIL"
    ((errors++))
else
    echo "  Tensions section present — OK"
fi

if ! echo "$output" | grep -q "Summary:"; then
    echo "  Missing summary — FAIL"
    ((errors++))
else
    echo "  Summary present — OK"
fi

# -------------------------------------------
# Test 2: All 10 needs are listed
# -------------------------------------------
echo ""
echo "Test 2: All needs listed"

for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    if echo "$output" | grep -q "$need:"; then
        echo "  $need — OK"
    else
        echo "  $need — MISSING"
        ((errors++))
    fi
done

# -------------------------------------------
# Test 3: Tension values are mathematically correct
# Formula: tension = importance × deprivation
# Where: deprivation = 3 - round(satisfaction)
# -------------------------------------------
echo ""
echo "Test 3: Tension values verification"

for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    # Get importance from config
    imp=$(jq -r ".needs.$need.importance" "$CONFIG_FILE")
    
    # Get satisfaction from state (float)
    sat=$(jq -r ".$need.satisfaction // 2" "$STATE_FILE")
    
    # Float deprivation (matches actual code: scale=2; 3 - satisfaction)
    dep=$(echo "scale=2; 3 - $sat" | bc -l)
    if (( $(echo "$dep < 0" | bc -l) )); then dep="0"; fi
    # Float tension = importance × deprivation (matches code: scale=1)
    expected=$(echo "scale=1; $imp * $dep" | bc -l)
    
    # Extract actual tension from output (match tension line, not cascade)
    need_line=$(echo "$output" | grep -E "^\s+$need: tension=" | head -1)
    actual=$(echo "$need_line" | sed -E 's/.*tension=([0-9.]+).*/\1/')
    
    # Tension=0 needs are not shown in output
    if [[ -z "$actual" && "$expected" == "0" ]]; then
        echo "  $need: not shown (tension=0) — OK"
    elif (( $(echo "${actual:-0} == $expected" | bc -l) )); then
        echo "  $need: tension=$actual — OK"
    else
        echo "  $need: tension=$actual (expected $expected, imp=$imp, sat=$sat→$sat_int, dep=$dep) — FAIL"
        ((errors++))
    fi
done

# -------------------------------------------
# Test 4: Actions are selected for high-tension needs
# -------------------------------------------
echo ""
echo "Test 4: Action selection"

# Set one need to crisis
jq '.expression.satisfaction = 0.5' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

output2=$("$RUN_CYCLE" 2>&1)

if echo "$output2" | grep -q "ACTION:"; then
    action_count=$(echo "$output2" | grep -c "ACTION:")
    echo "  $action_count action(s) selected — OK"
else
    echo "  No actions selected — FAIL"
    ((errors++))
fi

# Verify expression (importance=1, but sat=0.5 means tension=2.5) gets action
# Actually, higher importance needs will be picked first
# Let's check that SOME action is being taken
if echo "$output2" | grep -q "selected:"; then
    echo "  Action details present — OK"
else
    echo "  No action details — FAIL"
    ((errors++))
fi

# -------------------------------------------
# Test 5: Tensions are sorted by priority
# -------------------------------------------
echo ""
echo "Test 5: Tension sorting"

# Extract tensions in order they appear (float values)
tensions=$(echo "$output" | grep -E "^\s+\w+: tension=" | sed -E 's/.*tension=([0-9.]+).*/\1/')

# Check they are in descending order (numeric comparison)
prev=9999
sorted=true
for t in $tensions; do
    if (( $(echo "$t > $prev" | bc -l) )); then
        sorted=false
        break
    fi
    prev=$t
done

if $sorted; then
    echo "  Tensions sorted descending — OK"
else
    echo "  Tensions NOT sorted — FAIL"
    ((errors++))
fi

# Restore backup
cp "$STATE_FILE.test_backup" "$STATE_FILE"
rm "$STATE_FILE.test_backup"

if [[ $errors -eq 0 ]]; then
    echo ""
    echo "Full cycle test PASSED"
    exit 0
else
    echo ""
    echo "Full cycle test FAILED: $errors errors"
    exit 1
fi

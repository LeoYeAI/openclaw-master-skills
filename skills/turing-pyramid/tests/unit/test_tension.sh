#!/usr/bin/env bash
# Test: tension calculation
# CORRECT formula: tension = importance × (3 - satisfaction)
# NOT the old wrong formula: (10 - sat) * dep

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
RUN_CYCLE="$SKILL_DIR/scripts/run-cycle.sh"

export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
export SKIP_SCANS="true"  # Skip event scans for predictable tension testing

errors=0

# Test 1: Verify formula by checking run-cycle.sh output
echo "Test 1: Tension formula verification via run-cycle output"

# Backup state
cp "$STATE_FILE" "$STATE_FILE.tension_backup"

# Set known state: security sat=2.0
now_str=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq --arg t "$now_str" '.security.satisfaction = 2.0 | .security.last_decay_check = $t | .security.last_satisfied = $t' \
    "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Run cycle and capture output
output=$("$RUN_CYCLE" 2>&1)

# Extract security tension from output
# Format: "  security: tension=X (sat=Y, dep=Z)"
security_line=$(echo "$output" | grep -E "^\s+security: tension=" | head -1)
actual_tension=$(echo "$security_line" | sed -E 's/.*tension=([0-9.]+).*/\1/')

# Get importance from config
importance=$(jq -r '.needs.security.importance' "$CONFIG_FILE")

# Expected: importance × (3 - sat) = 10 × (3 - 2) = 10
expected_tension=$((importance * (3 - 2)))

# Restore backup
cp "$STATE_FILE.tension_backup" "$STATE_FILE"
rm "$STATE_FILE.tension_backup"

# Compare numerically (actual may be float "10.0", expected integer "10")
if (( $(echo "$actual_tension == $expected_tension" | bc -l) )); then
    echo "  security (sat=2.0): tension=$actual_tension — OK"
else
    echo "  security (sat=2.0): tension=$actual_tension (expected $expected_tension) — FAIL"
    ((errors++))
fi

# Test 2: Crisis state (sat=0)
echo ""
echo "Test 2: Crisis state tension"

cp "$STATE_FILE" "$STATE_FILE.tension_backup"

now_str=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq --arg t "$now_str" '.integrity.satisfaction = 0 | .integrity.last_decay_check = $t | .integrity.last_satisfied = $t' \
    "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

output=$("$RUN_CYCLE" 2>&1)

integrity_line=$(echo "$output" | grep -E "^\s+integrity: tension=" | head -1)
actual_tension=$(echo "$integrity_line" | sed -E 's/.*tension=([0-9.]+).*/\1/')

integrity_importance=$(jq -r '.needs.integrity.importance' "$CONFIG_FILE")
# Expected: 9 × (3 - 0) = 27
expected_tension=$((integrity_importance * 3))

cp "$STATE_FILE.tension_backup" "$STATE_FILE"
rm "$STATE_FILE.tension_backup"

if (( $(echo "$actual_tension == $expected_tension" | bc -l) )); then
    echo "  integrity (sat=0): tension=$actual_tension — OK"
else
    echo "  integrity (sat=0): tension=$actual_tension (expected $expected_tension) — FAIL"
    ((errors++))
fi

# Test 3: Satisfied state (sat=3) — tension=0 means NOT shown in output
echo ""
echo "Test 3: Satisfied state tension"

cp "$STATE_FILE" "$STATE_FILE.tension_backup"

now_str=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq --arg t "$now_str" '.expression.satisfaction = 3.0 | .expression.last_decay_check = $t | .expression.last_satisfied = $t' \
    "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

output=$("$RUN_CYCLE" 2>&1)

# sat=3.0 means tension=0, and tension=0 needs are NOT displayed (by design)
# So we verify expression does NOT appear in the tensions list
if echo "$output" | grep -qE "^\s+expression: tension="; then
    # If it appears, it should only be with tension=0
    expression_line=$(echo "$output" | grep -E "^\s+expression: tension=" | head -1)
    actual_tension=$(echo "$expression_line" | sed -E 's/.*tension=([0-9.]+).*/\1/')
    if [[ "$actual_tension" == "0" ]]; then
        echo "  expression (sat=3.0): tension=0 shown — OK (edge case)"
    else
        echo "  expression (sat=3.0): tension=$actual_tension (expected 0 or not shown) — FAIL"
        ((errors++))
    fi
else
    echo "  expression (sat=3.0): not shown (tension=0) — OK"
fi

cp "$STATE_FILE.tension_backup" "$STATE_FILE"
rm "$STATE_FILE.tension_backup"

# Test 4: Verify all tensions are calculated correctly
# Formula: tension = importance × deprivation
# Where: deprivation = 3 - round(satisfaction)
echo ""
echo "Test 4: All needs tension verification"

cp "$STATE_FILE" "$STATE_FILE.tension_backup"

# Set all needs to sat=1.0 for predictable testing (rounds to 1, dep=2)
now_str=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    jq --arg n "$need" --arg t "$now_str" '.[$n].satisfaction = 1.0 | .[$n].last_decay_check = $t | .[$n].last_satisfied = $t' \
        "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
done

output=$("$RUN_CYCLE" 2>&1)

for need in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    imp=$(jq -r ".needs.$need.importance" "$CONFIG_FILE")
    # sat=1.0 → sat_int=1 → deprivation=2 → tension=importance×2
    expected=$((imp * 2))
    
    # Match tension output format exactly: "  need: tension=X.Y"
    # Avoid matching deprivation cascade lines like "→ need: -0.25"
    need_line=$(echo "$output" | grep -E "^\s+$need: tension=" | head -1)
    actual=$(echo "$need_line" | sed -E 's/.*tension=([0-9.]+).*/\1/')
    
    # Allow tolerance for cross-need deprivation effects modifying sat slightly
    diff=$(echo "scale=4; $actual - $expected" | bc -l)
    diff=${diff#-}
    # Tolerance of 3.0 accounts for cross-need deprivation cascades
    if (( $(echo "$diff <= 3.0" | bc -l) )); then
        echo "  $need: tension=$actual (expected ~$expected) — OK"
    else
        echo "  $need: tension=$actual (expected ~$expected, imp=$imp, diff=$diff) — FAIL"
        ((errors++))
    fi
done

cp "$STATE_FILE.tension_backup" "$STATE_FILE"
rm "$STATE_FILE.tension_backup"

if [[ $errors -eq 0 ]]; then
    echo ""
    echo "All tension tests passed"
    exit 0
else
    echo ""
    echo "Tension tests FAILED: $errors errors"
    exit 1
fi

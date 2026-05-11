#!/bin/bash
# Tests for starvation guard feature
# Tests: detection, forced action, threshold, disabled guard

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$SKILL_DIR/scripts"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"

# Backup originals
cp "$CONFIG_FILE" "$CONFIG_FILE.test_bak"
cp "$STATE_FILE" "$STATE_FILE.test_bak"

PASS=0
FAIL=0
TOTAL=0

assert() {
    local name="$1"
    local expected="$2"
    local actual="$3"
    ((TOTAL++))
    if [[ "$actual" == *"$expected"* ]]; then
        echo "  ✅ $name"
        ((PASS++))
    else
        echo "  ❌ $name"
        echo "     expected to contain: $expected"
        echo "     got: $actual"
        ((FAIL++))
    fi
}

assert_not() {
    local name="$1"
    local unexpected="$2"
    local actual="$3"
    ((TOTAL++))
    if [[ "$actual" != *"$unexpected"* ]]; then
        echo "  ✅ $name"
        ((PASS++))
    else
        echo "  ❌ $name"
        echo "     expected NOT to contain: $unexpected"
        echo "     got: $actual"
        ((FAIL++))
    fi
}

cleanup() {
    mv "$CONFIG_FILE.test_bak" "$CONFIG_FILE"
    mv "$STATE_FILE.test_bak" "$STATE_FILE"
}
trap cleanup EXIT

echo "=== Starvation Guard Tests ==="
echo ""

# --- Test 1: Guard detects need at floor with no last_action_at ---
echo "Test 1: Detect need at floor with no last_action_at"

# Set all needs to sat=2.0 except 'expression' at 0.00
jq '
  to_entries | map(
    if .key == "expression" then
      .value.satisfaction = 0.00 |
      .value.last_action_at = null |
      .value.last_decay_check = "2026-03-07T00:00:00Z"
    else
      .value.satisfaction = 2.00 |
      .value.last_action_at = "2026-03-07T00:00:00Z" |
      .value.last_decay_check = "2026-03-07T00:00:00Z"
    end
  ) | from_entries
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Enable guard with 1h threshold (so expression is definitely starving)
jq '.settings.starvation_guard = {"enabled": true, "threshold_hours": 1, "sat_threshold": 0.5, "max_forced_per_cycle": 1}' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
assert "expression detected as starving" "Starvation guard: expression" "$OUTPUT"
assert "forced action for expression" "ACTION: expression" "$OUTPUT"
assert "STARVATION GUARD label shown" "STARVATION GUARD" "$OUTPUT"

echo ""

# --- Test 2: Guard disabled → no forcing ---
echo "Test 2: Guard disabled → no forced actions"

jq '.settings.starvation_guard.enabled = false' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
assert_not "no starvation guard message" "Starvation guard" "$OUTPUT"

echo ""

# --- Test 3: Need above sat_threshold → not starving ---
echo "Test 3: Need above threshold not starving"

jq '.settings.starvation_guard = {"enabled": true, "threshold_hours": 1, "sat_threshold": 0.5, "max_forced_per_cycle": 1}' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Set expression to sat=1.0 (above 0.5 threshold)
jq '.expression.satisfaction = 1.00' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
assert_not "expression not forced (above threshold)" "Starvation guard: expression" "$OUTPUT"

echo ""

# --- Test 4: Recent action → not starving ---
echo "Test 4: Recent action prevents starvation"

NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Set expression to sat=0.00 but with very recent action
jq --arg now "$NOW_ISO" '
  .expression.satisfaction = 0.00 |
  .expression.last_action_at = $now
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
assert_not "expression not forced (recent action)" "Starvation guard: expression" "$OUTPUT"

echo ""

# --- Test 5: mark-satisfied.sh sets last_action_at ---
echo "Test 5: mark-satisfied.sh records last_action_at"

WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/mark-satisfied.sh" expression 1.5 --reason "test action" > /dev/null 2>&1
LAST_ACTION=$(jq -r '.expression.last_action_at' "$STATE_FILE")
assert "last_action_at is set" "20" "$LAST_ACTION"  # starts with year prefix

echo ""

# --- Test 6: Multiple starving needs, max_forced=1 → only 1 forced ---
echo "Test 6: max_forced_per_cycle=1 limits forced actions"

jq '.settings.starvation_guard = {"enabled": true, "threshold_hours": 1, "sat_threshold": 0.5, "max_forced_per_cycle": 1}' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Set expression AND recognition to starving
jq '
  .expression.satisfaction = 0.00 | .expression.last_action_at = null |
  .recognition.satisfaction = 0.00 | .recognition.last_action_at = null
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
# Should have exactly 1 forced, not 2
FORCED_COUNT=$(echo "$OUTPUT" | grep -c "STARVATION GUARD")
assert "only 1 forced despite 2 starving" "1" "$FORCED_COUNT"

echo ""

# --- Test 7: Disabled need (importance=0) not detected as starving ---
echo "Test 7: importance=0 need excluded from starvation"

jq '.settings.starvation_guard = {"enabled": true, "threshold_hours": 1, "sat_threshold": 0.5, "max_forced_per_cycle": 1}' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Disable expression (importance=0) and set it at floor
jq '.needs.expression.importance = 0' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

jq 'to_entries | map(
    if .key == "expression" then
        .value.satisfaction = 0.00 |
        .value.last_action_at = null |
        .value.last_decay_check = "2026-03-07T00:00:00Z"
    else
        .value.satisfaction = 2.00 |
        .value.last_action_at = "2026-03-07T00:00:00Z" |
        .value.last_decay_check = "2026-03-07T00:00:00Z"
    end
) | from_entries' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
assert_not "importance=0 need not forced" "Starvation guard: expression" "$OUTPUT"

# Restore importance
jq '.needs.expression.importance = 1' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

echo ""

# --- Test 8: Forced need still gets proper action (not skip) ---
echo "Test 8: Forced need gets high impact action (sat=0.00)"

jq '.settings.starvation_guard = {"enabled": true, "threshold_hours": 1, "sat_threshold": 0.5, "max_forced_per_cycle": 1}' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

jq 'to_entries | map(
    if .key == "expression" then
        .value.satisfaction = 0.00 |
        .value.last_action_at = null |
        .value.last_decay_check = "2026-03-07T00:00:00Z"
    else
        .value.satisfaction = 3.00 |
        .value.last_action_at = "2026-03-07T00:00:00Z" |
        .value.last_decay_check = "2026-03-07T00:00:00Z"
    end
) | from_entries' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
# At sat=0.00, impact matrix gives 100% high range
assert "forced need gets action with impact" "★" "$OUTPUT"
assert "forced need shows mark-satisfied instruction" "mark-satisfied" "$OUTPUT"

echo ""

echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
exit $FAIL

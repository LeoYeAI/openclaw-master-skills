#!/bin/bash
# Tests for action staleness feature
# Tests: weight penalty, disabled, window expiry, min_weight, recording, distribution shift

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

assert_numeric() {
    local name="$1"
    local op="$2"    # -lt, -gt, -eq, -le, -ge
    local expected="$3"
    local actual="$4"
    ((TOTAL++))
    if [ "$actual" $op "$expected" ]; then
        echo "  ✅ $name (actual=$actual)"
        ((PASS++))
    else
        echo "  ❌ $name"
        echo "     expected: $op $expected, got: $actual"
        ((FAIL++))
    fi
}

cleanup() {
    mv "$CONFIG_FILE.test_bak" "$CONFIG_FILE"
    mv "$STATE_FILE.test_bak" "$STATE_FILE"
}
trap cleanup EXIT

# Source run-cycle.sh functions for unit testing
# We need NOW and NOW_ISO set
NOW=$(date +%s)
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "=== Action Staleness Tests ==="
echo ""

# --- Test 1: record_action_selection writes to state ---
echo "Test 1: record_action_selection writes to state"

# Reset state for expression
jq '.expression.satisfaction = 0.50 | .expression.last_decay_check = "2026-03-07T00:00:00Z" | .expression.action_history = {}' \
    "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Source the function (need SKILL_DIR context)
# We'll test via the full cycle instead — more reliable
# Set expression to crisis so it gets action, enable staleness
jq '.settings.action_staleness = {"enabled": true, "window_hours": 24, "penalty": 0.2, "min_weight": 5}' \
    "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Set only expression as needing action, others satisfied
jq 'to_entries | map(
    if .key == "expression" then
        .value.satisfaction = 0.00 |
        .value.last_decay_check = "2026-03-07T04:00:00Z" |
        .value.last_action_at = "2026-03-07T04:00:00Z" |
        .value.action_history = {}
    else
        .value.satisfaction = 3.00 |
        .value.last_decay_check = "2026-03-07T04:00:00Z" |
        .value.last_action_at = "2026-03-07T04:00:00Z"
    end
) | from_entries' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Disable starvation guard for clean test
jq '.settings.starvation_guard.enabled = false' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)

# Check that action_history was written
HISTORY=$(jq -r '.expression.action_history // empty | keys | length' "$STATE_FILE")
assert_numeric "action_history has entry after cycle" -ge 1 "$HISTORY"

echo ""

# --- Test 2: Stale action gets reduced weight (distribution shift) ---
echo "Test 2: Stale action shifts distribution"

# Expression has these high-impact actions:
# "write substantial post or essay" (weight 40)
# "develop scratchpad idea into finished piece" (weight 35)
# "create something new" (weight 25)
# 
# Mark "write substantial post" as recently used
# Run 50 cycles, count how often it's selected vs others

jq --arg now "$NOW_ISO" '
    .expression.satisfaction = 0.00 |
    .expression.action_history = {"write substantial post or essay": $now}
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

stale_count=0
fresh_count=0
FRESH_NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
for i in $(seq 1 50); do
    # Reset sat AND action_history each time (only target action is stale)
    jq --arg now "$FRESH_NOW" '
        .expression.satisfaction = 0.00 |
        .expression.last_decay_check = "2026-03-07T04:00:00Z" |
        .expression.action_history = {"write substantial post or essay": $now}
    ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    OUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
    if echo "$OUT" | grep -q "write substantial post or essay"; then
        ((stale_count++))
    else
        ((fresh_count++))
    fi
done

# Without staleness, "write substantial post" has 40/(40+35+25)=40% chance → ~20/50
# With staleness penalty 0.2, effective weight = 8, so 8/(8+35+25)=11.8% → ~6/50
# Fresh actions should dominate
assert_numeric "stale action selected less often (< 20 of 50)" -lt 20 "$stale_count"
assert_numeric "fresh actions selected more often (> 30 of 50)" -gt 30 "$fresh_count"

echo ""

# --- Test 3: Staleness disabled → normal distribution ---
echo "Test 3: Staleness disabled → no penalty"

jq '.settings.action_staleness.enabled = false' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Same setup: "write substantial post" marked as recent
jq --arg now "$NOW_ISO" '
    .expression.satisfaction = 0.00 |
    .expression.action_history = {"write substantial post or essay": $now}
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

disabled_stale_count=0
for i in $(seq 1 50); do
    jq --arg now "$FRESH_NOW" '
        .expression.satisfaction = 0.00 |
        .expression.last_decay_check = "2026-03-07T04:00:00Z" |
        .expression.action_history = {"write substantial post or essay": $now}
    ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    OUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
    if echo "$OUT" | grep -q "write substantial post or essay"; then
        ((disabled_stale_count++))
    fi
done

# Without penalty, should be around 40% → ~20/50
# Should be noticeably higher than with penalty
assert_numeric "without penalty, stale action selected more (> stale_count=$stale_count)" -gt "$stale_count" "$disabled_stale_count"

echo ""

# Re-enable for remaining tests
jq '.settings.action_staleness.enabled = true' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# --- Test 4: Action outside window → no penalty ---
echo "Test 4: Action outside staleness window → normal weight"

# Set action_history to 48h ago (window is 24h)
OLD_TIME=$(date -u -d "48 hours ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v-48H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)
jq --arg old "$OLD_TIME" '
    .expression.satisfaction = 0.00 |
    .expression.action_history = {"write substantial post or essay": $old}
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

old_count=0
for i in $(seq 1 30); do
    jq --arg old "$OLD_TIME" '
        .expression.satisfaction = 0.00 |
        .expression.last_decay_check = "2026-03-07T04:00:00Z" |
        .expression.action_history = {"write substantial post or essay": $old}
    ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    OUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
    if echo "$OUT" | grep -q "write substantial post or essay"; then
        ((old_count++))
    fi
done

# 40% chance over 30 runs → expect ~12. Should be > 5 at least
assert_numeric "expired staleness: action selected normally (> 5 of 30)" -gt 5 "$old_count"

echo ""

# --- Test 5: min_weight prevents total suppression ---
echo "Test 5: min_weight prevents zero weight"

# Set penalty to 0.01 (would make weight < 1) but min_weight=5 catches it
jq '.settings.action_staleness.penalty = 0.01 | .settings.action_staleness.min_weight = 5' \
    "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

jq --arg now "$NOW_ISO" '
    .expression.satisfaction = 0.00 |
    .expression.action_history = {"write substantial post or essay": $now}
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

min_count=0
for i in $(seq 1 50); do
    jq --arg now "$FRESH_NOW" '
        .expression.satisfaction = 0.00 |
        .expression.last_decay_check = "2026-03-07T04:00:00Z" |
        .expression.action_history = {"write substantial post or essay": $now}
    ' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    OUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
    if echo "$OUT" | grep -q "write substantial post or essay"; then
        ((min_count++))
    fi
done

# min_weight=5 out of (5+35+25)=65 → ~7.7% → ~4/50. Should be > 0 but < 15
assert_numeric "min_weight: action still selected sometimes (> 0)" -gt 0 "$min_count"
assert_numeric "min_weight: action still penalized (< 15)" -lt 15 "$min_count"

# Restore penalty
jq '.settings.action_staleness.penalty = 0.2' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

echo ""

# --- Test 6: No action_history field → treated as fresh ---
echo "Test 6: Missing action_history → no penalty"

jq 'del(.expression.action_history)' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
assert "cycle runs without action_history" "ACTION: expression" "$OUTPUT"

echo ""

# --- Test 7: Action history cleanup removes expired entries ---
echo "Test 7: action_history cleanup removes old entries"

# Re-enable staleness
jq '.settings.action_staleness = {"enabled": true, "window_hours": 24, "penalty": 0.2, "min_weight": 5}' \
    "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

OLD_TIME=$(date -u -d "48 hours ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v-48H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)
RECENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Set expression with 1 old + 1 recent entry in action_history
jq --arg old "$OLD_TIME" --arg recent "$RECENT_TIME" '
    .expression.satisfaction = 0.00 |
    .expression.last_decay_check = "2026-03-07T04:00:00Z" |
    .expression.last_action_at = "2026-03-07T04:00:00Z" |
    .expression.action_history = {
        "old expired action": $old,
        "write substantial post or essay": $recent
    }
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Disable starvation guard for clean test
jq '.settings.starvation_guard.enabled = false' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)

# After cycle, the old entry should be cleaned up
OLD_ENTRY=$(jq -r '.expression.action_history["old expired action"] // "GONE"' "$STATE_FILE")
assert "expired entry removed from action_history" "GONE" "$OLD_ENTRY"

# Recent entry should still exist (or be updated)
REMAINING=$(jq -r '.expression.action_history | keys | length' "$STATE_FILE")
assert_numeric "action_history not empty (recent entries kept)" -ge 1 "$REMAINING"

echo ""

# --- Test 8: Both features active — starvation + staleness interaction ---
echo "Test 8: Starvation guard + staleness work together"

jq '.settings.starvation_guard = {"enabled": true, "threshold_hours": 1, "sat_threshold": 0.5, "max_forced_per_cycle": 1}' \
    "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
jq '.settings.action_staleness = {"enabled": true, "window_hours": 24, "penalty": 0.2, "min_weight": 5}' \
    "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

FRESH_NOW2=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# expression: starving (sat=0, no last_action_at) + "write substantial post" is stale
jq --arg now "$FRESH_NOW2" '
    to_entries | map(
        if .key == "expression" then
            .value.satisfaction = 0.00 |
            .value.last_action_at = null |
            .value.last_decay_check = "2026-03-07T04:00:00Z" |
            .value.action_history = {"write substantial post or essay": $now}
        else
            .value.satisfaction = 2.00 |
            .value.last_action_at = "2026-03-07T04:00:00Z" |
            .value.last_decay_check = "2026-03-07T04:00:00Z"
        end
    ) | from_entries
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)

# Should be forced AND staleness should apply
assert "forced + staleness: expression forced" "STARVATION GUARD" "$OUTPUT"
assert "forced + staleness: action selected" "★" "$OUTPUT"

echo ""

# --- Test 9: All actions in range are stale — min_weight prevents deadlock ---
echo "Test 9: All stale actions still selectable via min_weight"

jq '.settings.starvation_guard.enabled = false' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Mark ALL high-impact expression actions as stale
jq --arg now "$FRESH_NOW2" '
    .expression.satisfaction = 0.00 |
    .expression.last_decay_check = "2026-03-07T04:00:00Z" |
    .expression.action_history = {
        "write substantial post or essay": $now,
        "develop scratchpad idea into finished piece": $now,
        "create something new (script, tool, doc)": $now
    }
' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

OUTPUT=$(WORKSPACE="$SKILL_DIR/../.." bash "$SCRIPTS_DIR/run-cycle.sh" --no-scans 2>&1)
# Should still select an action (min_weight prevents all-zero)
assert "all stale: still selects action" "★" "$OUTPUT"

echo ""

echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
exit $FAIL

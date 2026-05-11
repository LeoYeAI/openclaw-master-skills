#!/usr/bin/env bash
# test_research_threads.sh - Tests for research thread integration in understanding need
# Validates: config, scanner, action selection

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG="$SKILL_DIR/assets/needs-config.json"
CROSS="$SKILL_DIR/assets/cross-need-impact.json"

PASSED=0
FAILED=0

pass() { echo "  ✅ $1"; PASSED=$((PASSED + 1)); }
fail() { echo "  ❌ $1"; FAILED=$((FAILED + 1)); }

echo "🧪 Research Thread Integration Tests"
echo "======================================"

# --- Config tests ---

echo ""
echo "📋 Config tests:"

# Test 1: understanding importance raised to 4
imp=$(jq '.needs.understanding.importance' "$CONFIG")
[[ "$imp" == "4" ]] && pass "understanding importance = 4" || fail "understanding importance = $imp (expected 4)"

# Test 2: decay rate set to 8h
decay=$(jq '.needs.understanding.decay_rate_hours' "$CONFIG")
[[ "$decay" == "8" ]] && pass "understanding decay_rate = 8h" || fail "understanding decay_rate = $decay (expected 8)"

# Test 3: research thread actions exist
thread_actions=$(jq '[.needs.understanding.actions[] | select(.name | test("research thread"))] | length' "$CONFIG")
[[ "$thread_actions" -ge 3 ]] && pass "3 research thread actions present ($thread_actions)" || fail "research thread actions = $thread_actions (expected >= 3)"

# Test 4: continue-thread action has high weight
continue_weight=$(jq '.needs.understanding.actions[] | select(.name | test("continue active")) | .weight' "$CONFIG")
[[ "$continue_weight" -ge 50 ]] && pass "continue-thread weight = $continue_weight (>= 50)" || fail "continue-thread weight = $continue_weight (expected >= 50)"

# Test 5: start-thread action has appropriate impact
start_impact=$(jq '.needs.understanding.actions[] | select(.name | test("start new research")) | .impact' "$CONFIG")
[[ $(echo "$start_impact >= 2.0" | bc -l) -eq 1 ]] && pass "start-thread impact = $start_impact (>= 2.0)" || fail "start-thread impact = $start_impact (expected >= 2.0)"

# Test 6: synthesize action exists with mid-range impact
synth_impact=$(jq '.needs.understanding.actions[] | select(.name | test("synthesize")) | .impact' "$CONFIG")
[[ -n "$synth_impact" ]] && pass "synthesize action exists (impact=$synth_impact)" || fail "synthesize action missing"

# Test 7: total actions count (was 10 + 3 new = 13)
total_actions=$(jq '.needs.understanding.actions | length' "$CONFIG")
[[ "$total_actions" -ge 13 ]] && pass "total understanding actions = $total_actions (>= 13)" || fail "total actions = $total_actions (expected >= 13)"

# --- Cross-need impact tests ---

echo ""
echo "🔗 Cross-need impact tests:"

# Test 8: understanding → coherence exists
u_to_c=$(jq '[.impacts[] | select(.source == "understanding" and .target == "coherence")] | length' "$CROSS")
[[ "$u_to_c" -ge 1 ]] && pass "understanding → coherence impact exists" || fail "understanding → coherence missing"

# Test 9: understanding → expression exists (pre-existing)
u_to_e=$(jq '[.impacts[] | select(.source == "understanding" and .target == "expression")] | length' "$CROSS")
[[ "$u_to_e" -ge 1 ]] && pass "understanding → expression impact exists" || fail "understanding → expression missing"

# Test 10: understanding → competence exists (pre-existing)
u_to_comp=$(jq '[.impacts[] | select(.source == "understanding" and .target == "competence")] | length' "$CROSS")
[[ "$u_to_comp" -ge 1 ]] && pass "understanding → competence impact exists" || fail "understanding → competence missing"

# --- Scanner tests ---

echo ""
echo "🔍 Scanner tests:"

# Test 11: scanner detects research thread files
export WORKSPACE=$(mktemp -d)
mkdir -p "$WORKSPACE/memory" "$WORKSPACE/research/threads/test_topic"
echo "## Test entry" > "$WORKSPACE/research/threads/test_topic/test-thread.md"
touch -t "$(date +%Y%m%d%H%M)" "$WORKSPACE/research/threads/test_topic/test-thread.md"

# Create minimal needs-state and config for scanner
mkdir -p "$WORKSPACE/skills/turing-pyramid/assets"
cp "$SKILL_DIR/assets/needs-config.json" "$WORKSPACE/skills/turing-pyramid/assets/"
echo '{"needs":{"understanding":{"satisfaction":1.0,"last_satisfied":"2026-01-01T00:00:00Z","deprivation":3,"last_decay_check":"2026-01-01T00:00:00Z"}}}' > "$WORKSPACE/skills/turing-pyramid/assets/needs-state.json"
cp "$SKILL_DIR/assets/decay-config.json" "$WORKSPACE/skills/turing-pyramid/assets/" 2>/dev/null || echo '{}' > "$WORKSPACE/skills/turing-pyramid/assets/decay-config.json"

# Create empty memory files to avoid errors
echo "" > "$WORKSPACE/memory/$(date +%Y-%m-%d).md"

result=$(bash "$SKILL_DIR/scripts/scan_understanding.sh" 2>/dev/null || echo "error")
if [[ "$result" != "error" ]] && [[ "$result" -ge 1 ]]; then
    pass "scanner detects research threads (result=$result)"
else
    fail "scanner failed to detect threads (result=$result)"
fi

# Test 12: scanner works without threads dir
export WORKSPACE=$(mktemp -d)
mkdir -p "$WORKSPACE/memory"
mkdir -p "$WORKSPACE/skills/turing-pyramid/assets"
cp "$SKILL_DIR/assets/needs-config.json" "$WORKSPACE/skills/turing-pyramid/assets/"
echo '{"needs":{"understanding":{"satisfaction":1.0,"last_satisfied":"2026-01-01T00:00:00Z","deprivation":3,"last_decay_check":"2026-01-01T00:00:00Z"}}}' > "$WORKSPACE/skills/turing-pyramid/assets/needs-state.json"
cp "$SKILL_DIR/assets/decay-config.json" "$WORKSPACE/skills/turing-pyramid/assets/" 2>/dev/null || echo '{}' > "$WORKSPACE/skills/turing-pyramid/assets/decay-config.json"
echo "" > "$WORKSPACE/memory/$(date +%Y-%m-%d).md"

result=$(bash "$SKILL_DIR/scripts/scan_understanding.sh" 2>/dev/null || echo "error")
if [[ "$result" != "error" ]]; then
    pass "scanner works without threads dir (result=$result)"
else
    fail "scanner crashes without threads dir"
fi

# --- Weight compatibility test ---

echo ""
echo "⚖️ Weight tests:"

# Test 13: daemon-weights.json referenced in action name exists
if [[ -f "$HOME/.openclaw/workspace/daemon-weights.json" ]]; then
    pass "daemon-weights.json exists (referenced by start-thread action)"
else
    fail "daemon-weights.json missing (referenced by start-thread action)"
fi

# Test 14: action weights sum reasonably (not all 100)
total_weight=$(jq '[.needs.understanding.actions[].weight] | add' "$CONFIG")
action_count=$(jq '.needs.understanding.actions | length' "$CONFIG")
avg_weight=$(echo "$total_weight / $action_count" | bc -l)
if (( $(echo "$avg_weight > 20 && $avg_weight < 80" | bc -l) )); then
    pass "average action weight = $(printf '%.0f' $avg_weight) (reasonable range)"
else
    fail "average action weight = $(printf '%.0f' $avg_weight) (outside 20-80 range)"
fi

echo ""
echo "======================================"
echo "Results: $PASSED passed, $FAILED failed"
[[ $FAILED -eq 0 ]] && exit 0 || exit 1

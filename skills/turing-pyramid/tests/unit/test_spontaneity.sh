#!/usr/bin/env bash
# Test: Spontaneity Layer A — surplus accumulation, gate, matrix shift, spend
set -uo pipefail
# Note: NOT using set -e because we test functions that return non-zero (gate check returns 1 for closed)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
FIXTURES="$SCRIPT_DIR/../fixtures"

export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"

# Source the module under test
source "$SKILL_DIR/scripts/spontaneity.sh"

errors=0
pass=0

assert_eq() {
    local desc=$1 expected=$2 actual=$3
    if [[ "$expected" == "$actual" ]]; then
        echo "  ✅ $desc"
        ((pass++))
    else
        echo "  ❌ $desc: expected '$expected', got '$actual'"
        ((errors++))
    fi
}

assert_float_near() {
    local desc=$1 expected=$2 actual=$3 tolerance=${4:-0.1}
    local diff
    diff=$(echo "scale=4; $actual - $expected" | bc -l)
    diff=${diff#-}  # abs
    if (( $(echo "$diff <= $tolerance" | bc -l) )); then
        echo "  ✅ $desc ($actual ≈ $expected)"
        ((pass++))
    else
        echo "  ❌ $desc: expected ≈$expected (±$tolerance), got $actual"
        ((errors++))
    fi
}

# ─── Setup: create temp state and config ───
TMP_DIR=$(mktemp -d)
TMP_STATE="$TMP_DIR/needs-state.json"
TMP_CONFIG="$TMP_DIR/needs-config.json"
trap "rm -rf $TMP_DIR" EXIT

# Minimal config with spontaneity
cat > "$TMP_CONFIG" << 'CONF'
{
  "settings": {
    "spontaneity": {
      "enabled": true,
      "baseline": 2.0,
      "gate_min_satisfaction": 1.5,
      "default_threshold": 10,
      "default_cap": 48,
      "max_spend_ratio": 0.8,
      "spend_on_miss_ratio": 0.3
    }
  },
  "needs": {
    "expression": {
      "importance": 1,
      "decay_rate_hours": 8,
      "spontaneous": {
        "enabled": true,
        "target_matrix": { "low": 5, "mid": 25, "high": 70 },
        "cap": 48,
        "threshold": 10
      }
    },
    "security": {
      "importance": 10,
      "decay_rate_hours": 168,
      "spontaneous": null
    },
    "connection": {
      "importance": 5,
      "decay_rate_hours": 12,
      "spontaneous": {
        "enabled": true,
        "target_matrix": { "low": 10, "mid": 30, "high": 60 },
        "cap": 48,
        "threshold": 10
      }
    }
  }
}
CONF

reset_state() {
    local sat_expr=${1:-2.5} sat_sec=${2:-2.5} sat_conn=${3:-2.5}
    local surplus_expr=${4:-0} surplus_conn=${5:-0}
    local hours_ago=${6:-10}
    local ts
    ts=$(date -u -d "$hours_ago hours ago" +"%Y-%m-%dT%H:%M:%SZ")
    cat > "$TMP_STATE" << STATE
{
  "expression": {
    "satisfaction": $sat_expr,
    "surplus": $surplus_expr,
    "last_surplus_check": "$ts",
    "last_decay_check": "$ts"
  },
  "security": {
    "satisfaction": $sat_sec,
    "last_decay_check": "$ts"
  },
  "connection": {
    "satisfaction": $sat_conn,
    "surplus": $surplus_conn,
    "last_surplus_check": "$ts",
    "last_decay_check": "$ts"
  }
}
STATE
}

echo "═══ Test Suite: Spontaneity Layer A ═══"
echo ""

# ──────────────────────────────────────
echo "── Test 1: Gate check — all satisfied ──"
reset_state 2.5 2.5 2.5
if check_spontaneity_gate "$TMP_STATE" "$TMP_CONFIG" "false"; then
    assert_eq "gate opens when all sats >= 1.5" "open" "open"
else
    assert_eq "gate opens when all sats >= 1.5" "open" "closed"
fi

# ──────────────────────────────────────
echo "── Test 2: Gate check — one need below threshold ──"
reset_state 2.5 2.5 1.3  # connection=1.3 < 1.5
if check_spontaneity_gate "$TMP_STATE" "$TMP_CONFIG" "false"; then
    assert_eq "gate closed when connection=1.3" "closed" "open"
else
    assert_eq "gate closed when connection=1.3" "closed" "closed"
fi

# ──────────────────────────────────────
echo "── Test 3: Gate check — starvation active ──"
reset_state 2.5 2.5 2.5
if check_spontaneity_gate "$TMP_STATE" "$TMP_CONFIG" "true"; then
    assert_eq "gate closed during starvation" "closed" "open"
else
    assert_eq "gate closed during starvation" "closed" "closed"
fi

# ──────────────────────────────────────
echo "── Test 4: Gate check — exactly at threshold ──"
reset_state 1.5 1.5 1.5
if check_spontaneity_gate "$TMP_STATE" "$TMP_CONFIG" "false"; then
    assert_eq "gate opens at exact threshold 1.5" "open" "open"
else
    assert_eq "gate opens at exact threshold 1.5" "open" "closed"
fi

# ──────────────────────────────────────
echo "── Test 5: Surplus accumulation — positive delta ──"
reset_state 2.5 2.5 2.5 0 0 10
accumulate_surplus "$TMP_STATE" "$TMP_CONFIG" "false" > /dev/null 2>&1

surplus_expr=$(jq -r '.expression.surplus' "$TMP_STATE")
surplus_conn=$(jq -r '.connection.surplus' "$TMP_STATE")
# Expected: (2.5 - 2.0) * 10h = 5.0
assert_float_near "expression surplus after 10h at sat=2.5" "5.0" "$surplus_expr" 0.2
assert_float_near "connection surplus after 10h at sat=2.5" "5.0" "$surplus_conn" 0.2

# ──────────────────────────────────────
echo "── Test 6: Surplus accumulation — negative delta (drain) ──"
reset_state 1.6 2.5 2.5 20 0 10  # expression sat=1.6 < baseline=2.0, surplus=20
accumulate_surplus "$TMP_STATE" "$TMP_CONFIG" "false" > /dev/null 2>&1

surplus_expr=$(jq -r '.expression.surplus' "$TMP_STATE")
# Expected: 20 + (1.6 - 2.0) * 10 = 20 - 4 = 16
assert_float_near "surplus drains when sat < baseline" "16.0" "$surplus_expr" 0.2

# ──────────────────────────────────────
echo "── Test 7: Surplus accumulation — clamped at cap ──"
reset_state 3.0 2.5 2.5 45 0 10  # expression surplus=45, sat=3.0
accumulate_surplus "$TMP_STATE" "$TMP_CONFIG" "false" > /dev/null 2>&1

surplus_expr=$(jq -r '.expression.surplus' "$TMP_STATE")
# Expected: 45 + (3.0-2.0)*10 = 55, clamped to 48
assert_float_near "surplus capped at 48" "48.0" "$surplus_expr" 0.1

# ──────────────────────────────────────
echo "── Test 8: Surplus accumulation — clamped at 0 ──"
reset_state 1.5 2.5 2.5 2 0 10  # expression surplus=2, sat=1.5
accumulate_surplus "$TMP_STATE" "$TMP_CONFIG" "false" > /dev/null 2>&1

surplus_expr=$(jq -r '.expression.surplus' "$TMP_STATE")
# Expected: 2 + (1.5-2.0)*10 = 2 - 5 = -3, clamped to 0
assert_float_near "surplus floored at 0" "0.0" "$surplus_expr" 0.1

# ──────────────────────────────────────
echo "── Test 9: Surplus freezes when gate closed ──"
reset_state 2.5 2.5 1.3 15 10 10  # connection=1.3 → gate closed
accumulate_surplus "$TMP_STATE" "$TMP_CONFIG" "false" > /dev/null 2>&1

surplus_expr=$(jq -r '.expression.surplus' "$TMP_STATE")
surplus_conn=$(jq -r '.connection.surplus' "$TMP_STATE")
# Gate closed → surplus freezes at previous values
assert_float_near "expression surplus frozen (gate closed)" "15.0" "$surplus_expr" 0.1
assert_float_near "connection surplus frozen (gate closed)" "10.0" "$surplus_conn" 0.1

# ──────────────────────────────────────
echo "── Test 10: Security need skipped (spontaneous:null) ──"
reset_state 2.5 2.5 2.5 0 0 10
accumulate_surplus "$TMP_STATE" "$TMP_CONFIG" "false" > /dev/null 2>&1

sec_surplus=$(jq -r '.security.surplus // "null"' "$TMP_STATE")
assert_eq "security has no surplus field" "null" "$sec_surplus"

# ──────────────────────────────────────
echo "── Test 11: Matrix shift — not eligible (surplus < threshold) ──"
reset_state 2.5 2.5 2.5 5 0  # surplus=5, threshold=10
result=$(get_shifted_matrix "expression" 45 40 15 "$TMP_STATE" "$TMP_CONFIG")
assert_eq "no shift when surplus=5 < threshold=10" "none" "$result"

# ──────────────────────────────────────
echo "── Test 12: Matrix shift — not eligible (max_spend < threshold) ──"
# surplus=10, max_spend=10*0.8=8 < threshold=10 → NOT eligible
reset_state 2.5 2.5 2.5 10 0
result=$(get_shifted_matrix "expression" 45 40 15 "$TMP_STATE" "$TMP_CONFIG")
assert_eq "no shift when max_spend=8 < threshold=10" "none" "$result"

# ──────────────────────────────────────
echo "── Test 13: Matrix shift — eligible (surplus=13, max_spend=10.4) ──"
reset_state 2.5 2.5 2.5 13 0
result=$(get_shifted_matrix "expression" 45 40 15 "$TMP_STATE" "$TMP_CONFIG")

if [[ "$result" == "none" ]]; then
    assert_eq "shift should trigger at surplus=13" "shifted" "none"
else
    # Parse result
    s_low=$(echo "$result" | awk '{print $1}')
    s_mid=$(echo "$result" | awk '{print $2}')
    s_high=$(echo "$result" | awk '{print $3}')
    spend=$(echo "$result" | awk '{print $4}')
    t_val=$(echo "$result" | awk '{print $5}')
    
    # Verify sum = 100
    total=$((s_low + s_mid + s_high))
    assert_eq "shifted matrix sums to 100" "100" "$total"
    
    # Verify high > normal high (15)
    if [[ $s_high -gt 15 ]]; then
        assert_eq "shifted high > normal 15" "true" "true"
    else
        assert_eq "shifted high > normal 15" "true" "false (got $s_high)"
    fi
    
    # Verify spend is between threshold(10) and max_spend(10.4)
    if (( $(echo "$spend >= 10" | bc -l) )) && (( $(echo "$spend <= 10.4" | bc -l) )); then
        assert_eq "spend in range [10, 10.4]" "true" "true"
    else
        assert_eq "spend in range [10, 10.4]" "true" "false (got $spend)"
    fi
    
    # Verify t_val > 0
    if (( $(echo "$t_val > 0" | bc -l) )); then
        assert_eq "t > 0" "true" "true"
    else
        assert_eq "t > 0" "true" "false"
    fi
fi

# ──────────────────────────────────────
echo "── Test 14: Matrix shift — security (null) returns none ──"
result=$(get_shifted_matrix "security" 45 40 15 "$TMP_STATE" "$TMP_CONFIG")
assert_eq "security always returns none" "none" "$result"

# ──────────────────────────────────────
echo "── Test 15: Spend surplus — full spend on HIGH ──"
reset_state 2.5 2.5 2.5 20 0
spend_surplus "expression" "high" "12.5" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null

surplus_after=$(jq -r '.expression.surplus' "$TMP_STATE")
# Expected: 20 - 12.5 = 7.5
assert_float_near "full spend on high: 20 - 12.5 = 7.5" "7.5" "$surplus_after" 0.1

# ──────────────────────────────────────
echo "── Test 16: Spend surplus — partial spend on MID (miss) ──"
reset_state 2.5 2.5 2.5 20 0
spend_surplus "expression" "mid" "12.5" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null

surplus_after=$(jq -r '.expression.surplus' "$TMP_STATE")
# Expected: 20 - (12.5 * 0.3) = 20 - 3.75 = 16.25
assert_float_near "partial spend on mid: 20 - 3.75 = 16.25" "16.25" "$surplus_after" 0.2

# ──────────────────────────────────────
echo "── Test 17: Spend surplus — partial spend on LOW (miss) ──"
reset_state 2.5 2.5 2.5 20 0
spend_surplus "expression" "low" "10.0" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null

surplus_after=$(jq -r '.expression.surplus' "$TMP_STATE")
# Expected: 20 - (10.0 * 0.3) = 20 - 3.0 = 17.0
assert_float_near "partial spend on low: 20 - 3.0 = 17.0" "17.0" "$surplus_after" 0.1

# ──────────────────────────────────────
echo "── Test 18: Spend surplus — clamp at zero ──"
reset_state 2.5 2.5 2.5 5 0
spend_surplus "expression" "high" "10.0" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null

surplus_after=$(jq -r '.expression.surplus' "$TMP_STATE")
# Expected: 5 - 10 = -5, clamped to 0
assert_float_near "spend clamps at 0" "0.0" "$surplus_after" 0.1

# ──────────────────────────────────────
echo "── Test 19: High surplus shifts matrix strongly ──"
reset_state 2.5 2.5 2.5 48 0  # max surplus
result=$(get_shifted_matrix "expression" 45 40 15 "$TMP_STATE" "$TMP_CONFIG")

if [[ "$result" != "none" ]]; then
    s_high=$(echo "$result" | awk '{print $3}')
    # At surplus=48: min_spend=10, t_min=10/48=0.21 → high_min = 15+55*0.21 ≈ 27
    # Random roll can be anywhere in [10, 38.4], so high >= 26 is safe lower bound
    if [[ $s_high -gt 25 ]]; then
        assert_eq "high surplus → meaningful high shift (>25, got $s_high)" "true" "true"
    else
        assert_eq "high surplus → meaningful high shift (>25)" "true" "false (got $s_high)"
    fi
else
    assert_eq "should shift at max surplus" "shifted" "none"
fi

# ──────────────────────────────────────
echo "── Test 20: Accumulation skipped for disabled needs ──"
# Add a need with spontaneous.enabled=false
jq '.needs.test_disabled = {"importance": 1, "decay_rate_hours": 8, "spontaneous": {"enabled": false, "target_matrix": {"low": 10, "mid": 30, "high": 60}, "cap": 48, "threshold": 10}}' "$TMP_CONFIG" > "$TMP_CONFIG.tmp" && mv "$TMP_CONFIG.tmp" "$TMP_CONFIG"
jq '.test_disabled = {"satisfaction": 2.5, "surplus": 5, "last_surplus_check": "2026-03-15T10:00:00Z"}' "$TMP_STATE" > "$TMP_STATE.tmp" && mv "$TMP_STATE.tmp" "$TMP_STATE"

accumulate_surplus "$TMP_STATE" "$TMP_CONFIG" "false" > /dev/null 2>&1
surplus_disabled=$(jq -r '.test_disabled.surplus' "$TMP_STATE")
# Should remain 5 — not accumulated
assert_float_near "disabled need surplus unchanged" "5.0" "$surplus_disabled" 0.1

echo ""
echo "═══════════════════════════════════"
echo "Results: $pass passed, $errors failed"
echo "═══════════════════════════════════"

exit $errors

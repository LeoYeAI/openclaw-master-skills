#!/usr/bin/env bash
# Test: Spontaneity Layer B — Boredom Noise + Momentum Echo
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
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
    local desc=$1 expected=$2 actual=$3 tolerance=${4:-0.005}
    local diff
    diff=$(echo "scale=6; $actual - $expected" | bc -l)
    diff=${diff#-}
    if (( $(echo "$diff <= $tolerance" | bc -l) )); then
        echo "  ✅ $desc ($actual ≈ $expected)"
        ((pass++))
    else
        echo "  ❌ $desc: expected ≈$expected (±$tolerance), got $actual"
        ((errors++))
    fi
}

TMP_DIR=$(mktemp -d)
TMP_STATE="$TMP_DIR/needs-state.json"
TMP_CONFIG="$TMP_DIR/needs-config.json"
trap "rm -rf $TMP_DIR" EXIT

# Config with noise + echo
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
      "spend_on_miss_ratio": 0.3,
      "noise": {
        "enabled": true,
        "base_noise": 0.03,
        "norm_hours": 24,
        "max_multiplier": 3,
        "noise_cap": 0.12,
        "high_impact_threshold": 2.0
      },
      "echo": {
        "enabled": true,
        "echo_base": 0.08,
        "echo_duration_hours": 24
      }
    }
  },
  "needs": {
    "expression": {
      "importance": 1,
      "spontaneous": {
        "enabled": true,
        "target_matrix": { "low": 5, "mid": 25, "high": 70 },
        "cap": 48,
        "threshold": 10
      }
    },
    "security": {
      "importance": 10,
      "spontaneous": null
    }
  }
}
CONF

reset_state() {
    local high_hours_ago=${1:-24}
    local spont_hours_ago=${2:-48}
    local high_ts spont_ts
    high_ts=$(date -u -d "$high_hours_ago hours ago" +"%Y-%m-%dT%H:%M:%SZ")
    spont_ts=$(date -u -d "$spont_hours_ago hours ago" +"%Y-%m-%dT%H:%M:%SZ")
    cat > "$TMP_STATE" << STATE
{
  "expression": {
    "satisfaction": 2.5,
    "surplus": 0,
    "last_surplus_check": "2026-03-16T00:00:00Z",
    "last_high_action_at": "$high_ts",
    "last_spontaneous_at": "$spont_ts",
    "last_action_at": "2026-03-16T00:00:00Z"
  },
  "security": {
    "satisfaction": 2.5,
    "last_decay_check": "2026-03-16T00:00:00Z"
  }
}
STATE
}

echo "═══ Test Suite: Spontaneity Layer B ═══"
echo ""

# ── B2: Boredom Noise ──

echo "── Test 1: Boredom at 0 hours (just did high action) ──"
reset_state 0 48
result=$(calc_boredom_noise "expression" "$TMP_STATE" "$TMP_CONFIG")
# 0h/24h = 0 multiplier → 0.03 * 0 = 0
assert_float_near "boredom at 0h" "0.0000" "$result" 0.002

echo "── Test 2: Boredom at 24 hours (baseline) ──"
reset_state 24 48
result=$(calc_boredom_noise "expression" "$TMP_STATE" "$TMP_CONFIG")
# 24/24 = 1 → 0.03 * 1 = 0.03
assert_float_near "boredom at 24h" "0.0300" "$result" 0.002

echo "── Test 3: Boredom at 48 hours ──"
reset_state 48 48
result=$(calc_boredom_noise "expression" "$TMP_STATE" "$TMP_CONFIG")
# 48/24 = 2 → 0.03 * 2 = 0.06
assert_float_near "boredom at 48h" "0.0600" "$result" 0.002

echo "── Test 4: Boredom at 72+ hours (max) ──"
reset_state 100 48
result=$(calc_boredom_noise "expression" "$TMP_STATE" "$TMP_CONFIG")
# 100/24 = 4.17, capped at 3 → 0.03 * 3 = 0.09
assert_float_near "boredom at 100h (capped)" "0.0900" "$result" 0.002

echo "── Test 5: Boredom for disabled need ──"
result=$(calc_boredom_noise "security" "$TMP_STATE" "$TMP_CONFIG")
assert_eq "security boredom = 0" "0" "$result"

echo "── Test 6: Boredom at 12 hours ──"
reset_state 12 48
result=$(calc_boredom_noise "expression" "$TMP_STATE" "$TMP_CONFIG")
# 12/24 = 0.5 → 0.03 * 0.5 = 0.015
assert_float_near "boredom at 12h" "0.0150" "$result" 0.002

# ── B3: Momentum Echo ──

echo "── Test 7: Echo right after spontaneous (0h) ──"
reset_state 24 0
result=$(calc_echo_boost "expression" "$TMP_STATE" "$TMP_CONFIG")
# (1 - 0/24) * 0.08 = 0.08
assert_float_near "echo at 0h" "0.0800" "$result" 0.005

echo "── Test 8: Echo at 12 hours ──"
reset_state 24 12
result=$(calc_echo_boost "expression" "$TMP_STATE" "$TMP_CONFIG")
# (1 - 12/24) * 0.08 = 0.04
assert_float_near "echo at 12h" "0.0400" "$result" 0.005

echo "── Test 9: Echo at 24 hours (expired) ──"
reset_state 24 24
result=$(calc_echo_boost "expression" "$TMP_STATE" "$TMP_CONFIG")
assert_eq "echo at 24h = 0" "0" "$result"

echo "── Test 10: Echo at 48 hours (long expired) ──"
reset_state 24 48
result=$(calc_echo_boost "expression" "$TMP_STATE" "$TMP_CONFIG")
assert_eq "echo at 48h = 0" "0" "$result"

echo "── Test 11: Echo for disabled need ──"
result=$(calc_echo_boost "security" "$TMP_STATE" "$TMP_CONFIG")
assert_eq "security echo = 0" "0" "$result"

echo "── Test 12: Echo at 6 hours ──"
reset_state 24 6
result=$(calc_echo_boost "expression" "$TMP_STATE" "$TMP_CONFIG")
# (1 - 6/24) * 0.08 = 0.06
assert_float_near "echo at 6h" "0.0600" "$result" 0.005

# ── Combined: try_noise_upgrade ──

echo "── Test 13: No upgrade when range=high ──"
reset_state 100 0  # max boredom + max echo
result=$(try_noise_upgrade "expression" "high" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null)
assert_eq "high stays high" "high" "$result"

echo "── Test 14: No upgrade when range=skip ──"
result=$(try_noise_upgrade "expression" "skip" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null)
assert_eq "skip stays skip" "skip" "$result"

echo "── Test 15: No upgrade for disabled need ──"
reset_state 100 0
result=$(try_noise_upgrade "security" "low" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null)
assert_eq "security low stays low" "low" "$result"

echo "── Test 16: Noise disabled globally ──"
jq '.settings.spontaneity.noise.enabled = false | .settings.spontaneity.echo.enabled = false' "$TMP_CONFIG" > "$TMP_CONFIG.tmp" && mv "$TMP_CONFIG.tmp" "$TMP_CONFIG"
reset_state 100 0
result=$(try_noise_upgrade "expression" "low" "$TMP_STATE" "$TMP_CONFIG" 2>/dev/null)
assert_eq "disabled noise: low stays low" "low" "$result"
# Restore
jq '.settings.spontaneity.noise.enabled = true | .settings.spontaneity.echo.enabled = true' "$TMP_CONFIG" > "$TMP_CONFIG.tmp" && mv "$TMP_CONFIG.tmp" "$TMP_CONFIG"

echo "── Test 17: record_spontaneous updates state ──"
reset_state 24 48
record_spontaneous "expression" "$TMP_STATE"
last_spont=$(jq -r '.expression.last_spontaneous_at' "$TMP_STATE")
# Should be recent (within last minute)
last_spont_epoch=$(date -d "$last_spont" +%s)
now_epoch=$(date +%s)
diff=$((now_epoch - last_spont_epoch))
if [[ $diff -lt 60 ]]; then
    assert_eq "record_spontaneous sets recent timestamp" "true" "true"
else
    assert_eq "record_spontaneous sets recent timestamp" "true" "false (${diff}s ago)"
fi

echo "── Test 18: Boredom + echo combined under cap ──"
reset_state 48 6  # boredom=6%, echo=6% → total=12% = cap
boredom=$(calc_boredom_noise "expression" "$TMP_STATE" "$TMP_CONFIG")
echo_val=$(calc_echo_boost "expression" "$TMP_STATE" "$TMP_CONFIG")
total=$(echo "scale=4; $boredom + $echo_val" | bc -l)
noise_cap=0.12
if (( $(echo "$total > $noise_cap" | bc -l) )); then
    total="$noise_cap"
fi
assert_float_near "boredom(48h)+echo(6h) total ≤ cap" "0.1200" "$total" 0.005

echo "── Test 19: Boredom + echo combined over cap ──"
reset_state 100 0  # boredom=9%, echo=8% → total=17%, capped at 12%
boredom=$(calc_boredom_noise "expression" "$TMP_STATE" "$TMP_CONFIG")
echo_val=$(calc_echo_boost "expression" "$TMP_STATE" "$TMP_CONFIG")
total=$(echo "scale=4; $boredom + $echo_val" | bc -l)
if (( $(echo "$total > $noise_cap" | bc -l) )); then
    total="$noise_cap"
fi
assert_float_near "boredom(100h)+echo(0h) capped at 0.12" "0.1200" "$total" 0.001

echo ""
echo "═══════════════════════════════════"
echo "Results: $pass passed, $errors failed"
echo "═══════════════════════════════════"

exit $errors

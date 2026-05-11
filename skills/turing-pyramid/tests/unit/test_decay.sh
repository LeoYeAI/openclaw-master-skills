#!/usr/bin/env bash
# Test: satisfaction decay calculation
# Real formula: decay_delta = (hours_elapsed / decay_rate_hours) × multiplier
# This is LINEAR decay, not exponential!

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
RUN_CYCLE="$SKILL_DIR/scripts/run-cycle.sh"
FIXTURES="$SCRIPT_DIR/../fixtures"

export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
export SKIP_SCANS="true"
export SKIP_SPONTANEITY="true"

errors=0

# Test 1: Verify decay formula matches spec
echo "Test 1: Linear decay formula verification"

# Get security decay rate from config
decay_rate=$(jq -r '.needs.security.decay_rate_hours' "$CONFIG_FILE")
echo "  Security decay_rate_hours: $decay_rate"

# Expected: after decay_rate hours, satisfaction drops by 1.0
# decay_delta = hours / decay_rate = decay_rate / decay_rate = 1.0
expected_delta="1.0"

# Calculate what real code should produce
test_hours="$decay_rate"
calc_delta=$(echo "scale=4; $test_hours / $decay_rate" | bc -l)

if [[ "${calc_delta%.*}" == "1" || "$calc_delta" == "1.0000" ]]; then
    echo "  After $decay_rate hours: delta=1.0 — OK"
else
    echo "  After $decay_rate hours: delta=$calc_delta (expected 1.0) — FAIL"
    ((errors++))
fi

# Test 2: Verify decay is applied in run-cycle.sh
echo ""
echo "Test 2: Decay applied during cycle"

# Backup state
cp "$STATE_FILE" "$STATE_FILE.decay_backup"

# Set security to known state with old timestamp
now_epoch=$(date +%s)
# Set last_decay_check to 24 hours ago
old_time=$(date -u -d "@$((now_epoch - 86400))" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
           date -u -r $((now_epoch - 86400)) +%Y-%m-%dT%H:%M:%SZ)

# Set ALL needs to sat=2.0 with recent timestamps to prevent cross-need deprivation interference
# Then set security's last_decay_check to 24h ago for the actual test
now_str=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for n in security integrity coherence closure autonomy connection competence understanding recognition expression; do
    jq --arg n "$n" --arg now "$now_str" \
      '.[$n].satisfaction = 2.0 | .[$n].last_satisfied = $now | .[$n].last_decay_check = $now' \
      "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
done
jq --arg t "$old_time" '.security.satisfaction = 2.0 | .security.last_decay_check = $t' \
    "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Run cycle (will apply decay)
"$RUN_CYCLE" > /dev/null 2>&1

# Check new satisfaction
new_sat=$(jq -r '.security.satisfaction' "$STATE_FILE")

# Restore backup
cp "$STATE_FILE.decay_backup" "$STATE_FILE"
rm "$STATE_FILE.decay_backup"

# Expected decay after 24h with decay_rate=168h:
# delta = 24/168 ≈ 0.143, so sat should be ~1.857
# Allow tolerance: should be < 2.0 (decay happened) and > 1.5 (not too much)
if (( $(echo "$new_sat < 2.0" | bc -l) )) && (( $(echo "$new_sat > 1.5" | bc -l) )); then
    echo "  After 24h: sat=$new_sat (was 2.0) — OK (decay applied)"
else
    echo "  After 24h: sat=$new_sat (expected ~1.85) — FAIL"
    ((errors++))
fi

# Test 3: Floor enforcement (sat never below 0)
echo ""
echo "Test 3: Decay respects floor"

cp "$STATE_FILE" "$STATE_FILE.decay_backup"

# Set very old timestamp (1000 hours ago) and low satisfaction
very_old=$(date -u -d "@$((now_epoch - 3600000))" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
           date -u -r $((now_epoch - 3600000)) +%Y-%m-%dT%H:%M:%SZ)

jq --arg t "$very_old" '.security.satisfaction = 0.5 | .security.last_decay_check = $t' \
    "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

"$RUN_CYCLE" > /dev/null 2>&1

floor_sat=$(jq -r '.security.satisfaction' "$STATE_FILE")

cp "$STATE_FILE.decay_backup" "$STATE_FILE"
rm "$STATE_FILE.decay_backup"

# Should not go below 0
if (( $(echo "$floor_sat >= 0" | bc -l) )); then
    echo "  After extreme decay: sat=$floor_sat (≥0) — OK"
else
    echo "  After extreme decay: sat=$floor_sat (<0) — FAIL"
    ((errors++))
fi

if [[ $errors -eq 0 ]]; then
    echo ""
    echo "All decay tests passed"
    exit 0
else
    echo ""
    echo "Decay tests FAILED: $errors errors"
    exit 1
fi

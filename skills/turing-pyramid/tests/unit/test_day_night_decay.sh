#!/bin/bash
# test_day_night_decay.sh — Verify day/night decay multiplier logic

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
MULTIPLIER_SCRIPT="$SKILL_DIR/scripts/get-decay-multiplier.sh"
CONFIG_FILE="$SKILL_DIR/assets/decay-config.json"

PASS=true

echo "Testing day/night decay multiplier..."

# Check script exists
if [[ ! -x "$MULTIPLIER_SCRIPT" ]]; then
    echo "  ❌ get-decay-multiplier.sh not found or not executable"
    exit 1
fi

# Check config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "  ❌ decay-config.json not found"
    exit 1
fi

# Get config values
DAY_MULT=$(jq -r '.day_decay_multiplier // 1.0' "$CONFIG_FILE")
NIGHT_MULT=$(jq -r '.night_decay_multiplier // 0.5' "$CONFIG_FILE")
DAY_START=$(jq -r '.day_start // "06:01"' "$CONFIG_FILE")
DAY_END=$(jq -r '.day_end // "22:00"' "$CONFIG_FILE")

echo "  Config: day=$DAY_MULT, night=$NIGHT_MULT, range=$DAY_START-$DAY_END"

# Get current multiplier
CURRENT=$("$MULTIPLIER_SCRIPT")

# Verify it returns a valid number
if [[ "$CURRENT" =~ ^[0-9.]+$ ]]; then
    echo "  Current multiplier: $CURRENT — OK (valid number)"
else
    echo "  Current multiplier: $CURRENT — FAIL (not a number)"
    PASS=false
fi

# Verify it matches expected day or night value
if [[ "$CURRENT" == "$DAY_MULT" || "$CURRENT" == "$NIGHT_MULT" ]]; then
    echo "  Multiplier matches config — OK"
else
    echo "  Multiplier $CURRENT doesn't match day($DAY_MULT) or night($NIGHT_MULT) — FAIL"
    PASS=false
fi

# Verify multiplier is applied in decay calculation (conceptual check)
echo "  Day multiplier: $DAY_MULT (faster decay)"
echo "  Night multiplier: $NIGHT_MULT (slower decay)"

if (( $(echo "$NIGHT_MULT < $DAY_MULT" | bc -l) )); then
    echo "  Night < Day — OK (night is slower)"
else
    echo "  Night >= Day — WARNING (night should be slower)"
fi

if $PASS; then
    echo "✅ Day/night decay test PASSED"
    exit 0
else
    echo "❌ Day/night decay test FAILED"
    exit 1
fi

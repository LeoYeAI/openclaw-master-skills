#!/bin/bash
# test_action_probability.sh — Verify 6-level action probability config exists and is valid

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"

PASS=true

echo "Testing 6-level action probability config..."

# Check config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "  ❌ needs-config.json not found"
    exit 1
fi

# Verify action_probability section exists
if ! jq -e '.action_probability' "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "  ❌ action_probability section not found in config"
    exit 1
fi

# Test each sat level has correct value
test_probability() {
    local sat=$1
    local expected=$2
    
    local actual=$(jq -r ".action_probability.\"sat_$sat\" // -1" "$CONFIG_FILE")
    
    if [[ "$actual" == "$expected" ]]; then
        echo "  sat_$sat: $actual% — OK"
    else
        echo "  sat_$sat: $actual% (expected $expected%) — FAIL"
        PASS=false
    fi
}

test_probability "0.5" 100
test_probability "1.0" 90
test_probability "1.5" 75
test_probability "2.0" 50
test_probability "2.5" 25
test_probability "3.0" 0

# Verify roll_action logic exists in run-cycle.sh
if grep -q "6-level action probability" "$SKILL_DIR/scripts/run-cycle.sh"; then
    echo "  roll_action uses 6-level system — OK"
else
    echo "  roll_action may not use 6-level system — WARNING"
fi

if $PASS; then
    echo "✅ Action probability config test PASSED"
    exit 0
else
    echo "❌ Action probability config test FAILED"
    exit 1
fi

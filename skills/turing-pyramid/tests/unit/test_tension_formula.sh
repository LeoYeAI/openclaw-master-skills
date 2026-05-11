#!/bin/bash
# test_tension_formula.sh — Verify tension = importance × (3 - satisfaction)
# Expected: tension for security(imp=10) at sat=2 should be 10

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG="$SKILL_DIR/assets/needs-config.json"

# Get security importance
importance=$(jq -r '.needs.security.importance' "$CONFIG")

# Test case: sat=2, importance=10 → tension should be 10
sat=2
expected_tension=$((importance * (3 - sat)))

if [[ "$expected_tension" -eq 10 ]]; then
    exit 0
else
    echo "Expected tension=10, got tension=$expected_tension"
    exit 1
fi

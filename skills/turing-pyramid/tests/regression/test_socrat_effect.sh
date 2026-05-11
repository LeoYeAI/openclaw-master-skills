#!/bin/bash
# test_socrat_effect.sh — Regression test for connection→understanding floor clamping
# Bug: connection→understanding -0.05 showed 0.50→0.50 (no change at floor)
# Expected behavior: Negative cross-impact should be blocked when target is at floor
# This is CORRECT behavior — we're testing it stays correct

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
MARK_SCRIPT="$SKILL_DIR/scripts/mark-satisfied.sh"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
FIXTURES="$SCRIPT_DIR/../fixtures"

# Backup current state
cp "$STATE_FILE" "$STATE_FILE.test_backup"

# Set understanding to floor (0.5)
cp "$FIXTURES/needs-state-healthy.json" "$STATE_FILE"
jq '.understanding.satisfaction = 0.5' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# Get initial understanding sat
before=$(jq -r '.understanding.satisfaction' "$STATE_FILE")

# Satisfy connection (should trigger understanding -0.05)
"$MARK_SCRIPT" connection 1.0 > /dev/null 2>&1

# Get after
after=$(jq -r '.understanding.satisfaction' "$STATE_FILE")

# Restore backup
cp "$STATE_FILE.test_backup" "$STATE_FILE"
rm "$STATE_FILE.test_backup"

# Verify: understanding should still be >= 0.5 (floor protected)
if (( $(echo "$after >= 0.5" | bc -l) )); then
    # Also verify it didn't go below before (floor clamping worked)
    if (( $(echo "$after >= $before - 0.06" | bc -l) )); then
        exit 0
    else
        echo "Floor clamping failed: $before → $after (dropped more than expected)"
        exit 1
    fi
else
    echo "Floor violation: understanding=$after (expected >= 0.5)"
    exit 1
fi

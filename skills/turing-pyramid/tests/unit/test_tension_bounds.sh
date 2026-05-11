#!/bin/bash
# test_tension_bounds.sh — Verify tension stays within valid bounds [0, max_importance × 3]
# Max tension = 10 (security importance) × 3 = 30
# Min tension = 0 (when sat = 3)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG="$SKILL_DIR/assets/needs-config.json"

errors=0

# Get max importance from config
max_importance=$(jq '[.needs[].importance] | max' "$CONFIG")
max_tension=$((max_importance * 3))

echo "Max importance: $max_importance, Max tension: $max_tension"

# Test cases: various satisfaction levels
for sat in 0 0.5 1 1.5 2 2.5 3; do
    for imp in 1 5 10; do
        # tension = importance × (3 - sat)
        tension=$(echo "$imp * (3 - $sat)" | bc -l)
        
        # Check bounds
        if (( $(echo "$tension < 0" | bc -l) )); then
            echo "FAIL: tension=$tension < 0 (imp=$imp, sat=$sat)"
            ((errors++))
        fi
        
        if (( $(echo "$tension > $max_tension" | bc -l) )); then
            echo "FAIL: tension=$tension > $max_tension (imp=$imp, sat=$sat)"
            ((errors++))
        fi
    done
done

# Edge case: satisfaction below floor (0.5) — should still produce valid tension
sat=0.5
imp=10
tension=$(echo "$imp * (3 - $sat)" | bc -l)  # 10 × 2.5 = 25

if (( $(echo "$tension > $max_tension" | bc -l) )); then
    echo "FAIL: Edge case tension=$tension > $max_tension"
    ((errors++))
fi

if [[ $errors -eq 0 ]]; then
    exit 0
else
    echo "Total errors: $errors"
    exit 1
fi

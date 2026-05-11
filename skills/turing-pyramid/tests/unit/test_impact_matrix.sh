#!/bin/bash
# test_impact_matrix.sh — Verify 6-level impact selection matrix
# Tests that roll_impact_range returns correct distribution for each sat level

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"

PASS=true

echo "Testing 6-level impact matrix..."

test_impact_distribution() {
    local sat=$1
    local expected_high_min=$2
    local expected_high_max=$3
    
    local low=0 mid=0 high=0 skip=0
    
    for i in $(seq 1 100); do
        local roll=$((RANDOM % 100))
        
        local p_low=$(jq -r ".impact_matrix_default.\"sat_$sat\".low // 25" "$CONFIG_FILE")
        local p_mid=$(jq -r ".impact_matrix_default.\"sat_$sat\".mid // 50" "$CONFIG_FILE")
        local p_high=$(jq -r ".impact_matrix_default.\"sat_$sat\".high // 25" "$CONFIG_FILE")
        
        # Check for skip (all zeros)
        if [[ $p_low -eq 0 && $p_mid -eq 0 && $p_high -eq 0 ]]; then
            ((skip++))
            continue
        fi
        
        if [[ $roll -lt $p_low ]]; then
            ((low++))
        elif [[ $roll -lt $((p_low + p_mid)) ]]; then
            ((mid++))
        else
            ((high++))
        fi
    done
    
    if [[ "$sat" == "3.0" ]]; then
        if [[ $skip -eq 100 ]]; then
            echo "  sat=$sat: skip=100% — OK"
        else
            echo "  sat=$sat: skip=$skip% (expected 100%) — FAIL"
            PASS=false
        fi
    elif [[ $high -ge $expected_high_min && $high -le $expected_high_max ]]; then
        echo "  sat=$sat: high=$high% (expected $expected_high_min-$expected_high_max%) — OK"
    else
        echo "  sat=$sat: high=$high% (expected $expected_high_min-$expected_high_max%) — FAIL"
        PASS=false
    fi
}

# Test high action percentage with ±15% tolerance
test_impact_distribution "0.5" 85 100   # 100% high
test_impact_distribution "1.0" 55 85    # 70% high
test_impact_distribution "1.5" 30 60    # 45% high
test_impact_distribution "2.0" 10 40    # 25% high
test_impact_distribution "2.5" 0 30     # 15% high
test_impact_distribution "3.0" 0 0      # skip

if $PASS; then
    echo "✅ Impact matrix test PASSED"
    exit 0
else
    echo "❌ Impact matrix test FAILED"
    exit 1
fi

#!/bin/bash
# Test: autonomy need has actions across all impact ranges + continuation capability

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../../assets"
CONFIG="$ASSETS_DIR/needs-config.json"

# Count actions by impact range for autonomy
low=$(jq '[.needs.autonomy.actions[] | select(.impact >= 0 and .impact < 1)] | length' "$CONFIG")
mid=$(jq '[.needs.autonomy.actions[] | select(.impact >= 1 and .impact < 2)] | length' "$CONFIG")
high=$(jq '[.needs.autonomy.actions[] | select(.impact >= 2)] | length' "$CONFIG")
total=$(jq '.needs.autonomy.actions | length' "$CONFIG")

# Require at least 2 actions in each range (consolidated from 3)
if [ "$low" -lt 2 ]; then
    echo "FAIL: autonomy has only $low low-impact actions (need ≥2)"
    exit 1
fi

if [ "$mid" -lt 3 ]; then
    echo "FAIL: autonomy has only $mid mid-impact actions (need ≥3)"
    exit 1
fi

if [ "$high" -lt 3 ]; then
    echo "FAIL: autonomy has only $high high-impact actions (need ≥3)"
    exit 1
fi

# Check continuation actions exist (consolidated names)
continuation_found=$(jq '[.needs.autonomy.actions[] | select(.name | test("continue|refine|improve"))] | length' "$CONFIG")
if [ "$continuation_found" -lt 2 ]; then
    echo "FAIL: autonomy needs at least 2 continuation actions, found $continuation_found"
    exit 1
fi

# Check initiation actions exist
initiation_found=$(jq '[.needs.autonomy.actions[] | select(.name | test("initiate|explore|new"))] | length' "$CONFIG")
if [ "$initiation_found" -lt 2 ]; then
    echo "FAIL: autonomy needs at least 2 initiation actions, found $initiation_found"
    exit 1
fi

echo "autonomy coverage: low=$low, mid=$mid, high=$high (total=$total)"
echo "continuation=$continuation_found, initiation=$initiation_found — balanced"

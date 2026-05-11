#!/bin/bash
# Test: all needs have ≥3 high-impact actions (crisis mode guarantee)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../../assets"
CONFIG="$ASSETS_DIR/needs-config.json"

# Get all need names
needs=$(jq -r '.needs | keys[]' "$CONFIG")

failed=0
for need in $needs; do
    high_count=$(jq "[.needs.$need.actions[] | select(.impact >= 2.0)] | length" "$CONFIG")
    if [ "$high_count" -lt 3 ]; then
        echo "FAIL: $need has only $high_count high-impact actions (need ≥3 for crisis mode)"
        failed=1
    else
        echo "OK: $need has $high_count high-impact actions"
    fi
done

if [ "$failed" -eq 1 ]; then
    exit 1
fi
echo "All needs have ≥3 high-impact actions — crisis mode guaranteed"

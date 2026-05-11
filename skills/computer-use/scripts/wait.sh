#!/bin/bash
# wait.sh - Wait for specified duration then screenshot
# Usage: wait.sh seconds

export DISPLAY=:99

DURATION="$1"

if [ -z "$DURATION" ]; then
    echo "ERROR: Usage: wait.sh seconds" >&2
    exit 1
fi

# Validate duration is reasonable
if (( $(echo "$DURATION > 100" | bc -l) )); then
    echo "ERROR: Duration too long (max 100 seconds)" >&2
    exit 1
fi

sleep "$DURATION"
echo "Waited $DURATION seconds"

# Screenshot after waiting
exec "$(dirname "$0")/screenshot.sh"

#!/bin/bash
# hold_key.sh - Hold a key for specified duration
# Usage: hold_key.sh "key" duration_seconds

export DISPLAY=:99

KEY="$1"
DURATION="$2"

if [ -z "$KEY" ] || [ -z "$DURATION" ]; then
    echo "ERROR: Usage: hold_key.sh \"key\" duration_seconds" >&2
    exit 1
fi

# Validate duration is reasonable
if (( $(echo "$DURATION > 100" | bc -l) )); then
    echo "ERROR: Duration too long (max 100 seconds)" >&2
    exit 1
fi

xdotool keydown "$KEY"
sleep "$DURATION"
xdotool keyup "$KEY"

echo "Held $KEY for $DURATION seconds"

# Auto-screenshot after action
sleep 2
exec "$(dirname "$0")/screenshot.sh"

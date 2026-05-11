#!/bin/bash
# type_text.sh - Type text with realistic delays
# Usage: type_text.sh "text to type"
# Types in 50 character chunks with 12ms delay between keystrokes

export DISPLAY=:99

TEXT="$1"

if [ -z "$TEXT" ]; then
    echo "ERROR: Usage: type_text.sh \"text to type\"" >&2
    exit 1
fi

# Type in chunks of 50 characters
CHUNK_SIZE=50
LENGTH=${#TEXT}
OFFSET=0

while [ $OFFSET -lt $LENGTH ]; do
    CHUNK="${TEXT:$OFFSET:$CHUNK_SIZE}"
    xdotool type --delay 12 -- "$CHUNK"
    OFFSET=$((OFFSET + CHUNK_SIZE))
done

echo "Typed ${#TEXT} characters"

# Auto-screenshot after action
sleep 2
exec "$(dirname "$0")/screenshot.sh"

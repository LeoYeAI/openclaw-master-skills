#!/bin/bash
# key.sh - Press key or key combination
# Usage: key.sh "Return" or key.sh "ctrl+c" or key.sh "alt+F4"

export DISPLAY=:99

KEY="$1"

if [ -z "$KEY" ]; then
    echo "ERROR: Usage: key.sh \"key_combo\"" >&2
    exit 1
fi

xdotool key -- "$KEY"
echo "Pressed key: $KEY"

# Auto-screenshot after action
sleep 2
exec "$(dirname "$0")/screenshot.sh"

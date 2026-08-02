#!/bin/bash
# click.sh - Click at coordinates
# Usage: click.sh X Y [left|right|middle|double|triple]

export DISPLAY=:99

X=$1
Y=$2
BUTTON=${3:-left}

if [ -z "$X" ] || [ -z "$Y" ]; then
    echo "ERROR: Usage: click.sh X Y [left|right|middle|double|triple]" >&2
    exit 1
fi

# Move to position first
xdotool mousemove --sync "$X" "$Y"

# Click based on button type
case "$BUTTON" in
    left)
        xdotool click 1
        ;;
    right)
        xdotool click 3
        ;;
    middle)
        xdotool click 2
        ;;
    double)
        xdotool click --repeat 2 --delay 100 1
        ;;
    triple)
        xdotool click --repeat 3 --delay 100 1
        ;;
    *)
        echo "ERROR: Unknown button type: $BUTTON" >&2
        exit 1
        ;;
esac

echo "Clicked $BUTTON at $X,$Y"

# Auto-screenshot after action (2 sec delay)
sleep 2
exec "$(dirname "$0")/screenshot.sh"

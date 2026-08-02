#!/bin/bash
# scroll.sh - Scroll in a direction
# Usage: scroll.sh direction amount [x y]
# direction: up, down, left, right
# amount: number of scroll units

export DISPLAY=:99

DIRECTION="$1"
AMOUNT="${2:-3}"
X="$3"
Y="$4"

if [ -z "$DIRECTION" ]; then
    echo "ERROR: Usage: scroll.sh direction [amount] [x y]" >&2
    exit 1
fi

# Move to position if specified
if [ -n "$X" ] && [ -n "$Y" ]; then
    xdotool mousemove --sync "$X" "$Y"
fi

# Map direction to button
case "$DIRECTION" in
    up)
        BUTTON=4
        ;;
    down)
        BUTTON=5
        ;;
    left)
        BUTTON=6
        ;;
    right)
        BUTTON=7
        ;;
    *)
        echo "ERROR: Unknown direction: $DIRECTION (use up/down/left/right)" >&2
        exit 1
        ;;
esac

xdotool click --repeat "$AMOUNT" "$BUTTON"
echo "Scrolled $DIRECTION $AMOUNT times"

# Auto-screenshot after action
sleep 2
exec "$(dirname "$0")/screenshot.sh"

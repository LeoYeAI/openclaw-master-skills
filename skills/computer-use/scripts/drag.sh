#!/bin/bash
# drag.sh - Drag from start to end coordinates
# Usage: drag.sh X1 Y1 X2 Y2

export DISPLAY=:99

X1=$1
Y1=$2
X2=$3
Y2=$4

if [ -z "$X1" ] || [ -z "$Y1" ] || [ -z "$X2" ] || [ -z "$Y2" ]; then
    echo "ERROR: Usage: drag.sh X1 Y1 X2 Y2" >&2
    exit 1
fi

xdotool mousemove --sync "$X1" "$Y1" mousedown 1 mousemove --sync "$X2" "$Y2" mouseup 1

echo "Dragged from $X1,$Y1 to $X2,$Y2"

# Auto-screenshot after action
sleep 2
exec "$(dirname "$0")/screenshot.sh"

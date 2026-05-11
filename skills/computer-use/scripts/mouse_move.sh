#!/bin/bash
# mouse_move.sh - Move mouse to coordinates
# Usage: mouse_move.sh X Y

export DISPLAY=:99

X=$1
Y=$2

if [ -z "$X" ] || [ -z "$Y" ]; then
    echo "ERROR: Usage: mouse_move.sh X Y" >&2
    exit 1
fi

xdotool mousemove --sync "$X" "$Y"
echo "Moved mouse to $X,$Y"

#!/bin/bash
# cursor_position.sh - Get current mouse coordinates

export DISPLAY=:99

# Get mouse location
eval $(xdotool getmouselocation --shell 2>/dev/null)

echo "X=$X,Y=$Y"

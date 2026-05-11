#!/bin/bash
# mouse_up.sh - Release left mouse button

export DISPLAY=:99

xdotool mouseup 1
echo "Mouse button released"

# Auto-screenshot after action
sleep 2
exec "$(dirname "$0")/screenshot.sh"

#!/bin/bash
# mouse_down.sh - Press left mouse button (no release)

export DISPLAY=:99

xdotool mousedown 1
echo "Mouse button pressed"

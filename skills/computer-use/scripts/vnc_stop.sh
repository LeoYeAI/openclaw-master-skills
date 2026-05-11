#!/bin/bash
# Stop VNC services

echo "Stopping VNC services..."

pkill -f x11vnc 2>/dev/null
pkill -f websockify 2>/dev/null

sleep 1

if ! pgrep -f x11vnc > /dev/null && ! pgrep -f websockify > /dev/null; then
    echo "✓ VNC services stopped"
else
    echo "✗ Some processes may still be running"
    ps aux | grep -E "(x11vnc|websockify)" | grep -v grep
fi

#!/bin/bash
# Start VNC services for live desktop viewing

DISPLAY_NUM="${DISPLAY_NUM:-:99}"

# Kill existing instances
pkill -f "x11vnc.*display $DISPLAY_NUM" 2>/dev/null
pkill -f "websockify.*6080" 2>/dev/null
sleep 1

# Start x11vnc (VNC server)
echo "Starting x11vnc on $DISPLAY_NUM..."
x11vnc -display "$DISPLAY_NUM" -forever -shared -nopw -listen localhost &
sleep 2

# Start websockify (noVNC web bridge)
echo "Starting noVNC on port 6080..."
websockify --web=/usr/share/novnc 6080 localhost:5900 &
sleep 1

# Verify
if pgrep -f x11vnc > /dev/null && pgrep -f websockify > /dev/null; then
    echo ""
    echo "✓ VNC services started"
    echo ""
    echo "To connect:"
    echo "  1. SSH tunnel: ssh -L 6080:localhost:6080 your-server"
    echo "  2. Open: http://localhost:6080/vnc.html?autoconnect=true"
    echo ""
else
    echo "✗ Failed to start VNC services"
    exit 1
fi

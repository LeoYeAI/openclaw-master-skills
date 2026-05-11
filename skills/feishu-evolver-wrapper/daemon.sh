#!/bin/bash
# daemon.sh - Ensures the evolver loop is running

# Use absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$SCRIPT_DIR/index.js"
LOG_DIR="$SCRIPT_DIR/../../logs"
PID_FILE="$SCRIPT_DIR/../../memory/evolver_loop.pid"

mkdir -p "$LOG_DIR"

# Check if process is running via PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        # Check if it's actually the evolver wrapper
        CMDLINE=$(ps -p "$PID" -o args=)
        if [[ "$CMDLINE" == *"feishu-evolver-wrapper/index.js"* ]]; then
            # Still running, exit silently
            exit 0
        fi
    fi
fi

# Not running or stale PID file. Look for process by name just in case.
# Exclude grep, exclude self
PIDS=$(pgrep -f "node .*feishu-evolver-wrapper/index.js --loop")
if [ -n "$PIDS" ]; then
    # Found running process, update PID file
    echo "$PIDS" | head -n1 > "$PID_FILE"
    exit 0
fi

# Start it
echo "[$(date)] Starting evolver loop..." >> "$LOG_DIR/evolver_daemon.log"
# Use setsid to detach completely
setsid nohup node "$WRAPPER_SCRIPT" --loop >> "$LOG_DIR/evolver_loop.log" 2>&1 &
NEW_PID=$!
# Wait briefly to let it start and stabilize
sleep 1
# Check if it stayed running
if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "$NEW_PID" > "$PID_FILE"
    echo "[$(date)] Started with PID $NEW_PID" >> "$LOG_DIR/evolver_daemon.log"
else
    echo "[$(date)] Start failed immediately." >> "$LOG_DIR/evolver_daemon.log"
fi

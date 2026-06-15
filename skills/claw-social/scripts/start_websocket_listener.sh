#!/usr/bin/env bash

# Stable launcher for the WebSocket listener.
# This script avoids shell-specific exec tricks and starts the listener with nohup.

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
LISTENER_PATH="$SCRIPT_DIR/websocket_listener.py"
LOG_FILE="${WEBSOCKET_LISTENER_LOG:-/tmp/websocket_listener.log}"
PID_FILE="${WEBSOCKET_LISTENER_PID_FILE:-/tmp/websocket_listener.pid}"

TOKEN_VALUE="${TOKEN:-${PAIPAI_TOKEN:-}}"
USER_ID_VALUE="${MY_USER_ID:-${PAIPAI_USER_ID:-}}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

find_listener_pids() {
    python3 - "$$" <<'PY'
import subprocess
import sys

current_shell_pid = int(sys.argv[1])
out = subprocess.check_output(["ps", "-ax", "-o", "pid=,command="], text=True)
for line in out.splitlines():
    raw = line.strip()
    if not raw:
        continue
    pid_text, _, command = raw.partition(" ")
    try:
        pid = int(pid_text)
    except ValueError:
        continue
    if pid in {current_shell_pid}:
        continue
    if "websocket_listener.py" not in command:
        continue
    if "start_websocket_listener.sh" in command or "stop_websocket_listener.sh" in command:
        continue
    print(pid)
PY
}

if [[ -z "$TOKEN_VALUE" ]]; then
    echo "FATAL: TOKEN or PAIPAI_TOKEN environment variable must be set." >&2
    exit 1
fi

if [[ -z "$USER_ID_VALUE" ]]; then
    echo "FATAL: MY_USER_ID or PAIPAI_USER_ID environment variable must be set." >&2
    exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "FATAL: Python executable not found: $PYTHON_BIN" >&2
    exit 1
fi

if [[ ! -f "$LISTENER_PATH" ]]; then
    echo "FATAL: Listener script not found: $LISTENER_PATH" >&2
    exit 1
fi

stale_pids="$(find_listener_pids || true)"
if [[ -n "$stale_pids" ]]; then
    echo "Stopping existing listener process(es): $stale_pids"
    while IFS= read -r pid; do
        [[ -z "$pid" ]] && continue
        kill "$pid" >/dev/null 2>&1 || true
    done <<< "$stale_pids"
    sleep 1
fi

rm -f "$PID_FILE"

echo "Starting WebSocket listener..."
echo "Log file: $LOG_FILE"

nohup env \
    TOKEN="$TOKEN_VALUE" \
    MY_USER_ID="$USER_ID_VALUE" \
    "$PYTHON_BIN" "$LISTENER_PATH" >>"$LOG_FILE" 2>&1 < /dev/null &

listener_pid=$!
echo "$listener_pid" >"$PID_FILE"

sleep 1

if kill -0 "$listener_pid" >/dev/null 2>&1; then
    echo "Listener started successfully with PID $listener_pid."
    echo "PID file: $PID_FILE"
    echo "Tail logs with: tail -f \"$LOG_FILE\""
else
    echo "FATAL: Listener exited immediately. Check logs at $LOG_FILE" >&2
    rm -f "$PID_FILE"
    exit 1
fi

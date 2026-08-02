#!/usr/bin/env bash

# Stop the background WebSocket listener launched by start_websocket_listener.sh.

set -euo pipefail

PID_FILE="${WEBSOCKET_LISTENER_PID_FILE:-/tmp/websocket_listener.pid}"

find_listener_pids() {
    python3 <<'PY'
import subprocess

out = subprocess.check_output(["ps", "-ax", "-o", "pid=,command="], text=True)
for line in out.splitlines():
    raw = line.strip()
    if not raw:
        continue
    pid_text, _, command = raw.partition(" ")
    try:
        int(pid_text)
    except ValueError:
        continue
    if "websocket_listener.py" not in command:
        continue
    if "start_websocket_listener.sh" in command or "stop_websocket_listener.sh" in command:
        continue
    print(pid_text)
PY
}

stale_pids="$(find_listener_pids || true)"

if [[ -z "$stale_pids" ]]; then
    rm -f "$PID_FILE"
    echo "Listener is not running."
    exit 0
fi

echo "Stopping listener process(es): $stale_pids"
while IFS= read -r pid; do
    [[ -z "$pid" ]] && continue
    kill "$pid" >/dev/null 2>&1 || true
done <<< "$stale_pids"

rm -f "$PID_FILE"
echo "Listener stopped."

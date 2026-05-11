#!/usr/bin/env bash
# Serve a directory over HTTP, finding a free port automatically.
# Usage: serve.sh <directory>
#        serve.sh --stop

set -euo pipefail

PID_FILE="/tmp/build-game-server.pid"

if [[ "${1:-}" == "--stop" ]]; then
    if [[ -f "$PID_FILE" ]]; then
        kill "$(cat "$PID_FILE")" 2>/dev/null && echo "Server stopped." || echo "Server already stopped."
        rm -f "$PID_FILE"
    else
        echo "No server running."
    fi
    exit 0
fi

DIR="${1:-.}"
if [[ ! -d "$DIR" ]]; then
    echo "Error: '$DIR' is not a directory." >&2
    exit 1
fi

# Kill any previous server
if [[ -f "$PID_FILE" ]]; then
    kill "$(cat "$PID_FILE")" 2>/dev/null || true
    rm -f "$PID_FILE"
fi

# Find a free port between 8080-8099
PORT=""
for p in $(seq 8080 8099); do
    if python3 -c "import socket; s=socket.socket(); s.settimeout(0.1); s.bind(('127.0.0.1',$p)); s.close()" 2>/dev/null; then
        PORT=$p
        break
    fi
done

if [[ -z "$PORT" ]]; then
    echo "Error: No free port found in 8080-8099." >&2
    exit 1
fi

python3 -m http.server "$PORT" --directory "$DIR" --bind 127.0.0.1 >/dev/null 2>&1 &
echo $! > "$PID_FILE"

echo "http://localhost:$PORT"

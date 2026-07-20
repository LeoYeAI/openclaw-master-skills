#!/usr/bin/env bash
#
# Emotion daemon management script.
#
# Usage:
#   bash scripts/daemon.sh start [--config path/to/emoclaw.yaml]
#   bash scripts/daemon.sh stop
#   bash scripts/daemon.sh status
#   bash scripts/daemon.sh restart
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$(dirname "$SKILL_DIR")")"
VENV="$REPO_ROOT/emotion_model/.venv"
PIDFILE="/tmp/emotion-daemon.pid"

# Activate venv if it exists
activate_venv() {
    if [ -f "$VENV/bin/activate" ]; then
        source "$VENV/bin/activate"
    else
        echo "Warning: No venv found at $VENV"
        echo "The daemon will use the system Python."
    fi
}

do_start() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Emotion daemon is already running (PID $(cat "$PIDFILE"))"
        return 1
    fi

    activate_venv

    echo "Starting emotion daemon..."
    cd "$REPO_ROOT"

    PYTHONPATH="$REPO_ROOT" python -m emotion_model.daemon "$@" &
    local pid=$!
    echo "$pid" > "$PIDFILE"
    echo "Emotion daemon started (PID $pid)"
}

do_stop() {
    if [ ! -f "$PIDFILE" ]; then
        echo "No PID file found. Daemon may not be running."
        return 1
    fi

    local pid
    pid=$(cat "$PIDFILE")

    if kill -0 "$pid" 2>/dev/null; then
        echo "Stopping emotion daemon (PID $pid)..."
        kill "$pid"
        rm -f "$PIDFILE"
        echo "Daemon stopped."
    else
        echo "Daemon not running (stale PID file). Cleaning up."
        rm -f "$PIDFILE"
    fi
}

do_status() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Emotion daemon is running (PID $(cat "$PIDFILE"))"
    else
        echo "Emotion daemon is not running"
        [ -f "$PIDFILE" ] && rm -f "$PIDFILE"
    fi
}

case "${1:-}" in
    start)
        shift
        do_start "$@"
        ;;
    stop)
        do_stop
        ;;
    restart)
        shift
        do_stop 2>/dev/null || true
        sleep 1
        do_start "$@"
        ;;
    status)
        do_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status} [daemon args...]"
        exit 1
        ;;
esac

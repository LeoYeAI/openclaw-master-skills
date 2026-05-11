#!/usr/bin/env bash
# wait-for-auth.sh — Wait for the gh auth refresh background process to complete.
#
# Called after refresh-gh-scopes.sh returns a device code and the user has
# authorized it. Blocks until the gh process exits or times out.
#
# Usage: bash wait-for-auth.sh [--timeout <seconds>] [--pid <pid>]
# Output: JSON to stdout

set -euo pipefail

PID_FILE="${HOME}/.telnyx/gh_refresh.pid"
DEFAULT_TIMEOUT=900  # 15 minutes (matches device code TTL)

TIMEOUT="$DEFAULT_TIMEOUT"
PID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --timeout) TIMEOUT="$2"; shift 2 ;;
        --pid) PID="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Resolve PID from argument or file
if [ -z "$PID" ]; then
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
    else
        cat <<EOF
{
  "success": false,
  "message": "No gh auth refresh process found. Run refresh-gh-scopes.sh first."
}
EOF
        exit 1
    fi
fi

# Check if process is still running
if ! kill -0 "$PID" 2>/dev/null; then
    # Already exited — check if it succeeded by verifying scopes
    if gh auth status 2>&1 | grep -q "user"; then
        rm -f "$PID_FILE"
        cat <<EOF
{
  "success": true,
  "message": "Scopes refreshed successfully."
}
EOF
        exit 0
    else
        rm -f "$PID_FILE"
        cat <<EOF
{
  "success": false,
  "message": "gh auth refresh process exited but scopes were not updated."
}
EOF
        exit 1
    fi
fi

# Process is running — wait for it with timeout
START=$(date +%s)
while kill -0 "$PID" 2>/dev/null; do
    ELAPSED=$(( $(date +%s) - START ))
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        kill "$PID" 2>/dev/null || true
        rm -f "$PID_FILE"
        cat <<EOF
{
  "success": false,
  "message": "Timed out after ${TIMEOUT}s waiting for authorization. Device code may have expired."
}
EOF
        exit 1
    fi
    sleep 2
done

# Process exited — check result
wait "$PID" 2>/dev/null && EXIT_CODE=0 || EXIT_CODE=$?
rm -f "$PID_FILE"

if [ "$EXIT_CODE" -eq 0 ]; then
    cat <<EOF
{
  "success": true,
  "message": "Scopes refreshed successfully. Authorization complete."
}
EOF
    exit 0
else
    cat <<EOF
{
  "success": false,
  "message": "gh auth refresh failed (exit code ${EXIT_CODE}). The device code may have expired or authorization was denied."
}
EOF
    exit 1
fi

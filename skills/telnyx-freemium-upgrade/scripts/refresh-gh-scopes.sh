#!/usr/bin/env bash
# refresh-gh-scopes.sh — Refresh GitHub CLI scopes to include user and read:org.
# Returns the device code for the user to authorize manually or via cross-channel notification.
#
# Usage: bash refresh-gh-scopes.sh
# Output: JSON to stdout

set -euo pipefail

PID_FILE="${HOME}/.telnyx/gh_refresh.pid"

json_output() {
    local success="$1"
    local message="$2"
    local requires_browser="$3"
    local device_code="$4"
    local verification_uri="$5"
    local pid="${6:-null}"

    cat <<EOF
{
  "success": ${success},
  "message": ${message},
  "requires_browser": ${requires_browser},
  "device_code": ${device_code},
  "verification_uri": ${verification_uri},
  "pid": ${pid}
}
EOF
}

# Check if gh is installed
if ! command -v gh &>/dev/null; then
    json_output "false" '"GitHub CLI (gh) is not installed. Install: https://cli.github.com"' \
        "false" "null" "null"
    exit 0
fi

# Check if gh is authenticated
if ! gh auth status &>/dev/null 2>&1; then
    json_output "false" '"GitHub CLI is not authenticated. Run: gh auth login --web"' \
        "false" "null" "null"
    exit 0
fi

# Run gh auth refresh with browser suppressed to capture device code.
# gh auth refresh writes the device code to stderr and blocks until the
# user authorizes or the code expires (15 minutes).
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

# Start refresh in background with BROWSER=false to force device code flow
BROWSER=false gh auth refresh --scopes user,read:org 2>"$TMPFILE" &
REFRESH_PID=$!

# Wait briefly for gh to output the device code
sleep 3

# Check if the process already exited (success without needing browser)
if ! kill -0 "$REFRESH_PID" 2>/dev/null; then
    wait "$REFRESH_PID" && REFRESH_EXIT=0 || REFRESH_EXIT=$?
    if [ "$REFRESH_EXIT" -eq 0 ]; then
        json_output "true" '"Scopes refreshed successfully. No browser interaction needed."' \
            "false" "null" "null"
        exit 0
    else
        ERROR_MSG=$(cat "$TMPFILE" | tr '\n' ' ' | sed 's/"/\\"/g')
        json_output "false" "\"Scope refresh failed: ${ERROR_MSG}\"" \
            "false" "null" "null"
        exit 0
    fi
fi

# Process is still running — parse device code from stderr output
STDERR_OUTPUT=$(cat "$TMPFILE")

DEVICE_CODE=$(echo "$STDERR_OUTPUT" | grep -oE '[A-Z0-9]{4}-[A-Z0-9]{4}' | head -1 || echo "")
VERIFICATION_URI=$(echo "$STDERR_OUTPUT" | grep -oP 'https://github\.com/login/device' | head -1 || echo "https://github.com/login/device")

if [ -z "$DEVICE_CODE" ]; then
    # Could not parse device code — unexpected output
    ERROR_MSG=$(echo "$STDERR_OUTPUT" | tr '\n' ' ' | sed 's/"/\\"/g')
    kill "$REFRESH_PID" 2>/dev/null || true
    json_output "false" "\"Unexpected output from gh auth refresh: ${ERROR_MSG}\"" \
        "false" "null" "null"
    exit 0
fi

# Device code found — save PID so wait-for-auth.sh can track it.
mkdir -p "$(dirname "$PID_FILE")"
echo "$REFRESH_PID" > "$PID_FILE"

# Return device code + PID for the bot to track.
# The gh auth refresh process polls GitHub every 5s for up to 15 minutes.
# Use wait-for-auth.sh to block until auth completes or expires.
json_output "false" \
    "\"Scope refresh requires browser authorization. Enter the device code at the verification URL, then run wait-for-auth.sh to confirm.\"" \
    "true" "\"${DEVICE_CODE}\"" "\"${VERIFICATION_URI}\"" "$REFRESH_PID"

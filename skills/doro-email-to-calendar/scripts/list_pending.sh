#!/bin/bash
# List all pending invites that haven't been actioned
# Returns JSON array of pending events with their details
#
# Usage: list_pending.sh [options]
#   --summary           Output a human-readable summary instead of JSON
#   --update-reminded   Update last_reminded timestamp and increment reminder_count
#   --auto-dismiss      Auto-dismiss events that have been reminded 3+ times without response
#
# Features:
#   - Shows day-of-week for verification
#   - Tracks reminder_count and last_reminded
#   - Auto-dismisses after 3 ignored reminders
#   - Batched presentation format
#
# Logs to ~/.openclaw/workspace/memory/email-to-calendar/pending_invites.json

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"
PENDING_FILE="$HOME/.openclaw/workspace/memory/email-to-calendar/pending_invites.json"

# Check if file exists
if [ ! -f "$PENDING_FILE" ]; then
    # Check if --summary flag is present
    for arg in "$@"; do
        if [ "$arg" = "--summary" ]; then
            echo "No pending invites found."
            exit 0
        fi
    done
    echo "[]"
    exit 0
fi

# Delegate to Python implementation
python3 "$UTILS_DIR/pending_ops.py" "$@"

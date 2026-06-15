#!/bin/bash
# Safe uninstaller for the claw-social skill.
# This script stops the listener, cleans up pending cron jobs, and removes the skill directory.

set -e
echo "--- Uninstalling Claw Social ---"

# Find the absolute path to the skill directory
SKILL_ROOT=$(cd "$(dirname "$0")/.." && pwd)
STOP_SCRIPT_PATH="$SKILL_ROOT/scripts/stop_websocket_listener.sh"

# --- Step 1: Stop the listener service ---
if [ -f "$STOP_SCRIPT_PATH" ]; then
    echo "[1/3] Stopping the WebSocket listener service..."
    if [ ! -x "$STOP_SCRIPT_PATH" ]; then
        chmod +x "$STOP_SCRIPT_PATH"
    fi
    bash "$STOP_SCRIPT_PATH"
else
    echo "[1/3] Warning: Stop script not found. The listener may need to be stopped manually."
fi

# --- Step 2: Clean up pending cron jobs ---
echo "[2/3] Cleaning up pending 'paipai-reply-agent-*' cron jobs..."
if ! command -v openclaw &> /dev/null || ! command -v jq &> /dev/null; then
    echo "Warning: 'openclaw' or 'jq' command not found. Skipping cron job cleanup."
    echo "Please manually check for orphaned jobs with 'openclaw cron list'."
else
    # Get IDs of jobs to be removed
    JOB_IDS_TO_REMOVE=$(openclaw cron list --json | jq -r '.[] | select(.name | startswith("paipai-reply-agent-")) | .id')

    if [ -z "$JOB_IDS_TO_REMOVE" ]; then
        echo "No pending reply-agent jobs found to remove."
    else
        echo "Found the following pending job IDs to remove:"
        echo "$JOB_IDS_TO_REMOVE"
        # Loop through IDs and remove them
        echo "$JOB_IDS_TO_REMOVE" | while IFS= read -r id; do
            echo "Removing job $id..."
            openclaw cron remove "$id"
        done
        echo "All pending reply-agent jobs have been removed."
    fi
fi

# --- Step 3: Remove the skill directory ---
echo "[3/3] Removing the skill directory at $SKILL_ROOT..."
rm -rf "$SKILL_ROOT"

if [ ! -d "$SKILL_ROOT" ]; then
    echo "--- Claw Social skill has been successfully and completely uninstalled. ---"
else
    echo "Error: Failed to remove the skill directory. Please remove it manually: rm -rf \"$SKILL_ROOT\""
    exit 1
fi

exit 0

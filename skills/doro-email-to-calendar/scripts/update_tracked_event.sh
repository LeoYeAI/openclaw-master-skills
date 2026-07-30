#!/bin/bash
# Update a tracked event's metadata after a calendar update
# Usage: update_tracked_event.sh --event-id <id> [--summary <new_summary>] [--start <new_start>]
#
# Updates the tracked event's metadata to reflect calendar changes

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

# Parse arguments
EVENT_ID=""
NEW_SUMMARY=""
NEW_START=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --event-id)
            EVENT_ID="$2"
            shift 2
            ;;
        --summary)
            NEW_SUMMARY="$2"
            shift 2
            ;;
        --start)
            NEW_START="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [ -z "$EVENT_ID" ]; then
    echo "Error: --event-id is required" >&2
    exit 1
fi

# Delegate to Python implementation
python3 "$UTILS_DIR/event_tracking.py" update \
    --event-id "$EVENT_ID" \
    --summary "$NEW_SUMMARY" \
    --start "$NEW_START"

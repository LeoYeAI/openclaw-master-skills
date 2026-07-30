#!/bin/bash
# Delete a tracked event from the tracking file (after deleting from calendar)
# Usage: delete_tracked_event.sh --event-id <id>
#
# This removes the event from events.json tracking

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"
EVENTS_FILE="$HOME/.openclaw/workspace/memory/email-to-calendar/events.json"

# Parse arguments
EVENT_ID=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --event-id)
            EVENT_ID="$2"
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

if [ ! -f "$EVENTS_FILE" ]; then
    echo "Warning: No events file found" >&2
    exit 0
fi

# Delegate to Python implementation
python3 "$UTILS_DIR/event_tracking.py" delete --event-id "$EVENT_ID"

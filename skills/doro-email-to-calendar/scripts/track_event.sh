#!/bin/bash
# Track a created calendar event for future updates/deletions
# Usage: track_event.sh --event-id <id> --calendar-id <cal_id> --email-id <email_id> --summary <title> --start <datetime>
#
# This stores event metadata in events.json so we can:
# - Find existing events by email_id (for duplicate detection)
# - Update or delete events without searching the calendar
# - Track event history

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

# Parse arguments
EVENT_ID=""
CALENDAR_ID="primary"
EMAIL_ID=""
SUMMARY=""
START=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --event-id)
            EVENT_ID="$2"
            shift 2
            ;;
        --calendar-id)
            CALENDAR_ID="$2"
            shift 2
            ;;
        --email-id)
            EMAIL_ID="$2"
            shift 2
            ;;
        --summary)
            SUMMARY="$2"
            shift 2
            ;;
        --start)
            START="$2"
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
python3 "$UTILS_DIR/event_tracking.py" track \
    --event-id "$EVENT_ID" \
    --calendar-id "$CALENDAR_ID" \
    --email-id "$EMAIL_ID" \
    --summary "$SUMMARY" \
    --start "$START"

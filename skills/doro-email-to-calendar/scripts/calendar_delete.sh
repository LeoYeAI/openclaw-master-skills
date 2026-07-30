#!/bin/bash
# Delete a calendar event using provider abstraction
# Usage: calendar_delete.sh --event-id <id> [--calendar-id <id>] [--provider <provider>]
#
# Returns JSON with success status

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

EVENT_ID=""
CALENDAR_ID=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --event-id)
            EVENT_ID="$2"
            shift 2
            ;;
        --calendar-id)
            CALENDAR_ID="$2"
            shift 2
            ;;
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$EVENT_ID" ]; then
    echo "Usage: calendar_delete.sh --event-id <id> [--calendar-id <id>] [--provider <provider>]" >&2
    exit 1
fi

ARGS=(delete --event-id "$EVENT_ID")
if [ -n "$CALENDAR_ID" ]; then
    ARGS+=(--calendar-id "$CALENDAR_ID")
fi
if [ -n "$PROVIDER" ]; then
    ARGS+=(--provider "$PROVIDER")
fi

python3 "$UTILS_DIR/calendar_ops.py" "${ARGS[@]}"

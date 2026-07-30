#!/bin/bash
# Search calendar events using provider abstraction
# Usage: calendar_search.sh [--calendar-id <id>] --from <datetime> --to <datetime> [--provider <provider>]
#
# Dates should be in ISO format (e.g., 2026-02-03T00:00:00)
# Returns JSON with list of events

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

CALENDAR_ID=""
FROM_DT=""
TO_DT=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --calendar-id)
            CALENDAR_ID="$2"
            shift 2
            ;;
        --from)
            FROM_DT="$2"
            shift 2
            ;;
        --to)
            TO_DT="$2"
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

if [ -z "$FROM_DT" ] || [ -z "$TO_DT" ]; then
    echo "Usage: calendar_search.sh [--calendar-id <id>] --from <datetime> --to <datetime> [--provider <provider>]" >&2
    exit 1
fi

# Build args array (avoids eval quoting issues)
ARGS=(search --from "$FROM_DT" --to "$TO_DT")
if [ -n "$CALENDAR_ID" ]; then
    ARGS+=(--calendar-id "$CALENDAR_ID")
fi
if [ -n "$PROVIDER" ]; then
    ARGS+=(--provider "$PROVIDER")
fi

python3 "$UTILS_DIR/calendar_ops.py" "${ARGS[@]}"

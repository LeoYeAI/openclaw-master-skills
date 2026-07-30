#!/bin/bash
# Check for duplicate calendar events
# Usage: check_duplicate.sh <calendar_id> <event_title> <date> [time] [--provider <provider>]

CALENDAR_ID="${1:-primary}"
EVENT_TITLE="$2"
DATE="$3"
TIME="${4:-}"
PROVIDER=""

# Parse optional --provider flag
shift 4 2>/dev/null || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$EVENT_TITLE" ] || [ -z "$DATE" ]; then
    echo "Usage: check_duplicate.sh <calendar_id> <event_title> <date> [time] [--provider <provider>]" >&2
    exit 1
fi

# Parse date using shared parser
SCRIPT_DIR="$(dirname "$0")"
if [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    ISO_DATE="$DATE"
else
    ISO_DATE=$(python3 "$SCRIPT_DIR/utils/date_parser.py" date "$DATE" 2>/dev/null)
fi

if [ -z "$ISO_DATE" ]; then
    echo "Could not parse date: $DATE" >&2
    exit 1
fi

# Calculate search range (day before to day after)
START_DATE=$(date -d "$ISO_DATE -1 day" '+%Y-%m-%dT00:00:00Z' 2>/dev/null || date -v-1d -j -f "%Y-%m-%d" "$ISO_DATE" "+%Y-%m-%dT00:00:00Z")
END_DATE=$(date -d "$ISO_DATE +2 days" '+%Y-%m-%dT00:00:00Z' 2>/dev/null || date -v+2d -j -f "%Y-%m-%d" "$ISO_DATE" "+%Y-%m-%dT00:00:00Z")

# Search for events using calendar_search.sh
# Build args array (avoids eval quoting issues)
SEARCH_ARGS=(--calendar-id "$CALENDAR_ID" --from "$START_DATE" --to "$END_DATE")
if [ -n "$PROVIDER" ]; then
    SEARCH_ARGS+=(--provider "$PROVIDER")
fi
events_result=$("$SCRIPT_DIR/calendar_search.sh" "${SEARCH_ARGS[@]}" 2>/dev/null)
events=$(echo "$events_result" | jq -r '.data // []' 2>/dev/null)

if [ -z "$events" ] || [ "$events" = "[]" ]; then
    echo "null"
    exit 0
fi

# Check for duplicates by title similarity
# Extract title keywords (first 5 words, normalized)
TITLE_KEYWORDS=$(echo "$EVENT_TITLE" | tr '[:upper:]' '[:lower:]' | tr -c '[:alnum:]' ' ' | awk '{print $1, $2, $3, $4, $5}')

# Use Python to check for duplicates
echo "$events" | python3 -c "
import json
import sys
import re

events = json.load(sys.stdin)
title_keywords = '$TITLE_KEYWORDS'.lower().split()
search_date = '$ISO_DATE'
time_str = '$TIME'

for event in events:
    event_title = event.get('summary', '').lower()
    event_start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))

    # Check if same date
    if search_date in event_start:
        # Check title similarity with improved logic for short titles
        matches = sum(1 for kw in title_keywords if kw in event_title)
        total_keywords = len(title_keywords)

        if total_keywords == 0:
            continue
        elif total_keywords <= 2:
            # Short titles: require ALL keywords to match
            if matches == total_keywords:
                print(json.dumps(event))
                sys.exit(0)
        else:
            # Longer titles: require at least 50% match
            if matches >= (total_keywords + 1) // 2:
                print(json.dumps(event))
                sys.exit(0)

print('null')
"

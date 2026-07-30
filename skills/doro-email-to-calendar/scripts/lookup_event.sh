#!/bin/bash
# Look up a tracked event by email_id, event_id, or summary
# Usage: lookup_event.sh --email-id <id> | --event-id <id> | --summary <text> | --list [--validate]
#
# Options:
#   --validate    Check if the calendar event still exists, remove orphaned entries
#
# Returns JSON with the event details if found, or empty array [] if not

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"
EVENTS_FILE="$HOME/.openclaw/workspace/memory/email-to-calendar/events.json"

# Parse arguments
SEARCH_TYPE=""
SEARCH_VALUE=""
VALIDATE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --email-id)
            SEARCH_TYPE="email_id"
            SEARCH_VALUE="$2"
            shift 2
            ;;
        --event-id)
            SEARCH_TYPE="event_id"
            SEARCH_VALUE="$2"
            shift 2
            ;;
        --summary)
            SEARCH_TYPE="summary"
            SEARCH_VALUE="$2"
            shift 2
            ;;
        --list)
            SEARCH_TYPE="list"
            shift
            ;;
        --validate)
            VALIDATE="true"
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: lookup_event.sh --email-id <id> | --event-id <id> | --summary <text> | --list [--validate]" >&2
            exit 1
            ;;
    esac
done

if [ -z "$SEARCH_TYPE" ]; then
    echo "Error: Must specify --email-id, --event-id, --summary, or --list" >&2
    exit 1
fi

if [ ! -f "$EVENTS_FILE" ]; then
    echo "[]"
    exit 0
fi

# Delegate to Python implementation
python3 "$UTILS_DIR/event_tracking.py" lookup \
    --type "$SEARCH_TYPE" \
    --value "$SEARCH_VALUE" \
    --validate "$VALIDATE" \
    --script-dir "$SCRIPT_DIR"

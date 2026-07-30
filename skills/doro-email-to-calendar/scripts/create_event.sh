#!/bin/bash
# Create or update a calendar event with automatic tracking and changelog
# Usage: create_event.sh <calendar_id> <title> <date> <start_time> <end_time> <description> <attendee_email> [event_id] [email_id] [--provider <provider>]
#
# If event_id is provided, updates existing event. Otherwise creates new one.
# Captures the event ID from JSON output and stores it in events.json tracking.
# Records changes to changelog.json for undo support.
# Returns the event ID on success for reference.

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

CALENDAR_ID="${1:-primary}"
TITLE="$2"
DATE="$3"
START_TIME="$4"
END_TIME="$5"
DESCRIPTION="$6"
ATTENDEE_EMAIL="$7"
EXISTING_EVENT_ID="${8:-}"
EMAIL_ID="${9:-}"
PROVIDER=""

# Parse optional --provider flag from remaining args
shift 9 2>/dev/null || true
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

if [ -z "$TITLE" ] || [ -z "$DATE" ]; then
    echo "Usage: create_event.sh <calendar_id> <title> <date> <start_time> <end_time> <description> <attendee_email> [event_id]" >&2
    exit 1
fi

# Get agent name from config for attribution (default: "Ripurapu")
CONFIG_FILE="$HOME/.config/email-to-calendar/config.json"
AGENT_NAME=$(jq -r '.agent_name // "Ripurapu"' "$CONFIG_FILE" 2>/dev/null)
if [ -z "$AGENT_NAME" ] || [ "$AGENT_NAME" = "null" ]; then
    AGENT_NAME="Ripurapu"
fi

# Append agent attribution to description
if [ -n "$DESCRIPTION" ]; then
    DESCRIPTION="$DESCRIPTION

---
Created by $AGENT_NAME (AI assistant)"
else
    DESCRIPTION="Created by $AGENT_NAME (AI assistant)"
fi

# Parse date to ISO format using shared parser
ISO_DATE=$(python3 "$SCRIPT_DIR/utils/date_parser.py" date "$DATE" 2>/dev/null)

if [ -z "$ISO_DATE" ]; then
    echo "Could not parse date: $DATE" >&2
    exit 1
fi

# Parse times using shared parser
START_PARSED=$(python3 "$SCRIPT_DIR/utils/date_parser.py" time "$START_TIME" 2>/dev/null)
END_PARSED=$(python3 "$SCRIPT_DIR/utils/date_parser.py" time "$END_TIME" 2>/dev/null)

# Default times if not provided
if [ -z "$START_PARSED" ]; then
    START_PARSED="09:00"
fi
if [ -z "$END_PARSED" ]; then
    END_PARSED="17:00"
fi

# Build ISO datetime strings
START_ISO="${ISO_DATE}T${START_PARSED}:00"
END_ISO="${ISO_DATE}T${END_PARSED}:00"

# Variable to track if this is a new creation (for changelog)
IS_NEW_EVENT=false
BEFORE_STATE=""

# Function to get current event state for changelog (before update)
get_event_state() {
    local event_id="$1"
    local cal_id="$2"
    # Try to get current state from tracking first (faster)
    local tracked=$("$SCRIPT_DIR/lookup_event.sh" --event-id "$event_id" 2>/dev/null)
    if [ "$(echo "$tracked" | jq 'length' 2>/dev/null)" -gt 0 ]; then
        echo "$tracked" | jq -c '.[0] | {summary: .summary, start: .start, end: null}'
    fi
}

# Function to create a new event using calendar_ops.py
create_new_event() {
    IS_NEW_EVENT=true
    # Build args array (avoids eval quoting issues)
    local -a CREATE_ARGS=(create --summary "$TITLE" --from "$START_ISO" --to "$END_ISO" --calendar-id "$CALENDAR_ID")

    if [ -n "$DESCRIPTION" ]; then
        CREATE_ARGS+=(--description "$DESCRIPTION")
    fi
    if [ -n "$ATTENDEE_EMAIL" ]; then
        CREATE_ARGS+=(--attendees "$ATTENDEE_EMAIL")
    fi
    if [ -n "$PROVIDER" ]; then
        CREATE_ARGS+=(--provider "$PROVIDER")
    fi

    RESULT=$(python3 "$UTILS_DIR/calendar_ops.py" "${CREATE_ARGS[@]}" 2>&1)
    # Extract event ID from JSON response (nested in data.id)
    EVENT_ID=$(echo "$RESULT" | jq -r '.data.id // empty' 2>/dev/null)
}

# Check if this is an update or create
if [ -n "$EXISTING_EVENT_ID" ]; then
    # Get before state for changelog
    BEFORE_STATE=$(get_event_state "$EXISTING_EVENT_ID" "$CALENDAR_ID")

    # Update existing event using calendar_ops.py
    echo "Updating existing event: $EXISTING_EVENT_ID" >&2
    # Build args array (avoids eval quoting issues)
    UPDATE_ARGS=(update --event-id "$EXISTING_EVENT_ID" --summary "$TITLE" --from "$START_ISO" --to "$END_ISO" --calendar-id "$CALENDAR_ID")

    if [ -n "$DESCRIPTION" ]; then
        UPDATE_ARGS+=(--description "$DESCRIPTION")
    fi
    if [ -n "$ATTENDEE_EMAIL" ]; then
        UPDATE_ARGS+=(--add-attendees "$ATTENDEE_EMAIL")
    fi
    if [ -n "$PROVIDER" ]; then
        UPDATE_ARGS+=(--provider "$PROVIDER")
    fi

    RESULT=$(python3 "$UTILS_DIR/calendar_ops.py" "${UPDATE_ARGS[@]}" 2>&1)

    # Self-healing: Check if event was deleted externally (404/410 error)
    if echo "$RESULT" | jq -e '.error_type == "not_found"' > /dev/null 2>&1 || echo "$RESULT" | grep -qiE "404|not found|410|gone|does not exist|deleted"; then
        echo "Event $EXISTING_EVENT_ID no longer exists, removing from tracking and creating new" >&2
        "$SCRIPT_DIR/delete_tracked_event.sh" --event-id "$EXISTING_EVENT_ID"
        BEFORE_STATE=""  # Clear before state since we're creating new
        # Fall back to creating a new event
        create_new_event
    else
        EVENT_ID="$EXISTING_EVENT_ID"
    fi
else
    # Create new event
    create_new_event
fi

# Output the result
echo "$RESULT"

# Track the event and log to changelog if we have an ID
if [ -n "$EVENT_ID" ]; then
    # Build args array (avoids eval quoting issues)
    TRACK_ARGS=(--event-id "$EVENT_ID" --calendar-id "$CALENDAR_ID" --summary "$TITLE" --start "$START_ISO")
    if [ -n "$EMAIL_ID" ]; then
        TRACK_ARGS+=(--email-id "$EMAIL_ID")
    fi
    "$SCRIPT_DIR/track_event.sh" "${TRACK_ARGS[@]}" >&2
    echo "Event ID: $EVENT_ID" >&2

    # Log to changelog for undo support
    if [ "$IS_NEW_EVENT" = true ]; then
        # Log create
        CHANGE_ID=$("$SCRIPT_DIR/changelog.sh" log-create \
            --event-id "$EVENT_ID" \
            --calendar-id "$CALENDAR_ID" \
            --summary "$TITLE" \
            --start "$START_ISO" \
            --end "$END_ISO" \
            --email-id "$EMAIL_ID" 2>/dev/null) || true
        if [ -n "$CHANGE_ID" ]; then
            echo "Change logged: $CHANGE_ID (can undo within 24 hours)" >&2
        fi
    elif [ -n "$BEFORE_STATE" ]; then
        # Log update with before/after state
        AFTER_STATE=$(cat << EOF
{"summary": "$TITLE", "start": "$START_ISO", "end": "$END_ISO"}
EOF
)
        CHANGE_ID=$("$SCRIPT_DIR/changelog.sh" log-update \
            --event-id "$EVENT_ID" \
            --calendar-id "$CALENDAR_ID" \
            --before-json "$BEFORE_STATE" \
            --after-json "$AFTER_STATE" \
            --email-id "$EMAIL_ID" 2>/dev/null) || true
        if [ -n "$CHANGE_ID" ]; then
            echo "Change logged: $CHANGE_ID (can undo within 24 hours)" >&2
        fi
    fi

    # Also update pending_invites.json to mark this event as created
    if [ -n "$EMAIL_ID" ]; then
        "$SCRIPT_DIR/update_invite_status.sh" \
            --email-id "$EMAIL_ID" \
            --event-title "$TITLE" \
            --status created \
            --event-id "$EVENT_ID" 2>/dev/null || true

        # Auto-disposition email based on config (mark read and/or archive)
        "$SCRIPT_DIR/disposition_email.sh" --email-id "$EMAIL_ID" 2>/dev/null || true
    fi
fi

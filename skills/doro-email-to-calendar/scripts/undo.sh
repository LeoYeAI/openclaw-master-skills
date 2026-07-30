#!/bin/bash
# Undo recent calendar changes
# Usage: undo.sh <action> [options]
#
# Actions:
#   last                       Undo the most recent undoable change
#   --change-id <id>           Undo a specific change by ID
#   list                       List undoable changes
#
# Options:
#   --provider <provider>      Calendar provider (default: from config)
#
# Undo behavior:
#   create -> deletes the event
#   update -> restores the 'before' state
#   delete -> recreates the event (if within time window)

SCRIPTS_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPTS_DIR/utils"

# Parse action
ACTION="${1:-}"
shift 2>/dev/null || true

CHANGE_ID=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --change-id)
            CHANGE_ID="$2"
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

# Provider will be added to each args array individually

case "$ACTION" in
    last)
        # Find most recent undoable change
        CHANGE_ID=$(python3 "$UTILS_DIR/undo_ops.py" find-last 2>/dev/null)
        if [ -z "$CHANGE_ID" ]; then
            echo "No undoable changes found." >&2
            exit 1
        fi
        echo "Undoing: $CHANGE_ID"
        ;;

    list)
        python3 "$UTILS_DIR/undo_ops.py" list
        exit 0
        ;;

    --change-id)
        if [ -z "$2" ]; then
            echo "Error: --change-id requires a value" >&2
            exit 1
        fi
        CHANGE_ID="$2"
        ;;

    "")
        echo "Usage: undo.sh <action> [options]"
        echo ""
        echo "Actions:"
        echo "  last                  Undo the most recent undoable change"
        echo "  --change-id <id>      Undo a specific change by ID"
        echo "  list                  List undoable changes"
        exit 1
        ;;

    *)
        # Assume it's a change ID directly
        CHANGE_ID="$ACTION"
        ;;
esac

if [ -z "$CHANGE_ID" ]; then
    echo "Error: No change ID specified" >&2
    exit 1
fi

# Get the change details
CHANGE_JSON=$("$SCRIPTS_DIR/changelog.sh" get --change-id "$CHANGE_ID" 2>/dev/null)
if [ -z "$CHANGE_JSON" ]; then
    echo "Error: Change $CHANGE_ID not found" >&2
    exit 1
fi

# Check if can undo
CAN_UNDO=$("$SCRIPTS_DIR/changelog.sh" can-undo --change-id "$CHANGE_ID" 2>/dev/null)
if [ "$CAN_UNDO" != "true" ]; then
    echo "Error: Change $CHANGE_ID cannot be undone (older than 24 hours or already undone)" >&2
    exit 1
fi

# Parse change details
ACTION_TYPE=$(echo "$CHANGE_JSON" | jq -r '.action')
EVENT_ID=$(echo "$CHANGE_JSON" | jq -r '.event_id')
CALENDAR_ID=$(echo "$CHANGE_JSON" | jq -r '.calendar_id // "primary"')

echo "Undoing $ACTION_TYPE for event $EVENT_ID..."

case "$ACTION_TYPE" in
    create)
        # Undo create: delete the event using calendar_ops.py
        echo "Deleting event that was created..."
        DELETE_ARGS=(delete --event-id "$EVENT_ID" --calendar-id "$CALENDAR_ID")
        if [ -n "$PROVIDER" ]; then
            DELETE_ARGS+=(--provider "$PROVIDER")
        fi
        RESULT=$(python3 "$UTILS_DIR/calendar_ops.py" "${DELETE_ARGS[@]}" 2>&1)

        if echo "$RESULT" | jq -e '.success == false' > /dev/null 2>&1; then
            echo "Warning: Event may already be deleted: $(echo "$RESULT" | jq -r '.error')" >&2
        else
            echo "Event deleted successfully"
        fi

        # Remove from tracking
        "$SCRIPTS_DIR/delete_tracked_event.sh" --event-id "$EVENT_ID" 2>/dev/null || true
        ;;

    update)
        # Undo update: restore before state using calendar_ops.py
        BEFORE_SUMMARY=$(echo "$CHANGE_JSON" | jq -r '.before.summary // empty')
        BEFORE_START=$(echo "$CHANGE_JSON" | jq -r '.before.start // empty')
        BEFORE_END=$(echo "$CHANGE_JSON" | jq -r '.before.end // empty')

        if [ -z "$BEFORE_SUMMARY" ]; then
            echo "Error: No 'before' state recorded for this update" >&2
            exit 1
        fi

        echo "Restoring previous state: \"$BEFORE_SUMMARY\""

        UPDATE_ARGS=(update --event-id "$EVENT_ID" --calendar-id "$CALENDAR_ID" --summary "$BEFORE_SUMMARY")
        if [ -n "$BEFORE_START" ]; then
            UPDATE_ARGS+=(--from "$BEFORE_START")
        fi
        if [ -n "$BEFORE_END" ]; then
            UPDATE_ARGS+=(--to "$BEFORE_END")
        fi
        if [ -n "$PROVIDER" ]; then
            UPDATE_ARGS+=(--provider "$PROVIDER")
        fi

        RESULT=$(python3 "$UTILS_DIR/calendar_ops.py" "${UPDATE_ARGS[@]}" 2>&1)

        if echo "$RESULT" | jq -e '.success == false' > /dev/null 2>&1; then
            echo "Error restoring event: $(echo "$RESULT" | jq -r '.error')" >&2
            exit 1
        fi

        echo "Event restored to previous state"

        # Update tracking
        "$SCRIPTS_DIR/update_tracked_event.sh" --event-id "$EVENT_ID" --summary "$BEFORE_SUMMARY" 2>/dev/null || true
        ;;

    delete)
        # Undo delete: recreate the event using calendar_ops.py
        BEFORE_SUMMARY=$(echo "$CHANGE_JSON" | jq -r '.before.summary // empty')
        BEFORE_START=$(echo "$CHANGE_JSON" | jq -r '.before.start // empty')
        BEFORE_END=$(echo "$CHANGE_JSON" | jq -r '.before.end // empty')

        if [ -z "$BEFORE_SUMMARY" ] || [ -z "$BEFORE_START" ]; then
            echo "Error: Insufficient 'before' state to recreate event" >&2
            exit 1
        fi

        echo "Recreating deleted event: \"$BEFORE_SUMMARY\""

        CREATE_ARGS=(create --summary "$BEFORE_SUMMARY" --from "$BEFORE_START" --to "$BEFORE_END" --calendar-id "$CALENDAR_ID")
        if [ -n "$PROVIDER" ]; then
            CREATE_ARGS+=(--provider "$PROVIDER")
        fi
        RESULT=$(python3 "$UTILS_DIR/calendar_ops.py" "${CREATE_ARGS[@]}" 2>&1)

        NEW_EVENT_ID=$(echo "$RESULT" | jq -r '.data.id // empty' 2>/dev/null)

        if [ -n "$NEW_EVENT_ID" ]; then
            echo "Event recreated with new ID: $NEW_EVENT_ID"

            # Track the new event
            "$SCRIPTS_DIR/track_event.sh" \
                --event-id "$NEW_EVENT_ID" \
                --calendar-id "$CALENDAR_ID" \
                --summary "$BEFORE_SUMMARY" \
                --start "$BEFORE_START" 2>/dev/null || true
        else
            echo "Error recreating event: $(echo "$RESULT" | jq -r '.error // .raw')" >&2
            exit 1
        fi
        ;;

    *)
        echo "Error: Unknown action type: $ACTION_TYPE" >&2
        exit 1
        ;;
esac

# Mark the change as undone
python3 "$UTILS_DIR/undo_ops.py" mark-undone --change-id "$CHANGE_ID"

echo "Undo complete. Change $CHANGE_ID has been reversed."

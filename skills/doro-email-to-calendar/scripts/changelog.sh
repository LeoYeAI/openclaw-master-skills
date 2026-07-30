#!/bin/bash
# Record event changes for audit trail and undo support
# Usage: changelog.sh <action> [options]
#
# Actions:
#   log-create --event-id <id> --calendar-id <cal> --summary <s> --start <t> --end <t> [--email-id <id>]
#   log-update --event-id <id> --calendar-id <cal> --before-json <json> --after-json <json> [--email-id <id>]
#   log-delete --event-id <id> --calendar-id <cal> --before-json <json>
#   list [--last N]            List recent changes (default: 10)
#   get --change-id <id>       Get details of a specific change
#   can-undo --change-id <id>  Check if a change can still be undone
#
# Logs to ~/.openclaw/workspace/memory/email-to-calendar/changelog.json
# Changes older than 24 hours have can_undo=false

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

# Parse action
ACTION="${1:-}"
shift 2>/dev/null || true

# Build arguments array for Python script
ARGS=("$ACTION")

while [[ $# -gt 0 ]]; do
    case "$1" in
        --event-id|--calendar-id|--summary|--start|--end|--email-id|--before-json|--after-json|--change-id|--last)
            ARGS+=("$1" "$2")
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Validate required arguments for each action
case "$ACTION" in
    log-create)
        has_event_id=false
        has_summary=false
        for ((i=0; i<${#ARGS[@]}; i++)); do
            case "${ARGS[$i]}" in
                --event-id) has_event_id=true ;;
                --summary) has_summary=true ;;
            esac
        done
        if ! $has_event_id || ! $has_summary; then
            echo "Error: --event-id and --summary are required for log-create" >&2
            exit 1
        fi
        ;;
    log-update)
        has_event_id=false
        for ((i=0; i<${#ARGS[@]}; i++)); do
            if [[ "${ARGS[$i]}" == "--event-id" ]]; then
                has_event_id=true
                break
            fi
        done
        if ! $has_event_id; then
            echo "Error: --event-id is required for log-update" >&2
            exit 1
        fi
        ;;
    log-delete)
        has_event_id=false
        for ((i=0; i<${#ARGS[@]}; i++)); do
            if [[ "${ARGS[$i]}" == "--event-id" ]]; then
                has_event_id=true
                break
            fi
        done
        if ! $has_event_id; then
            echo "Error: --event-id is required for log-delete" >&2
            exit 1
        fi
        ;;
    get|can-undo)
        has_change_id=false
        for ((i=0; i<${#ARGS[@]}; i++)); do
            if [[ "${ARGS[$i]}" == "--change-id" ]]; then
                has_change_id=true
                break
            fi
        done
        if ! $has_change_id; then
            echo "Error: --change-id is required for $ACTION" >&2
            exit 1
        fi
        ;;
    list)
        # No required arguments
        ;;
    "")
        echo "Usage: changelog.sh <action> [options]"
        echo ""
        echo "Actions:"
        echo "  log-create --event-id <id> --calendar-id <cal> --summary <s> --start <t> --end <t>"
        echo "  log-update --event-id <id> --calendar-id <cal> --before-json <json> --after-json <json>"
        echo "  log-delete --event-id <id> --calendar-id <cal> --before-json <json>"
        echo "  list [--last N]            List recent changes (default: 10)"
        echo "  get --change-id <id>       Get details of a specific change"
        echo "  can-undo --change-id <id>  Check if a change can still be undone"
        exit 1
        ;;
esac

# Delegate to Python implementation
python3 "$UTILS_DIR/changelog_ops.py" "${ARGS[@]}"

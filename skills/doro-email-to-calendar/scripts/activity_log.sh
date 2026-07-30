#!/bin/bash
# Record activity for silent audit trail
# Usage: activity_log.sh <action> [options]
#
# Actions:
#   start-session              Start a new processing session
#   log-skip --email-id <id> --subject <sub> --reason <reason>
#   log-event --email-id <id> --title <title> --action <created|auto_ignored|pending>
#   end-session                Finalize the current session
#   show [--last N]            Show recent activity (default: last session)
#
# Logs to ~/.openclaw/workspace/memory/email-to-calendar/activity.json
# This creates a silent audit trail - use 'show' to display on request

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

# Parse action
ACTION="${1:-}"
shift 2>/dev/null || true

# Build arguments array for Python script
ARGS=("$ACTION")

while [[ $# -gt 0 ]]; do
    case "$1" in
        --email-id|--subject|--title|--reason|--action|--last)
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
    log-skip)
        has_email_id=false
        has_reason=false
        for ((i=0; i<${#ARGS[@]}; i++)); do
            case "${ARGS[$i]}" in
                --email-id) has_email_id=true ;;
                --reason) has_reason=true ;;
            esac
        done
        if ! $has_email_id || ! $has_reason; then
            echo "Error: --email-id and --reason are required for log-skip" >&2
            exit 1
        fi
        ;;
    log-event)
        has_email_id=false
        has_title=false
        for ((i=0; i<${#ARGS[@]}; i++)); do
            case "${ARGS[$i]}" in
                --email-id) has_email_id=true ;;
                --title) has_title=true ;;
            esac
        done
        if ! $has_email_id || ! $has_title; then
            echo "Error: --email-id and --title are required for log-event" >&2
            exit 1
        fi
        ;;
    start-session|end-session|show)
        # No required arguments
        ;;
    "")
        echo "Usage: activity_log.sh <action> [options]"
        echo ""
        echo "Actions:"
        echo "  start-session              Start a new processing session"
        echo "  log-skip --email-id <id> --subject <sub> --reason <reason>"
        echo "  log-event --email-id <id> --title <title> --action <action> [--reason <reason>]"
        echo "  end-session                Finalize the current session"
        echo "  show [--last N]            Show recent activity (default: last session)"
        exit 1
        ;;
esac

# Delegate to Python implementation
python3 "$UTILS_DIR/activity_ops.py" "${ARGS[@]}"

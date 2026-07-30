#!/bin/bash
# Update the status of a pending invite event
#
# Usage: update_invite_status.sh --invite-id <id> --event-title <title> --status <status> [--event-id <cal_event_id>]
#        update_invite_status.sh --email-id <email_id> --event-title <title> --status <status> [--event-id <cal_event_id>]
#
# Status values: pending, created, dismissed, expired
#
# Examples:
#   update_invite_status.sh --invite-id inv_20260201_001 --event-title "Valentine's Day" --status created --event-id abc123
#   update_invite_status.sh --email-id 19c1c86dcc389443 --event-title "Staff Development" --status dismissed

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"
PENDING_FILE="$HOME/.openclaw/workspace/memory/email-to-calendar/pending_invites.json"

INVITE_ID=""
EMAIL_ID=""
EVENT_TITLE=""
NEW_STATUS=""
CALENDAR_EVENT_ID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --invite-id)
            INVITE_ID="$2"
            shift 2
            ;;
        --email-id)
            EMAIL_ID="$2"
            shift 2
            ;;
        --event-title)
            EVENT_TITLE="$2"
            shift 2
            ;;
        --status)
            NEW_STATUS="$2"
            shift 2
            ;;
        --event-id)
            CALENDAR_EVENT_ID="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Validate inputs
if [ -z "$EVENT_TITLE" ] || [ -z "$NEW_STATUS" ]; then
    echo "Error: --event-title and --status are required" >&2
    echo "Usage: update_invite_status.sh --invite-id <id> --event-title <title> --status <status>" >&2
    exit 1
fi

if [ -z "$INVITE_ID" ] && [ -z "$EMAIL_ID" ]; then
    echo "Error: Either --invite-id or --email-id is required" >&2
    exit 1
fi

# Validate status
case "$NEW_STATUS" in
    pending|created|dismissed|expired)
        ;;
    *)
        echo "Error: Invalid status. Must be: pending, created, dismissed, expired" >&2
        exit 1
        ;;
esac

# Check if file exists
if [ ! -f "$PENDING_FILE" ]; then
    echo "Error: No pending invites file found" >&2
    exit 1
fi

# Delegate to Python implementation
python3 "$UTILS_DIR/invite_ops.py" \
    --invite-id "$INVITE_ID" \
    --email-id "$EMAIL_ID" \
    --event-title "$EVENT_TITLE" \
    --status "$NEW_STATUS" \
    --event-id "$CALENDAR_EVENT_ID"

#!/bin/bash
# Add a pending invite with events to track
#
# Usage: add_pending.sh --email-id <id> --email-subject <subject> --events-json <json>
#
# Arguments:
#   --email-id      The email message ID (required)
#   --email-subject The email subject line (optional)
#   --events-json   JSON array of events with keys: title, date, time, status (required)
#
# Example:
#   add_pending.sh --email-id "19c2b6cde1cf74e2" \
#     --email-subject "Birthday Party Invite" \
#     --events-json '[{"title":"Birthday Party","date":"2026-02-15","time":"14:00","status":"pending"}]'
#
# Returns JSON: {"success": true, "invite_id": "inv_20260205_001"}

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

EMAIL_ID=""
EMAIL_SUBJECT=""
EVENTS_JSON=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --email-id)
            EMAIL_ID="$2"
            shift 2
            ;;
        --email-subject)
            EMAIL_SUBJECT="$2"
            shift 2
            ;;
        --events-json)
            EVENTS_JSON="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Validate required arguments
if [ -z "$EMAIL_ID" ]; then
    echo "Error: --email-id is required" >&2
    echo "Usage: add_pending.sh --email-id <id> --email-subject <subject> --events-json <json>" >&2
    exit 1
fi

if [ -z "$EVENTS_JSON" ]; then
    echo "Error: --events-json is required" >&2
    exit 1
fi

# Build args array (avoids eval quoting issues)
ARGS=(add --email-id "$EMAIL_ID" --events-json "$EVENTS_JSON")
if [ -n "$EMAIL_SUBJECT" ]; then
    ARGS+=(--email-subject "$EMAIL_SUBJECT")
fi

python3 "$UTILS_DIR/pending_ops.py" "${ARGS[@]}"

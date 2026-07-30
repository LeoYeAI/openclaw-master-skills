#!/bin/bash
# Modify an email (add/remove labels) using provider abstraction
# Usage: email_modify.sh --email-id <id> [--remove-labels <labels>] [--add-labels <labels>] [--provider <provider>]
#
# Labels should be comma-separated (e.g., "UNREAD,INBOX")
# Returns JSON with success status

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

EMAIL_ID=""
REMOVE_LABELS=""
ADD_LABELS=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --email-id)
            EMAIL_ID="$2"
            shift 2
            ;;
        --remove-labels)
            REMOVE_LABELS="$2"
            shift 2
            ;;
        --add-labels)
            ADD_LABELS="$2"
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

if [ -z "$EMAIL_ID" ]; then
    echo "Usage: email_modify.sh --email-id <id> [--remove-labels <labels>] [--add-labels <labels>] [--provider <provider>]" >&2
    exit 1
fi

# Build args array (avoids eval quoting issues)
ARGS=(modify --email-id "$EMAIL_ID")
if [ -n "$REMOVE_LABELS" ]; then
    ARGS+=(--remove-labels "$REMOVE_LABELS")
fi
if [ -n "$ADD_LABELS" ]; then
    ARGS+=(--add-labels "$ADD_LABELS")
fi
if [ -n "$PROVIDER" ]; then
    ARGS+=(--provider "$PROVIDER")
fi

python3 "$UTILS_DIR/email_ops.py" "${ARGS[@]}"

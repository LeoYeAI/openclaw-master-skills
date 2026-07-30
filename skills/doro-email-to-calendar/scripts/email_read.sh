#!/bin/bash
# Read an email by ID using provider abstraction
# Usage: email_read.sh --email-id <id> [--provider <provider>]
#
# Returns JSON with email content

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

EMAIL_ID=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --email-id)
            EMAIL_ID="$2"
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
    echo "Usage: email_read.sh --email-id <id> [--provider <provider>]" >&2
    exit 1
fi

ARGS=(read --email-id "$EMAIL_ID")
if [ -n "$PROVIDER" ]; then
    ARGS+=(--provider "$PROVIDER")
fi

python3 "$UTILS_DIR/email_ops.py" "${ARGS[@]}"

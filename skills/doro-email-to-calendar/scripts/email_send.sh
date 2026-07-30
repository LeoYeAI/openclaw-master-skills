#!/bin/bash
# Send an email using provider abstraction
# Usage: email_send.sh --to <email> --subject <subject> --body <body> [--provider <provider>]
#
# Returns JSON with success status

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

TO=""
SUBJECT=""
BODY=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --to)
            TO="$2"
            shift 2
            ;;
        --subject)
            SUBJECT="$2"
            shift 2
            ;;
        --body)
            BODY="$2"
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

if [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
    echo "Usage: email_send.sh --to <email> --subject <subject> --body <body> [--provider <provider>]" >&2
    exit 1
fi

ARGS=(send --to "$TO" --subject "$SUBJECT" --body "$BODY")
if [ -n "$PROVIDER" ]; then
    ARGS+=(--provider "$PROVIDER")
fi

python3 "$UTILS_DIR/email_ops.py" "${ARGS[@]}"

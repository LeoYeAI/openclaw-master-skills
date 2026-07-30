#!/bin/bash
# Disposition an email (mark read and/or archive) based on config
# Usage: disposition_email.sh --email-id <id> [options]
#
# Options:
#   --email-id <id>     Email message ID (required)
#   --mark-read         Force mark as read (override config)
#   --no-mark-read      Skip marking as read (override config)
#   --archive           Force archive (override config)
#   --no-archive        Skip archiving (override config)
#   --provider <name>   Provider to use (default: from config)
#
# Returns JSON with success status and actions taken

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

EMAIL_ID=""
MARK_READ=""
NO_MARK_READ=""
ARCHIVE=""
NO_ARCHIVE=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --email-id)
            EMAIL_ID="$2"
            shift 2
            ;;
        --mark-read)
            MARK_READ="true"
            shift
            ;;
        --no-mark-read)
            NO_MARK_READ="true"
            shift
            ;;
        --archive)
            ARCHIVE="true"
            shift
            ;;
        --no-archive)
            NO_ARCHIVE="true"
            shift
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
    echo "Usage: disposition_email.sh --email-id <id> [--mark-read] [--no-mark-read] [--archive] [--no-archive] [--provider <provider>]" >&2
    exit 1
fi

# Build args array (avoids eval quoting issues)
ARGS=(disposition --email-id "$EMAIL_ID")

if [ "$MARK_READ" = "true" ]; then
    ARGS+=(--mark-read true)
fi
if [ "$NO_MARK_READ" = "true" ]; then
    ARGS+=(--no-mark-read)
fi
if [ "$ARCHIVE" = "true" ]; then
    ARGS+=(--archive true)
fi
if [ "$NO_ARCHIVE" = "true" ]; then
    ARGS+=(--no-archive)
fi
if [ -n "$PROVIDER" ]; then
    ARGS+=(--provider "$PROVIDER")
fi

python3 "$UTILS_DIR/disposition_ops.py" "${ARGS[@]}"

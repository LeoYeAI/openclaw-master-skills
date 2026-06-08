#!/usr/bin/env bash
set -euo pipefail

# notify.sh — Utility script for sending notifications through OpenClaw messaging.
# Outputs structured JSON that the agent runtime uses to send the actual message.

VALID_CHANNELS="telegram whatsapp slack discord email"

usage() {
    cat <<'EOF'
Usage: notify.sh <channel> <message> [--urgent]

Send a notification through OpenClaw messaging.

Arguments:
  channel    Notification channel: telegram, whatsapp, slack, discord, email
  message    The notification text (quote if it contains spaces)

Options:
  --urgent   Mark as urgent (adds warning prefix, requests immediate delivery)
  --help     Show this help message

Output:
  Structured JSON for the agent runtime to send the actual message.

Example:
  notify.sh telegram "Workflow 'Monday Report' completed. 5/5 steps passed."
  notify.sh slack "Step 3 failed: element not found" --urgent
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage

if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments. Use --help for usage." >&2
    exit 1
fi

CHANNEL="$1"
MESSAGE="$2"
shift 2
URGENT="false"

while [ $# -gt 0 ]; do
    case "$1" in
        --urgent)
            URGENT="true"
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo "Error: Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate channel
channel_valid="false"
for vc in $VALID_CHANNELS; do
    if [ "$CHANNEL" = "$vc" ]; then
        channel_valid="true"
        break
    fi
done

if [ "$channel_valid" = "false" ]; then
    echo "Error: Invalid channel '$CHANNEL'. Valid: $VALID_CHANNELS" >&2
    exit 1
fi

# Add urgent prefix if requested
if [ "$URGENT" = "true" ]; then
    MESSAGE="⚠️ $MESSAGE"
fi

# Get timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Output structured JSON
jq -n \
    --arg channel "$CHANNEL" \
    --arg message "$MESSAGE" \
    --argjson urgent "$URGENT" \
    --arg timestamp "$TIMESTAMP" \
    '{
        channel: $channel,
        message: $message,
        urgent: $urgent,
        timestamp: $timestamp
    }'

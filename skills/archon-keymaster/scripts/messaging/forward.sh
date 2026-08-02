#!/bin/bash
# Forward a dmail
# Usage: forward.sh <dmail-did> <recipient-did> [additional-body]

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
fi
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

if [ $# -lt 2 ]; then
    echo "Usage: $0 <dmail-did> <recipient-did> [additional-body]"
    exit 1
fi

ORIGINAL_DID="$1"
RECIPIENT="$2"
ADDITIONAL="${3:-}"

# Get original message from list (has metadata)
DMAILS=$(npx @didcid/keymaster list-dmail 2>/dev/null)
ORIGINAL=$(echo "$DMAILS" | jq --arg did "$ORIGINAL_DID" '.[$did] // empty')

if [ -z "$ORIGINAL" ] || [ "$ORIGINAL" = "null" ]; then
    echo "Error: Could not retrieve original dmail from inbox"
    exit 1
fi

SENDER=$(echo "$ORIGINAL" | jq -r '.sender // "Unknown"')
SUBJECT=$(echo "$ORIGINAL" | jq -r '.message.subject')
BODY=$(echo "$ORIGINAL" | jq -r '.message.body')
DATE=$(echo "$ORIGINAL" | jq -r '.date')

# Add Fwd: prefix if not already there
if [[ ! "$SUBJECT" =~ ^Fwd: ]]; then
    SUBJECT="Fwd: $SUBJECT"
fi

# Build forwarded body
FORWARD_BODY=""
if [ -n "$ADDITIONAL" ]; then
    FORWARD_BODY="$ADDITIONAL

---------- Forwarded message ----------"
else
    FORWARD_BODY="---------- Forwarded message ----------"
fi
FORWARD_BODY="$FORWARD_BODY
From: $SENDER
Date: $DATE
Subject: $SUBJECT

$BODY"

# Create forward JSON
TMPFILE=$(mktemp /tmp/dmail-XXXXXX.json)
trap "rm -f $TMPFILE" EXIT

# Escape for JSON
FORWARD_BODY_ESCAPED=$(echo "$FORWARD_BODY" | jq -Rs .)

cat > "$TMPFILE" << EOF
{
    "to": ["$RECIPIENT"],
    "cc": [],
    "subject": "$SUBJECT",
    "body": $FORWARD_BODY_ESCAPED,
    "reference": "$ORIGINAL_DID"
}
EOF

# Create and send
echo "Creating forward..." >&2
DMAIL_DID=$(npx @didcid/keymaster create-dmail "$TMPFILE")
echo "Sending..." >&2
NOTICE_DID=$(npx @didcid/keymaster send-dmail "$DMAIL_DID")
echo "Forwarded! Notice: $NOTICE_DID" >&2

npx @didcid/keymaster file-dmail "$DMAIL_DID" "sent" >/dev/null 2>&1

echo "$DMAIL_DID"

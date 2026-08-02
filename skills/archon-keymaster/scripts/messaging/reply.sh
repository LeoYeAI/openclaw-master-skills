#!/bin/bash
# Reply to a dmail
# Usage: reply.sh <dmail-did> <body>

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
    echo "Usage: $0 <dmail-did> <body>"
    exit 1
fi

ORIGINAL_DID="$1"
BODY="$2"

# Get original message from list (has metadata)
DMAILS=$(npx @didcid/keymaster list-dmail 2>/dev/null)
ORIGINAL=$(echo "$DMAILS" | jq --arg did "$ORIGINAL_DID" '.[$did] // empty')

if [ -z "$ORIGINAL" ] || [ "$ORIGINAL" = "null" ]; then
    echo "Error: Could not retrieve original dmail from inbox"
    exit 1
fi

# Extract sender DID (controller of the dmail DID doc)
SENDER_DID=$(echo "$ORIGINAL" | jq -r '.docs.didDocument.controller')
SUBJECT=$(echo "$ORIGINAL" | jq -r '.message.subject')

if [ "$SENDER_DID" = "null" ] || [ -z "$SENDER_DID" ]; then
    echo "Error: Could not determine sender DID"
    exit 1
fi

# Add Re: prefix if not already there
if [[ ! "$SUBJECT" =~ ^Re: ]]; then
    SUBJECT="Re: $SUBJECT"
fi

# Escape body for JSON
BODY_ESCAPED=$(echo "$BODY" | jq -Rs .)

# Create reply JSON
TMPFILE=$(mktemp /tmp/dmail-XXXXXX.json)
trap "rm -f $TMPFILE" EXIT

cat > "$TMPFILE" << EOF
{
    "to": ["$SENDER_DID"],
    "cc": [],
    "subject": "$SUBJECT",
    "body": $BODY_ESCAPED,
    "reference": "$ORIGINAL_DID"
}
EOF

# Create and send
echo "Creating reply..." >&2
DMAIL_DID=$(npx @didcid/keymaster create-dmail "$TMPFILE")
echo "Sending..." >&2
NOTICE_DID=$(npx @didcid/keymaster send-dmail "$DMAIL_DID")
echo "Reply sent! Notice: $NOTICE_DID" >&2

npx @didcid/keymaster file-dmail "$DMAIL_DID" "sent" >/dev/null 2>&1

echo "$DMAIL_DID"

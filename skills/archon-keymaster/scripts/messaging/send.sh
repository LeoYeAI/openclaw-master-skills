#!/bin/bash
# Send a dmail to one or more recipients
# Usage: send.sh <recipient-did> <subject> <body> [cc-did...]

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
fi
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

if [ $# -lt 3 ]; then
    echo "Usage: $0 <recipient-did> <subject> <body> [cc-did...]"
    echo "Example: $0 'did:cid:alice...' 'Hello' 'How are you?'"
    exit 1
fi

RECIPIENT="$1"
SUBJECT="$2"
BODY="$3"
shift 3

# Build CC array from remaining arguments
CC_JSON="[]"
if [ $# -gt 0 ]; then
    CC_JSON=$(printf '%s\n' "$@" | jq -R . | jq -s .)
fi

# Escape subject and body for JSON
SUBJECT_ESCAPED=$(echo "$SUBJECT" | jq -Rs . | sed 's/^"//;s/"$//')
BODY_ESCAPED=$(echo "$BODY" | jq -Rs .)

# Create temporary JSON file
TMPFILE=$(mktemp /tmp/dmail-XXXXXX.json)
trap "rm -f $TMPFILE" EXIT

cat > "$TMPFILE" << EOF
{
    "to": ["$RECIPIENT"],
    "cc": $CC_JSON,
    "subject": "$SUBJECT_ESCAPED",
    "body": $BODY_ESCAPED,
    "reference": ""
}
EOF

# Create the dmail
echo "Creating dmail..." >&2
DMAIL_DID=$(npx @didcid/keymaster create-dmail "$TMPFILE")
echo "Created: $DMAIL_DID" >&2

# Send the dmail
echo "Sending..." >&2
NOTICE_DID=$(npx @didcid/keymaster send-dmail "$DMAIL_DID")
echo "Sent! Notice: $NOTICE_DID" >&2

# Tag as sent
npx @didcid/keymaster file-dmail "$DMAIL_DID" "sent" >/dev/null 2>&1

# Return the dmail DID
echo "$DMAIL_DID"

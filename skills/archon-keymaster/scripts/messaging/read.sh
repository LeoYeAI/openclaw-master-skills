#!/bin/bash
# Read a specific dmail
# Usage: read.sh <dmail-did>

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
fi
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 <dmail-did>"
    exit 1
fi

DMAIL_DID="$1"

# Get full dmail list and filter for this one (list-dmail has full metadata)
DMAILS=$(npx @didcid/keymaster list-dmail 2>/dev/null)
DMAIL=$(echo "$DMAILS" | jq --arg did "$DMAIL_DID" '.[$did] // empty')

if [ -z "$DMAIL" ] || [ "$DMAIL" = "null" ]; then
    # Try getting just the message content
    MSG=$(npx @didcid/keymaster get-dmail "$DMAIL_DID" 2>/dev/null)
    if [ -z "$MSG" ] || [ "$MSG" = "null" ]; then
        echo "Error: Could not retrieve dmail $DMAIL_DID"
        exit 1
    fi
    # Display minimal format (message only, no metadata)
    echo "═══════════════════════════════════════════════════════════════"
    echo "$MSG" | jq -r '
        "To:      \(.to | join(", "))",
        (if .cc | length > 0 then "CC:      \(.cc | join(", "))" else empty end),
        "Subject: \(.subject)",
        (if .reference != "" then "Re:      \(.reference)" else empty end),
        "═══════════════════════════════════════════════════════════════",
        "",
        .body
    '
    exit 0
fi

# Display formatted with full metadata
echo "$DMAIL" | jq -r '
    "═══════════════════════════════════════════════════════════════",
    "From:    \(.sender // "Unknown")",
    "To:      \(.to | join(", "))",
    (if .cc | length > 0 then "CC:      \(.cc | join(", "))" else empty end),
    "Date:    \(.date // "Unknown")",
    "Subject: \(.message.subject)",
    (if .message.reference != "" then "Re:      \(.message.reference)" else empty end),
    "Tags:    \(.tags | join(", "))",
    "═══════════════════════════════════════════════════════════════",
    "",
    .message.body,
    ""
'

# Show attachments if any
ATTACHMENTS=$(echo "$DMAIL" | jq -r '.attachments | keys | length')
if [ "$ATTACHMENTS" -gt 0 ]; then
    echo "Attachments:"
    echo "$DMAIL" | jq -r '.attachments | to_entries[] | "  - \(.key)"'
fi

# Mark as read (remove unread tag, keep others)
CURRENT_TAGS=$(echo "$DMAIL" | jq -r '.tags | map(select(. != "unread")) | join(",")')
if [ -n "$CURRENT_TAGS" ]; then
    npx @didcid/keymaster file-dmail "$DMAIL_DID" "$CURRENT_TAGS" >/dev/null 2>&1 || true
fi

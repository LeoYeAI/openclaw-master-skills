#!/bin/bash
# Download an attachment from a dmail
# Usage: get-attachment.sh <dmail-did> <attachment-name> <output-path>

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
    echo "Usage: $0 <dmail-did> <attachment-name> <output-path>"
    echo ""
    echo "To list attachments, use: npx @didcid/keymaster list-dmail-attachments <dmail-did>"
    exit 1
fi

DMAIL_DID="$1"
ATTACHMENT_NAME="$2"
OUTPUT_PATH="$3"

npx @didcid/keymaster get-dmail-attachment "$DMAIL_DID" "$ATTACHMENT_NAME" "$OUTPUT_PATH"

echo "Downloaded '$ATTACHMENT_NAME' to $OUTPUT_PATH"

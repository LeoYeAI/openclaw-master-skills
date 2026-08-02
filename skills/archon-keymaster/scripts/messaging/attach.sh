#!/bin/bash
# Add an attachment to a dmail
# Usage: attach.sh <dmail-did> <file-path>

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
    echo "Usage: $0 <dmail-did> <file-path>"
    exit 1
fi

DMAIL_DID="$1"
FILE_PATH="$2"

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

npx @didcid/keymaster add-dmail-attachment "$DMAIL_DID" "$FILE_PATH"

FILENAME=$(basename "$FILE_PATH")
echo "Attached '$FILENAME' to $DMAIL_DID"

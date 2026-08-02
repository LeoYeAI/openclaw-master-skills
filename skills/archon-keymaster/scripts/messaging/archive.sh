#!/bin/bash
# Archive a dmail (removes from inbox)
# Usage: archive.sh <dmail-did>

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

# Set archive tag (removes inbox, unread)
npx @didcid/keymaster file-dmail "$DMAIL_DID" "archive"

echo "Archived: $DMAIL_DID"

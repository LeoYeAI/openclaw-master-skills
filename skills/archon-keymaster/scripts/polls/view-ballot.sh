#!/bin/bash
# View ballot details

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <ballot-did>"
    echo ""
    echo "View details of a ballot"
    echo ""
    echo "Shows the poll DID, voter DID, and vote (if you have permission to decrypt)."
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaier..."
    exit 1
fi

BALLOT_DID=$1

# Ensure environment is loaded
if [ -z "$ARCHON_PASSPHRASE" ]; then
    if [ -f ~/.archon.env ]; then
        source ~/.archon.env
    else
        echo "Error: ARCHON_PASSPHRASE not set. Run create-id.sh first."
        exit 1
    fi
fi

# Set wallet path
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

# View ballot
npx @didcid/keymaster view-ballot "$BALLOT_DID"

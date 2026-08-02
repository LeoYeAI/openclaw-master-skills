#!/bin/bash
# Remove poll results from publication

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <poll-did>"
    echo ""
    echo "Remove published results from a poll"
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaier..."
    exit 1
fi

POLL_DID=$1

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

# Unpublish
echo "Removing poll results..."
npx @didcid/keymaster unpublish-poll "$POLL_DID"

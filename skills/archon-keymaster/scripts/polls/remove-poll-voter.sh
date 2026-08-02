#!/bin/bash
# Remove a voter from a poll

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <poll-did> <voter-did>"
    echo ""
    echo "Remove a voter from a poll's eligible voter list"
    echo ""
    echo "Arguments:"
    echo "  poll-did   DID of the poll"
    echo "  voter-did  DID of the voter to remove"
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaier... did:cid:bagaaierb..."
    exit 1
fi

POLL_DID=$1
VOTER_DID=$2

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

# Remove voter
echo "Removing voter from poll..."
npx @didcid/keymaster remove-poll-voter "$POLL_DID" "$VOTER_DID"

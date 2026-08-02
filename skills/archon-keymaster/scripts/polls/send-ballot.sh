#!/bin/bash
# Send a ballot to the poll owner

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <ballot-did> <poll-did>"
    echo ""
    echo "Send your ballot to the poll owner for counting"
    echo ""
    echo "Arguments:"
    echo "  ballot-did  DID of your ballot (from vote-poll.sh)"
    echo "  poll-did    DID of the poll"
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaierballot... did:cid:bagaaierpoll..."
    exit 1
fi

BALLOT_DID=$1
POLL_DID=$2

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

# Send ballot
echo "Sending ballot to poll owner..."
npx @didcid/keymaster send-ballot "$BALLOT_DID" "$POLL_DID"

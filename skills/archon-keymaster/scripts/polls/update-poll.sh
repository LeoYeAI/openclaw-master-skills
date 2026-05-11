#!/bin/bash
# Add a ballot to the poll (poll owner only)

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <ballot-did>"
    echo ""
    echo "Add a received ballot to the poll tally (poll owner only)"
    echo ""
    echo "This is used by the poll owner to count ballots received from voters."
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaierballot..."
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

# Update poll with ballot
echo "Adding ballot to poll..."
npx @didcid/keymaster update-poll "$BALLOT_DID"

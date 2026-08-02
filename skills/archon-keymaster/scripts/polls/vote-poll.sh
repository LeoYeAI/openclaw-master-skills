#!/bin/bash
# Vote in a poll

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <poll-did> <vote-index>"
    echo ""
    echo "Cast a vote in a poll"
    echo ""
    echo "Arguments:"
    echo "  poll-did     DID of the poll"
    echo "  vote-index   Vote number: 0 = spoil, 1-N = option index"
    echo ""
    echo "Use view-poll.sh first to see available options and their indices."
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaier... 1    # Vote for first option"
    echo "  $0 did:cid:bagaaier... 0    # Spoil ballot"
    exit 1
fi

POLL_DID=$1
VOTE=$2

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

# Vote
echo "Casting vote in poll..."
npx @didcid/keymaster vote-poll "$POLL_DID" "$VOTE"

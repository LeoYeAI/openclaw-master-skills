#!/bin/bash
# Get details of an Archon group
# Usage: ./get-group.sh <group-did-or-alias>

set -e

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

if [ -z "$1" ]; then
    echo "Usage: $0 <group-did-or-alias>"
    echo ""
    echo "Examples:"
    echo "  $0 research-team"
    echo "  $0 did:cid:bagaaiera..."
    exit 1
fi

GROUP="$1"

echo "Group details for: $GROUP"
echo ""

npx @didcid/keymaster get-group "$GROUP"

#!/bin/bash
# Create an authorization challenge from a credential DID
# Usage: create-challenge-cc.sh <credential-did> [--alias <alias>]
# Example: create-challenge-cc.sh did:cid:bagaaiera...

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <credential-did> [--alias <alias>]"
    echo "Example: $0 did:cid:bagaaiera..."
    exit 1
fi

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

# Create challenge from credential DID
npx @didcid/keymaster create-challenge-cc "$@"

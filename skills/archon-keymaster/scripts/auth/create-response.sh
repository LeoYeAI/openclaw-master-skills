#!/bin/bash
# Create a response to an authorization challenge
# Usage: create-response.sh <challenge>
# Example: create-response.sh '{"challenge":"...","credentialSubject":{...}}'

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <challenge>"
    echo "Example: $0 '{\"challenge\":\"...\",\"credentialSubject\":{...}}'"
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

CHALLENGE="$1"

# Create response to challenge
npx @didcid/keymaster create-response "$CHALLENGE"

#!/bin/bash
# Get a credential by DID or alias

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <credential-did-or-alias>"
    echo ""
    echo "Retrieve a credential by its DID or alias"
    echo ""
    echo "Examples:"
    echo "  $0 my-proof-of-human"
    echo "  $0 did:cid:bagaaiera..."
    exit 1
fi

CREDENTIAL_DID=$1

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

# Get credential
npx @didcid/keymaster get-credential "$CREDENTIAL_DID"

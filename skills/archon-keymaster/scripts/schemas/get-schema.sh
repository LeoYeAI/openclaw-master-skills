#!/bin/bash
# Get a schema by DID or alias

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <schema-did-or-alias>"
    echo ""
    echo "Retrieve a schema by its DID or alias"
    echo ""
    echo "Examples:"
    echo "  $0 proof-of-human-schema"
    echo "  $0 did:cid:bagaaiera4yl4xi..."
    exit 1
fi

SCHEMA_DID=$1

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

# Get schema
npx @didcid/keymaster get-schema "$SCHEMA_DID"

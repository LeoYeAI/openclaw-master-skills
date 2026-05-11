#!/bin/bash
# Accept and save a verifiable credential

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <credential-did-or-alias> [options]"
    echo ""
    echo "Accept and save a verifiable credential issued to you"
    echo ""
    echo "Options:"
    echo "  --registry TEXT  Registry URL (default: hyperswarm)"
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaiera..."
    exit 1
fi

CREDENTIAL_DID=$1
shift

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

# Accept credential
echo "Accepting credential $CREDENTIAL_DID..."
npx @didcid/keymaster accept-credential "$CREDENTIAL_DID" "$@"

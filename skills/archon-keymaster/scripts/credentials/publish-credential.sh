#!/bin/bash
# Publish a credential to your DID manifest (makes it publicly visible)

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <credential-did-or-alias>"
    echo ""
    echo "Publish the existence of a credential to your DID manifest"
    echo "This makes the credential publicly visible in your manifest"
    echo ""
    echo "Example:"
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

# Publish credential
echo "Publishing credential $CREDENTIAL_DID to manifest..."
npx @didcid/keymaster publish-credential "$CREDENTIAL_DID"

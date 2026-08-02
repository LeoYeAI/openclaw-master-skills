#!/bin/bash
# Revoke a verifiable credential you issued

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <credential-did-or-alias>"
    echo ""
    echo "Revoke a verifiable credential that you previously issued"
    echo "This invalidates the credential"
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

# Revoke credential
echo "Revoking credential $CREDENTIAL_DID..."
npx @didcid/keymaster revoke-credential "$CREDENTIAL_DID"

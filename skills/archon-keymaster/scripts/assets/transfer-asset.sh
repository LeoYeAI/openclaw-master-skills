#!/bin/bash
# Transfer an asset to another DID
# Usage: transfer-asset.sh <asset-did> <recipient-did>
# Example: transfer-asset.sh did:cid:bagaaiera... did:cid:bagaaierat...

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

if [ $# -lt 2 ]; then
    echo "Usage: $0 <asset-did> <recipient-did>"
    echo "Example: $0 did:cid:bagaaiera... did:cid:bagaaierat..."
    exit 1
fi

ASSET_DID="$1"
RECIPIENT_DID="$2"

# Transfer asset
npx @didcid/keymaster transfer-asset "$ASSET_DID" "$RECIPIENT_DID"

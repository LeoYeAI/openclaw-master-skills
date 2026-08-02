#!/bin/bash
# Get an asset and format as JSON
# Usage: get-asset-json.sh <asset-did>
# Example: get-asset-json.sh did:cid:bagaaiera...

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

if [ $# -lt 1 ]; then
    echo "Usage: $0 <asset-did>"
    echo "Example: $0 did:cid:bagaaiera..."
    exit 1
fi

ASSET_DID="$1"

# Get asset as JSON
npx @didcid/keymaster get-asset-json "$ASSET_DID"

#!/bin/bash
# Update an existing asset
# Usage: update-asset.sh <asset-did> <json-data>
# Example: update-asset.sh did:cid:bagaaiera... '{"type":"document","updated":true}'

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
    echo "Usage: $0 <asset-did> <json-data>"
    echo "Example: $0 did:cid:bagaaiera... '{\"type\":\"document\",\"updated\":true}'"
    exit 1
fi

ASSET_DID="$1"
JSON_DATA="$2"

# Update asset
npx @didcid/keymaster update-asset "$ASSET_DID" "$JSON_DATA"

#!/bin/bash
# Update an asset with new image data
# Usage: update-asset-image.sh <asset-did> <image-path>
# Example: update-asset-image.sh did:cid:bagaaiera... avatar.png

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
    echo "Usage: $0 <asset-did> <image-path>"
    echo "Example: $0 did:cid:bagaaiera... avatar.png"
    exit 1
fi

ASSET_DID="$1"
IMAGE_PATH="$2"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: File '$IMAGE_PATH' not found"
    exit 1
fi

# Update asset image
npx @didcid/keymaster update-asset-image "$ASSET_DID" "$IMAGE_PATH"

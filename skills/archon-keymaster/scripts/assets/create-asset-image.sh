#!/bin/bash
# Create a new asset from an image file
# Usage: create-asset-image.sh <image-path>
# Example: create-asset-image.sh avatar.png

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
    echo "Usage: $0 <image-path>"
    echo "Example: $0 avatar.png"
    exit 1
fi

IMAGE_PATH="$1"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: File '$IMAGE_PATH' not found"
    exit 1
fi

# Create asset from image
npx @didcid/keymaster create-asset-image "$IMAGE_PATH"

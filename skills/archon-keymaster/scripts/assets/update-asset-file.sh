#!/bin/bash
# Update an asset with new file data
# Usage: update-asset-file.sh <asset-did> <file-path>
# Example: update-asset-file.sh did:cid:bagaaiera... document.pdf

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
    echo "Usage: $0 <asset-did> <file-path>"
    echo "Example: $0 did:cid:bagaaiera... document.pdf"
    exit 1
fi

ASSET_DID="$1"
FILE_PATH="$2"

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File '$FILE_PATH' not found"
    exit 1
fi

# Update asset file
npx @didcid/keymaster update-asset-file "$ASSET_DID" "$FILE_PATH"

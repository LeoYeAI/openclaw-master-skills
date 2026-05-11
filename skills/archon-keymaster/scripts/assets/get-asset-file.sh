#!/bin/bash
# Get a file asset and save it to disk
# Usage: get-asset-file.sh <asset-did> [output-path]
# Example: get-asset-file.sh did:cid:bagaaiera... ./downloaded.pdf

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
    echo "Usage: $0 <asset-did> [output-path]"
    echo "Example: $0 did:cid:bagaaiera... ./document.pdf"
    exit 1
fi

ASSET_DID="$1"
OUTPUT_PATH="$2"

# Get asset file
if [ -n "$OUTPUT_PATH" ]; then
    npx @didcid/keymaster get-asset-file "$ASSET_DID" "$OUTPUT_PATH"
else
    npx @didcid/keymaster get-asset-file "$ASSET_DID"
fi

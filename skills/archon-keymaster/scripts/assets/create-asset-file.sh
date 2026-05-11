#!/bin/bash
# Create a new asset from a file
# Usage: create-asset-file.sh <file-path>
# Example: create-asset-file.sh document.pdf

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
    echo "Usage: $0 <file-path>"
    echo "Example: $0 document.pdf"
    exit 1
fi

FILE_PATH="$1"

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File '$FILE_PATH' not found"
    exit 1
fi

# Create asset from file
npx @didcid/keymaster create-asset-file "$FILE_PATH"

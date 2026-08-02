#!/bin/bash
# Create a new asset from JSON data
# Usage: create-asset.sh <json-data>
# Example: create-asset.sh '{"type":"document","title":"My Doc","content":"..."}'

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
    echo "Usage: $0 <json-data>"
    echo "Example: $0 '{\"type\":\"document\",\"title\":\"My Doc\"}'"
    exit 1
fi

JSON_DATA="$1"

# Create asset
npx @didcid/keymaster create-asset "$JSON_DATA"

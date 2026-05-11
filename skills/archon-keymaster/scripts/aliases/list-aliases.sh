#!/bin/bash
# List all alias → DID mappings

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

echo "=== Your DID Aliases ==="
echo ""

npx @didcid/keymaster list-aliases

echo ""
echo "Add alias: ./add-alias.sh <alias> <did>"
echo "Remove alias: ./remove-alias.sh <alias>"
echo "Resolve: ./resolve-did.sh <alias>"

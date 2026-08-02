#!/bin/bash
# Switch active DID (for multi-DID setups)
# Usage: ./switch-id.sh <did-name>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <did-name>"
    echo ""
    echo "Available DIDs:"
    "$(dirname "$0")/list-ids.sh"
    exit 1
fi

DID_NAME="$1"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

# Require ARCHON_WALLET_PATH
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

# Check wallet exists
if [ ! -f "$ARCHON_WALLET_PATH" ]; then
    echo "ERROR: No wallet found at $ARCHON_WALLET_PATH"
    exit 1
fi

echo "=== Switching Active DID ==="
echo ""
echo "Target: $DID_NAME"
echo ""

# Switch active DID (keymaster validates the name exists)
npx @didcid/keymaster use-id "$DID_NAME"

echo ""
echo "✓ Active DID: $DID_NAME"
echo ""
echo "Note: This updates the wallet. To verify:"
echo "  npx @didcid/keymaster list-ids"

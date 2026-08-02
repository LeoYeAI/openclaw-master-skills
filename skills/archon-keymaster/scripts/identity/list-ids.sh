#!/bin/bash
# List all DIDs in your wallet

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    echo "Run ./scripts/identity/create-id.sh first"
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

echo "=== Your Archon DIDs ==="
echo ""

npx @didcid/keymaster list-ids

echo ""
echo "Switch active DID:"
echo "  ./scripts/identity/switch-id.sh <did-name>"

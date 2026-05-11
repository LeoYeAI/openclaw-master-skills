#!/bin/bash
# Create an additional DID in your existing wallet
# Usage: ./create-additional-id.sh <did-name>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <did-name>"
    echo ""
    echo "Examples:"
    echo "  $0 pseudonym"
    echo "  $0 work-persona"
    echo "  $0 bot-identity"
    exit 1
fi

DID_NAME="$1"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    echo ""
    echo "Run ./scripts/identity/create-id.sh first to set up your environment"
    exit 1
fi

# Require ARCHON_WALLET_PATH
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

# Check if wallet exists
if [ ! -f "$ARCHON_WALLET_PATH" ]; then
    echo "ERROR: No wallet found at $ARCHON_WALLET_PATH"
    echo ""
    echo "Create your first identity with:"
    echo "  ./scripts/identity/create-id.sh"
    exit 1
fi

echo "=== Creating Additional DID ==="
echo ""
echo "Name: $DID_NAME"
echo "Wallet: $ARCHON_WALLET_PATH"
echo ""

npx @didcid/keymaster create-id "$DID_NAME"

echo ""
echo "✓ DID '$DID_NAME' created"
echo ""
echo "List all DIDs:"
echo "  ./scripts/identity/list-ids.sh"
echo ""
echo "Switch to this DID:"
echo "  ./scripts/identity/switch-id.sh $DID_NAME"

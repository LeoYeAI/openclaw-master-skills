#!/bin/bash
# Add a member to an Archon group
# Usage: ./add-member.sh <group-did-or-alias> <member-did-or-alias>

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

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <group> <member>"
    echo ""
    echo "Examples:"
    echo "  $0 research-team did:cid:bagaaiera..."
    echo "  $0 did:cid:group... alice"
    exit 1
fi

GROUP="$1"
MEMBER="$2"

echo "Adding member to group..."
echo "  Group:  $GROUP"
echo "  Member: $MEMBER"

npx @didcid/keymaster add-group-member "$GROUP" "$MEMBER"

echo ""
echo "✓ Member added to group"

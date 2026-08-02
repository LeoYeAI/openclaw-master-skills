#!/bin/bash
# Test if a DID is a member of a group
# Usage: ./test-member.sh <group-did-or-alias> [member-did-or-alias]
# If member is omitted, tests current identity

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

if [ -z "$1" ]; then
    echo "Usage: $0 <group> [member]"
    echo ""
    echo "If member is omitted, tests current identity."
    echo ""
    echo "Examples:"
    echo "  $0 research-team"
    echo "  $0 research-team alice"
    echo "  $0 did:cid:group... did:cid:member..."
    exit 1
fi

GROUP="$1"
MEMBER="${2:-}"

if [ -z "$MEMBER" ]; then
    echo "Testing if current identity is in group: $GROUP"
else
    echo "Testing membership..."
    echo "  Group:  $GROUP"
    echo "  Member: $MEMBER"
fi
echo ""

if [ -n "$MEMBER" ]; then
    npx @didcid/keymaster test-group "$GROUP" "$MEMBER"
else
    npx @didcid/keymaster test-group "$GROUP"
fi

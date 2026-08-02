#!/bin/bash
# Add a friendly alias for a DID
# Usage: ./add-alias.sh <alias> <did>

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <alias> <did>"
    echo ""
    echo "Examples:"
    echo "  $0 alice did:cid:bagaaiera..."
    echo "  $0 proof-of-human-schema did:cid:bagaaiera4yl4xi..."
    echo "  $0 backup-vault did:cid:bagaaierab..."
    exit 1
fi

ALIAS="$1"
DID="$2"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    echo "Run archon-id skill first to set up your environment"
    exit 1
fi

# Add alias
npx @didcid/keymaster add-alias "$ALIAS" "$DID"

echo ""
echo "✓ Alias '$ALIAS' added for DID: $DID"
echo ""
echo "You can now use '$ALIAS' in place of the full DID in Keymaster commands."

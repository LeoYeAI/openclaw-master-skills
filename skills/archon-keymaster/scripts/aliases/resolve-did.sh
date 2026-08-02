#!/bin/bash
# Resolve an alias to its DID (or pass through a DID unchanged)
# Usage: ./resolve-did.sh <alias-or-did>

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <alias-or-did>"
    echo ""
    echo "Examples:"
    echo "  $0 alice"
    echo "  $0 did:cid:bagaaiera..."
    exit 1
fi

ALIAS_OR_DID="$1"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

# Resolve (works with both aliases and DIDs)
npx @didcid/keymaster resolve-did "$ALIAS_OR_DID"

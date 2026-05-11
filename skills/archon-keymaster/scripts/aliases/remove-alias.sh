#!/bin/bash
# Remove an alias mapping
# Usage: ./remove-alias.sh <alias>

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <alias>"
    echo ""
    echo "Examples:"
    echo "  $0 alice"
    echo "  $0 old-schema"
    exit 1
fi

ALIAS="$1"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

# Remove alias
npx @didcid/keymaster remove-alias "$ALIAS"

echo ""
echo "✓ Alias '$ALIAS' removed"

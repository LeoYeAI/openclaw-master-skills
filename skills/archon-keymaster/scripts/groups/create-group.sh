#!/bin/bash
# Create a new Archon group and auto-alias it by name
# Usage: ./create-group.sh <group-name>

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
    echo "Usage: $0 <group-name>"
    echo ""
    echo "Creates a group and automatically aliases it by name."
    echo ""
    echo "Example: $0 research-team"
    exit 1
fi

GROUP_NAME="$1"

echo "Creating group: $GROUP_NAME"

# Create the group with auto-alias
npx @didcid/keymaster create-group "$GROUP_NAME" --alias "$GROUP_NAME"

echo ""
echo "✓ Group '$GROUP_NAME' created and aliased"
echo ""
echo "Next steps:"
echo "  Add members: ./scripts/groups/add-member.sh $GROUP_NAME <member-did>"
echo "  View group:  ./scripts/groups/get-group.sh $GROUP_NAME"
echo "  List groups: ./scripts/groups/list-groups.sh"

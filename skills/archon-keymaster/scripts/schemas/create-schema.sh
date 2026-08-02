#!/bin/bash
# Create a verifiable credential schema from a JSON file

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <schema-file.json> [options]"
    echo ""
    echo "Create a verifiable credential schema"
    echo ""
    echo "Options:"
    echo "  --owned          Mark schema as owned by creator (default: true)"
    echo "  --registry TEXT  Registry URL (default: hyperswarm)"
    echo ""
    echo "Example schema file format:"
    echo '{'
    echo '  "name": "proof-of-human",'
    echo '  "description": "Verifies human status",'
    echo '  "properties": {'
    echo '    "credence": { "type": "number", "minimum": 0, "maximum": 1 }'
    echo '  },'
    echo '  "required": ["credence"]'
    echo '}'
    exit 1
fi

SCHEMA_FILE=$1
shift

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Error: Schema file not found: $SCHEMA_FILE"
    exit 1
fi

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

# Create schema
echo "Creating schema from $SCHEMA_FILE..."
npx @didcid/keymaster create-schema "$SCHEMA_FILE" "$@"

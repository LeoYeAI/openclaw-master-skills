#!/bin/bash
# Create a poll from a JSON file

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <poll-file.json> [options]"
    echo ""
    echo "Create a poll from a JSON template file"
    echo ""
    echo "Options:"
    echo "  --alias TEXT     DID alias"
    echo "  --registry TEXT  Registry URL (default: hyperswarm)"
    echo ""
    echo "Generate a template with: create-poll-template.sh > poll.json"
    echo ""
    echo "Template structure (v2):"
    echo '  {'
    echo '    "version": 2,'
    echo '    "name": "poll-name",'
    echo '    "description": "What is this poll about?",'
    echo '    "options": ["yes", "no", "abstain"],'
    echo '    "deadline": "2026-03-01T00:00:00.000Z"'
    echo '  }'
    echo ""
    echo "After creating the poll, add voters with add-poll-voter.sh"
    exit 1
fi

POLL_FILE=$1
shift

if [ ! -f "$POLL_FILE" ]; then
    echo "Error: Poll file not found: $POLL_FILE"
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

# Create poll
echo "Creating poll from $POLL_FILE..."
npx @didcid/keymaster create-poll "$POLL_FILE" "$@"

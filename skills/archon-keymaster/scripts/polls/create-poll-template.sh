#!/bin/bash
# Generate a poll template JSON

set -e

echo "Generating poll template..." >&2

# Ensure environment is loaded
if [ -z "$ARCHON_PASSPHRASE" ]; then
    if [ -f ~/.archon.env ]; then
        source ~/.archon.env
    else
        echo "Error: ARCHON_PASSPHRASE not set. Run create-id.sh first." >&2
        exit 1
    fi
fi

# Set wallet path
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env" >&2
    exit 1
fi

# Generate template
# Template structure (v2):
# {
#   "version": 2,
#   "name": "poll-name",
#   "description": "What is this poll about?",
#   "options": ["yes", "no", "abstain"],
#   "deadline": "2026-03-01T00:00:00.000Z"
# }
npx @didcid/keymaster create-poll-template

#!/bin/bash
# Decrypt an encrypted message DID
# Usage: ./decrypt-message.sh <encrypted-did>

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <encrypted-did>"
    echo ""
    echo "Example:"
    echo "  $0 did:cid:bagaaiera..."
    exit 1
fi

ENCRYPTED_DID="$1"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

echo "Decrypting message..."
echo ""

# Decrypt
DECRYPTED=$(npx @didcid/keymaster decrypt-did "$ENCRYPTED_DID")

echo "✓ Message decrypted"
echo ""
echo "Message:"
echo "$DECRYPTED"

#!/bin/bash
# Encrypt a message for a specific DID
# Usage: ./encrypt-message.sh <message> <recipient-name-or-did>

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <message> <recipient-name-or-did>"
    echo ""
    echo "Examples:"
    echo "  $0 'Secret meeting at 3pm' alice"
    echo "  $0 'Confidential info' did:cid:bagaaiera..."
    exit 1
fi

MESSAGE="$1"
RECIPIENT="$2"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    echo "Run archon-id skill first"
    exit 1
fi

# Resolve recipient name to DID if needed (suppress verbose output)
RECIPIENT_DID=$(npx @didcid/keymaster resolve-did "$RECIPIENT" 2>/dev/null | head -1 || echo "$RECIPIENT")

# If resolution gave us JSON, just use the original input
if [[ "$RECIPIENT_DID" == "{"* ]]; then
    RECIPIENT_DID="$RECIPIENT"
fi

echo "Encrypting message for: $RECIPIENT_DID"
echo ""

# Encrypt message
ENCRYPTED_DID=$(npx @didcid/keymaster encrypt-message "$MESSAGE" "$RECIPIENT_DID" 2>/dev/null | head -1)

echo "✓ Message encrypted"
echo ""
echo "Encrypted DID:"
echo "$ENCRYPTED_DID"
echo ""
echo "Send this DID to the recipient. Only they can decrypt it."
echo ""
echo "Recipient decrypts with:"
echo "  ./decrypt-message.sh $ENCRYPTED_DID"

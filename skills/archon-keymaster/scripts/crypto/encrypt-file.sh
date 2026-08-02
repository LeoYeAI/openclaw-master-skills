#!/bin/bash
# Encrypt a file for a specific DID
# Usage: ./encrypt-file.sh <input-file> <recipient-name-or-did>

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <input-file> <recipient-name-or-did>"
    echo ""
    echo "Examples:"
    echo "  $0 secret.pdf alice"
    echo "  $0 document.txt bob"
    echo "  $0 data.csv did:cid:bagaaiera..."
    echo ""
    echo "Note: Returns an encrypted DID. Content is stored on-chain/IPFS."
    exit 1
fi

INPUT_FILE="$1"
RECIPIENT="$2"

# Check input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

# Resolve recipient name to DID if needed (suppress verbose output)
RECIPIENT_DID=$(npx @didcid/keymaster resolve-did "$RECIPIENT" 2>/dev/null | head -1 || echo "$RECIPIENT")

# If resolution gave us JSON, just use the original input
if [[ "$RECIPIENT_DID" == "{"* ]]; then
    RECIPIENT_DID="$RECIPIENT"
fi

echo "Encrypting: $INPUT_FILE"
echo "For: $RECIPIENT_DID"
echo ""

# Encrypt file
ENCRYPTED_DID=$(npx @didcid/keymaster encrypt-file "$INPUT_FILE" "$RECIPIENT_DID" 2>/dev/null | head -1)

echo "✓ File encrypted"
echo ""
echo "Encrypted DID:"
echo "$ENCRYPTED_DID"
echo ""
echo "Send this DID to the recipient. Only they can decrypt it."
echo "Content is stored on-chain/IPFS, referenced by this DID."
echo ""
echo "Recipient decrypts with:"
echo "  ./decrypt-message.sh $ENCRYPTED_DID > <output-filename>"

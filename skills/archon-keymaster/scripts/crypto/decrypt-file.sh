#!/bin/bash
# Decrypt an encrypted DID to a file
# Usage: ./decrypt-file.sh <encrypted-did> <output-file>

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <encrypted-did> <output-file>"
    echo ""
    echo "Examples:"
    echo "  $0 did:cid:bagaaiera... secret.pdf"
    echo "  $0 did:cid:bagaaiera... document.txt"
    exit 1
fi

ENCRYPTED_DID="$1"
OUTPUT_FILE="$2"

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

echo "Decrypting: $ENCRYPTED_DID"
echo "Output: $OUTPUT_FILE"
echo ""

# Decrypt (outputs to stdout, we redirect)
if npx @didcid/keymaster decrypt-did "$ENCRYPTED_DID" > "$OUTPUT_FILE" 2>&1; then
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    
    echo "✓ File decrypted"
    echo ""
    echo "Decrypted file: $OUTPUT_FILE ($FILE_SIZE)"
else
    echo "✗ Decryption failed"
    echo "Either the DID was not encrypted for you, or an error occurred."
    rm -f "$OUTPUT_FILE"
    exit 1
fi

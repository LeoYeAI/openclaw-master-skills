#!/bin/bash
# Verify a signed file
# Usage: ./verify-file.sh <file>

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <file>"
    echo ""
    echo "Examples:"
    echo "  $0 manifest.json"
    echo "  $0 contract.json"
    exit 1
fi

FILE="$1"

# Check file exists
if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE"
    exit 1
fi

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

echo "Verifying: $FILE"
echo ""

# Verify file
if npx @didcid/keymaster verify-file "$FILE" 2>&1 | tee /tmp/verify-output.txt; then
    echo ""
    echo "✓ Signature valid"
    
    # Try to extract signer info from file
    if command -v jq >/dev/null 2>&1; then
        SIGNER=$(jq -r '.proof.verificationMethod // .issuer // "unknown"' "$FILE" 2>/dev/null)
        CREATED=$(jq -r '.proof.created // "unknown"' "$FILE" 2>/dev/null)
        
        if [ "$SIGNER" != "unknown" ]; then
            echo "Signed by: $SIGNER"
        fi
        if [ "$CREATED" != "unknown" ]; then
            echo "Signed at: $CREATED"
        fi
    fi
else
    echo ""
    echo "✗ Signature verification FAILED"
    echo ""
    echo "This file may have been tampered with, or the signature is invalid."
    exit 1
fi

rm -f /tmp/verify-output.txt

#!/bin/bash
# Sign a JSON file with your DID (modifies file in place)
# Usage: ./sign-file.sh <file>

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <file>"
    echo ""
    echo "Examples:"
    echo "  $0 manifest.json"
    echo "  $0 contract.json"
    echo ""
    echo "Note: File must be valid JSON. Signature is added in place."
    exit 1
fi

FILE="$1"

# Check file exists
if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE"
    exit 1
fi

# Check it's JSON
if ! jq empty "$FILE" 2>/dev/null; then
    echo "ERROR: File is not valid JSON"
    exit 1
fi

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

echo "Signing: $FILE"
echo ""

# Create temp file for safety
TEMP_FILE="${FILE}.signing.tmp"

# Sign file (outputs to stdout)
if npx @didcid/keymaster sign-file "$FILE" > "$TEMP_FILE" 2>&1; then
    # Replace original with signed version
    mv "$TEMP_FILE" "$FILE"
    echo "✓ File signed (signature added in place)"
    echo ""
    echo "Others can verify with:"
    echo "  ./verify-file.sh $FILE"
else
    echo "✗ Signing failed"
    rm -f "$TEMP_FILE"
    exit 1
fi

#!/bin/bash
# Bind a credential to a subject DID (creates credential template)

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <schema-did-or-alias> <subject-did-or-alias>"
    echo ""
    echo "Create a bound credential template for a subject"
    echo "This creates a credential file that can be filled in and issued"
    echo ""
    echo "Examples:"
    echo "  $0 proof-of-human-schema alice"
    echo "  $0 did:cid:bagaaiera... did:cid:bagaaierb..."
    echo ""
    echo "Output: Saves bound credential JSON to <subject-did>.BOUND.json"
    exit 1
fi

SCHEMA_DID=$1
SUBJECT_DID=$2

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

# Resolve subject DID to get actual DID (in case it's an alias)
SUBJECT_RESOLVED=$(npx @didcid/keymaster get-alias "$SUBJECT_DID" 2>/dev/null || echo "$SUBJECT_DID")

# Bind credential
echo "Binding credential for subject $SUBJECT_DID using schema $SCHEMA_DID..."

# Generate output filename based on subject DID
SUBJECT_SHORT=$(echo "$SUBJECT_RESOLVED" | sed 's/did:cid://')
OUTPUT_FILE="${SUBJECT_SHORT}.BOUND.json"

# Run bind command and save to file
npx @didcid/keymaster bind-credential "$SCHEMA_DID" "$SUBJECT_DID" | tee "$OUTPUT_FILE"

echo ""
echo "Saved bound credential to: $OUTPUT_FILE"
echo "Edit this file to fill in the credentialSubject data, then run:"
echo "  ./scripts/credentials/issue-credential.sh $OUTPUT_FILE"

#!/usr/bin/env bash
set -euo pipefail

# VIA Mandate — Quick Start Example
#
# Before running, set your credentials:
#   export VIA_API_KEY="your-api-key"
#   export VIA_SIGNATURE_SECRET="your-signing-secret"
# Optional override:
#   export VIA_API_URL="https://api.humanos.id"

SCRIPT_DIR="$(cd "$(dirname "$0")/../scripts" && pwd)"

echo "=== VIA Humanos Quick Start ==="
echo ""

# 1. Create an approval request
echo "Step 1: Creating approval request..."
RESULT=$("$SCRIPT_DIR/create-request.sh" \
  --contact "test@example.com" \
  --type "json" \
  --name "Payment Authorization" \
  --data '{"label":"amount","value":"EUR 450","type":"string"}')

echo "$RESULT" | jq .
REQUEST_ID=$(echo "$RESULT" | jq -r '.id // .requestId // empty')

if [[ -z "$REQUEST_ID" ]]; then
  echo "Failed to create request. Check your credentials."
  exit 1
fi

echo ""
echo "Request ID: $REQUEST_ID"
echo "An approval link has been sent to the contact."
echo ""

# 2. Check the status
echo "Step 2: Checking request status..."
"$SCRIPT_DIR/get-request.sh" --id "$REQUEST_ID"

echo ""
echo "=== Done ==="
echo "The contact will receive a link to approve or reject."
echo "Poll the status with: scripts/get-request.sh --id $REQUEST_ID"

#!/bin/bash
# Veto a fund proposal
# Usage: ast-veto.sh <vault_address> <proposal_id>
# Requires: AST_API_KEY env var. Optional: BANKR_KEY env var for auto-submission.

VAULT=$1; PROPOSAL_ID=$2
API_KEY="${AST_API_KEY:?Set AST_API_KEY env var}"
API_URL="${AST_API_URL:-https://agenticstreet.ai/api}"

RESULT=$(curl -s -X POST "$API_URL/funds/$VAULT/proposals/$PROPOSAL_ID/veto" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}')

# Check for API error
if echo "$RESULT" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $(echo "$RESULT" | jq -r '.error')"
  exit 1
fi

if [ -n "$BANKR_KEY" ]; then
  echo "Submitting veto via Bankr..."
  curl -s -X POST "https://api.bankr.bot/agent/submit" \
    -H "X-API-Key: $BANKR_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"transaction\": $RESULT, \"waitForConfirmation\": true}" | jq '.'
else
  echo "Veto TxData:"
  echo "$RESULT" | jq '.'
  echo "Sign and submit. See api-reference.md#submitting-transactions."
fi

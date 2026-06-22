#!/bin/bash
# Deposit USDC into an Agentic Street fund
# Usage: ast-deposit.sh <raise_address> <amount_usdc_6dec>
# Example: ast-deposit.sh 0xRaise... 5000000000
# Requires: AST_API_KEY env var. Optional: BANKR_KEY env var for auto-submission.

RAISE=$1; AMOUNT=$2
API_KEY="${AST_API_KEY:?Set AST_API_KEY env var}"
API_URL="${AST_API_URL:-https://agenticstreet.ai/api}"

# Get unsigned calldata from Agentic Street
RESULT=$(curl -s -X POST "$API_URL/funds/$RAISE/deposit" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"amount\":\"$AMOUNT\"}")

# Check for API error
if echo "$RESULT" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $(echo "$RESULT" | jq -r '.error')"
  exit 1
fi

TX1=$(echo "$RESULT" | jq -c '.[0]')
TX2=$(echo "$RESULT" | jq -c '.[1]')

if [ -n "$BANKR_KEY" ]; then
  echo "Submitting USDC approval via Bankr..."
  curl -s -X POST "https://api.bankr.bot/agent/submit" \
    -H "X-API-Key: $BANKR_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"transaction\": $TX1, \"waitForConfirmation\": true}" | jq '.'

  echo "Submitting deposit via Bankr..."
  curl -s -X POST "https://api.bankr.bot/agent/submit" \
    -H "X-API-Key: $BANKR_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"transaction\": $TX2, \"waitForConfirmation\": true}" | jq '.'
else
  echo "Transaction 1 — USDC approval:"
  echo "$TX1" | jq '.'
  echo ""
  echo "Transaction 2 — deposit:"
  echo "$TX2" | jq '.'
  echo ""
  echo "Sign and submit both in order. See api-reference.md#submitting-transactions."
fi

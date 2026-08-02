#!/usr/bin/env bash
set -euo pipefail

# lightning-pay.sh - Pay BOLT11 invoice with automatic verification
# Usage: ./lightning-pay.sh <bolt11> [id]
# Returns: {"paymentHash": "...", "paid": true/false, "preimage": "..."}

source ~/.archon.env

# Pay the invoice
result=$(npx @didcid/keymaster lightning-pay "$@")
hash=$(echo "$result" | jq -r .paymentHash)

# Verify payment settled
status=$(npx @didcid/keymaster lightning-check "$hash" "${2:-}" | jq -r .paid)

if [ "$status" = "true" ]; then
  echo "✅ Payment confirmed"
else
  echo "❌ Payment failed or pending"
  exit 1
fi

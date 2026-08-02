#!/usr/bin/env bash
set -euo pipefail

# lightning-zap.sh - Send sats via Lightning Address, DID, or alias with automatic verification
# Usage: ./lightning-zap.sh <recipient> <amount> [memo] [id]
# recipient: Lightning Address (user@domain.com), DID, or alias

source ~/.archon.env

# Send the zap
result=$(npx @didcid/keymaster lightning-zap "$@")
hash=$(echo "$result" | jq -r .paymentHash)

# Verify payment settled
status=$(npx @didcid/keymaster lightning-check "$hash" "${4:-}" | jq -r .paid)

if [ "$status" = "true" ]; then
  echo "✅ Payment confirmed"
else
  echo "❌ Payment failed or pending"
  exit 1
fi

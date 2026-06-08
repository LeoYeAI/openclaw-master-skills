#!/bin/bash
# check_balance.sh — Check wallet balances on refinORE
# Usage: check_balance.sh <api_url> <api_key>
#
# First fetches wallet address via /account/me, then checks balances.
set -euo pipefail

API_URL="${1:-${REFINORE_API_URL:-https://automine.refinore.com/api}}"
API_KEY="${2:-${REFINORE_API_KEY:-}}"

if [ -z "$API_KEY" ]; then
  echo "❌ No credentials. Set REFINORE_API_KEY"; exit 1
fi

AUTH_HEADER="x-api-key: $API_KEY"

# Step 1: Get wallet address from account info
echo "🔍 Fetching account info..."
ACCOUNT_INFO=$(curl -s "$API_URL/account/me" -H "$AUTH_HEADER")

WALLET=$(echo "$ACCOUNT_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin).get('wallet_address',''))" 2>/dev/null || echo "")

if [ -z "$WALLET" ]; then
  echo "⚠️  Could not determine wallet address. Raw response:"
  echo "$ACCOUNT_INFO" | python3 -m json.tool 2>/dev/null || echo "$ACCOUNT_INFO"
  exit 1
fi

echo "📍 Wallet address: $WALLET"

# Step 2: Check balances
echo ""
echo "💰 Balances:"
curl -s "$API_URL/wallet/balances?wallet=$WALLET" -H "$AUTH_HEADER" | python3 -m json.tool 2>/dev/null || \
  curl -s "$API_URL/wallet/balances?wallet=$WALLET" -H "$AUTH_HEADER"

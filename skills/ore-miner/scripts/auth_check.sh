#!/bin/bash
# auth_check.sh — Validate refinORE credentials
# Usage: auth_check.sh <api_url> <api_key>
# Or set REFINORE_API_URL and REFINORE_API_KEY env vars
set -euo pipefail

API_URL="${1:-${REFINORE_API_URL:-https://automine.refinore.com/api}}"
API_KEY="${2:-${REFINORE_API_KEY:-}}"

if [ -z "$API_KEY" ]; then
  echo "❌ No credentials found."
  echo "Usage: auth_check.sh <api_url> <api_key>"
  echo "   Or: REFINORE_API_KEY=rsk_... auth_check.sh"
  exit 1
fi

AUTH_HEADER="x-api-key: $API_KEY"
echo "🔑 Using API key authentication"

echo "🔍 Validating against $API_URL..."

RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/account/me" -H "$AUTH_HEADER")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
  WALLET=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('wallet_address','unknown'))" 2>/dev/null || echo "unknown")
  EMAIL=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('email','unknown'))" 2>/dev/null || echo "unknown")
  echo "✅ Authenticated!"
  echo "  Email: $EMAIL"
  echo "  Wallet: $WALLET"
else
  echo "❌ Authentication failed (HTTP $HTTP_CODE)"
  echo "$BODY"
  exit 1
fi

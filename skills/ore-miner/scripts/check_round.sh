#!/bin/bash
# check_round.sh — Get current round info + active session status from refinORE
# Usage: check_round.sh <api_url> <api_key>
set -euo pipefail

API_URL="${1:-${REFINORE_API_URL:-https://automine.refinore.com/api}}"
API_KEY="${2:-${REFINORE_API_KEY:-}}"

if [ -z "$API_KEY" ]; then
  echo "❌ No credentials. Set REFINORE_API_KEY"; exit 1
fi

AUTH_HEADER="x-api-key: $API_KEY"

echo "=== Current Round ==="
curl -s "$API_URL/rounds/current" -H "$AUTH_HEADER" | python3 -m json.tool 2>/dev/null || \
  curl -s "$API_URL/rounds/current" -H "$AUTH_HEADER"

echo ""
echo "=== Active Session ==="
curl -s "$API_URL/mining/session" -H "$AUTH_HEADER" | python3 -m json.tool 2>/dev/null || \
  curl -s "$API_URL/mining/session" -H "$AUTH_HEADER"

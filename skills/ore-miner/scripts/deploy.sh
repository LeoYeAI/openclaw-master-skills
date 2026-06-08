#!/bin/bash
# deploy.sh — Start mining with specific tile IDs via refinORE API
# Usage: deploy.sh <api_url> <api_key> <sol_amount> <tile_ids_comma_separated>
# Example: deploy.sh https://automine.refinore.com/api rsk_abc 0.005 "0,6,12,18,24"
set -euo pipefail

API_URL="${1:?Usage: deploy.sh <api_url> <api_key> <sol_amount> <tile_ids>}"
API_KEY="${2:?Missing API key}"
SOL_AMOUNT="${3:-0.005}"
TILE_IDS="${4:?Missing tile IDs (comma-separated, 0-24)}"

AUTH_HEADER="x-api-key: $API_KEY"

# Step 1: Get wallet address
echo "🔍 Fetching wallet address..."
ACCOUNT_INFO=$(curl -s "$API_URL/account/me" -H "$AUTH_HEADER")
WALLET=$(echo "$ACCOUNT_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin).get('wallet_address',''))" 2>/dev/null || echo "")

if [ -z "$WALLET" ]; then
  echo "❌ Could not get wallet address. Response:"
  echo "$ACCOUNT_INFO"
  exit 1
fi
echo "  Wallet: $WALLET"

# Convert comma-separated to JSON array
TILES_JSON=$(echo "$TILE_IDS" | python3 -c "import sys; print([int(x.strip()) for x in sys.stdin.read().split(',')])")
NUM_TILES=$(echo "$TILE_IDS" | tr ',' '\n' | wc -l)

echo "⛏️ Deploying with custom tiles on refinORE..."
echo "  SOL: $SOL_AMOUNT | Tiles: $NUM_TILES | IDs: $TILE_IDS"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/mining/start" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
    \"wallet_address\": \"$WALLET\",
    \"sol_amount\": $SOL_AMOUNT,
    \"num_squares\": $NUM_TILES,
    \"custom_tiles\": $TILES_JSON,
    \"tile_selection_mode\": \"custom\",
    \"mining_token\": \"SOL\",
    \"auto_restart\": true,
    \"frequency\": \"every_round\"
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  echo "✅ Custom tile mining started!"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
  echo "❌ Failed (HTTP $HTTP_CODE)"
  echo "$BODY"
  exit 1
fi

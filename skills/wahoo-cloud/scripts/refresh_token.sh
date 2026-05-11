#!/usr/bin/env bash
# Refresh the Wahoo access token using the refresh_token. Reads tokens from
# ~/.openclaw/secrets/wahoo_tokens.json (preferred) or env vars, and writes
# the new tokens back to the same JSON file.

set -e

TOKENS_FILE="${WAHOO_TOKENS_FILE:-$HOME/.openclaw/secrets/wahoo_tokens.json}"

if [ -z "$WAHOO_CLIENT_ID" ] || [ -z "$WAHOO_CLIENT_SECRET" ]; then
  echo "Error: WAHOO_CLIENT_ID and WAHOO_CLIENT_SECRET must be set"
  exit 1
fi

REFRESH_TOKEN="${WAHOO_REFRESH_TOKEN:-}"
if [ -z "$REFRESH_TOKEN" ] && [ -f "$TOKENS_FILE" ]; then
  REFRESH_TOKEN=$(grep -o '"refresh_token":"[^"]*' "$TOKENS_FILE" | cut -d'"' -f4)
fi

if [ -z "$REFRESH_TOKEN" ]; then
  echo "Error: no refresh_token in env or $TOKENS_FILE"
  echo "Run skills/wahoo/scripts/oauth_setup.py first"
  exit 1
fi

RESPONSE=$(curl -s -X POST https://api.wahooligan.com/oauth/token \
  -d client_id="$WAHOO_CLIENT_ID" \
  -d client_secret="$WAHOO_CLIENT_SECRET" \
  -d grant_type=refresh_token \
  -d refresh_token="$REFRESH_TOKEN")

NEW_ACCESS=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
NEW_REFRESH=$(echo "$RESPONSE" | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)
EXPIRES_IN=$(echo "$RESPONSE" | grep -o '"expires_in":[0-9]*' | cut -d':' -f2)

if [ -z "$NEW_ACCESS" ]; then
  echo "❌ Refresh failed:"
  echo "$RESPONSE"
  exit 1
fi

EXPIRES_AT=$(( $(date +%s) + ${EXPIRES_IN:-7200} ))

mkdir -p "$(dirname "$TOKENS_FILE")"
cat > "$TOKENS_FILE" <<EOF
{
  "access_token": "$NEW_ACCESS",
  "refresh_token": "$NEW_REFRESH",
  "expires_in": ${EXPIRES_IN:-7200},
  "expires_at": $EXPIRES_AT,
  "token_type": "bearer"
}
EOF
chmod 600 "$TOKENS_FILE"

echo "✅ Token refreshed → $TOKENS_FILE"
echo "   expires_at: $(date -d "@$EXPIRES_AT" 2>/dev/null || date -r "$EXPIRES_AT" 2>/dev/null || echo "$EXPIRES_AT")"

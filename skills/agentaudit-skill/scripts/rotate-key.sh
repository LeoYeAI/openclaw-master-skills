#!/usr/bin/env bash
# Rotate your AgentAudit API key
# Usage: bash scripts/rotate-key.sh
# Requires: existing API key in credentials or AGENTAUDIT_API_KEY env var

set -euo pipefail

# Dependencies
for cmd in curl jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Required dependency '$cmd' not found." >&2
    exit 1
  fi
done

REGISTRY_URL="https://www.agentaudit.dev"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_CRED_FILE="$SCRIPT_DIR/../config/credentials.json"
USER_CRED_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/agentaudit"
USER_CRED_FILE="$USER_CRED_DIR/credentials.json"

# ── Load shared helpers ──
source "$SCRIPT_DIR/_load-key.sh"
source "$SCRIPT_DIR/_curl-retry.sh"
API_KEY="$(load_api_key)"

if [ -z "$API_KEY" ]; then
  echo "❌ No API key found. Register first: bash scripts/register.sh <agent-name>" >&2
  exit 1
fi

echo "🔄 Rotating API key..."

RESPONSE=$(curl_retry -s -w "\n%{http_code}" -X POST "$REGISTRY_URL/api/keys/rotate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  NEW_KEY=$(echo "$BODY" | jq -r '.api_key')
  AGENT_NAME=$(echo "$BODY" | jq -r '.agent_name')

  if [ -z "$NEW_KEY" ] || [ "$NEW_KEY" = "null" ]; then
    echo "❌ Rotation failed — no new key in response" >&2
    echo "$BODY" >&2
    exit 1
  fi

  # Save to skill-local config
  mkdir -p "$(dirname "$SKILL_CRED_FILE")"
  ( umask 077; echo "$BODY" | jq '{api_key: .api_key, agent_name: .agent_name}' > "$SKILL_CRED_FILE" )

  # Save to user-level config (backup)
  mkdir -p "$USER_CRED_DIR"
  ( umask 077; echo "$BODY" | jq '{api_key: .api_key, agent_name: .agent_name}' > "$USER_CRED_FILE" )

  echo "✅ Key rotated successfully!"
  echo "   Agent: $AGENT_NAME"
  echo "   New key: ${NEW_KEY:0:6}...${NEW_KEY: -4}"
  echo ""
  echo "   Saved to:"
  echo "     • $SKILL_CRED_FILE"
  echo "     • $USER_CRED_FILE"

  if [ -n "${AGENTAUDIT_API_KEY:-}" ]; then
    echo ""
    echo "   ⚠️  You also have AGENTAUDIT_API_KEY set in your environment."
    echo "      Update it from the saved credentials:"
    echo "      export AGENTAUDIT_API_KEY=\"\$(jq -r .api_key $USER_CRED_FILE)\""
  fi
else
  echo "❌ Key rotation failed (HTTP $HTTP_CODE):" >&2
  echo "$BODY" >&2
  exit 1
fi

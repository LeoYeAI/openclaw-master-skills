#!/usr/bin/env bash
# Register for an API key at the AgentAudit
# Usage: bash scripts/register.sh <agent-name>
# Saves key to config/credentials.json

set -euo pipefail

# Dependencies: curl, jq
for cmd in curl jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Required dependency '$cmd' not found. Install it first." >&2
    exit 1
  fi
done

REGISTRY_URL="https://www.agentaudit.dev"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CRED_FILE="$SCRIPT_DIR/../config/credentials.json"
USER_CRED_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/agentaudit"
USER_CRED_FILE="$USER_CRED_DIR/credentials.json"

AGENT_NAME="${1:-}"
if [ -z "$AGENT_NAME" ]; then
  echo "Usage: bash scripts/register.sh <agent-name>" >&2
  echo "  agent-name: alphanumeric, dashes, underscores, dots (2-64 chars)" >&2
  exit 1
fi

# Sanitize agent name: only allow alphanumeric, dashes, underscores, dots
if ! echo "$AGENT_NAME" | grep -qE '^[a-zA-Z0-9._-]{2,64}$'; then
  echo "❌ Invalid agent name. Use only alphanumeric, dashes, underscores, dots (2-64 chars)." >&2
  exit 1
fi

# Check if already registered (check both locations)
# IMPORTANT: Validate the key against the server, not just file existence.
# Keys can become stale if the DB is reset or the key was from a different environment.
for check_file in "$CRED_FILE" "$USER_CRED_FILE"; do
  if [ -f "$check_file" ]; then
    EXISTING_KEY=$(jq -r '.api_key // empty' "$check_file" 2>/dev/null || true)
    if [ -n "$EXISTING_KEY" ]; then
      # Validate key against server (quick check)
      VALIDATE_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 \
        -H "Authorization: Bearer $EXISTING_KEY" \
        "$REGISTRY_URL/api/auth/validate" 2>/dev/null || echo "000")

      if [ "$VALIDATE_HTTP" = "200" ]; then
        echo "Already registered. Key validated against server."
        echo "  Key found in $check_file"
        # Ensure both locations have the key
        if [ "$check_file" = "$USER_CRED_FILE" ] && [ ! -f "$CRED_FILE" ]; then
          mkdir -p "$(dirname "$CRED_FILE")"
          ( umask 077; cp "$USER_CRED_FILE" "$CRED_FILE" )
          echo "  Restored skill-local copy to: $CRED_FILE"
        fi
        exit 0
      else
        echo "⚠️  Cached key in $check_file is stale (server returned $VALIDATE_HTTP). Re-registering..."
        rm -f "$CRED_FILE" "$USER_CRED_FILE"
        break
      fi
    fi
  fi
done

echo "Registering agent '$AGENT_NAME' at $REGISTRY_URL/api/register ..."

# Use jq to safely build JSON payload (prevents injection)
JSON_PAYLOAD=$(jq -n --arg name "$AGENT_NAME" '{agent_name: $name}')

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$REGISTRY_URL/api/register" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  CRED_JSON=$(echo "$BODY" | jq '{api_key: .api_key, agent_name: .agent_name}')

  # Save to skill-local config
  mkdir -p "$(dirname "$CRED_FILE")"
  ( umask 077; echo "$CRED_JSON" > "$CRED_FILE" )

  # Save to user-level config (survives skill re-installation)
  mkdir -p "$USER_CRED_DIR"
  ( umask 077; echo "$CRED_JSON" > "$USER_CRED_FILE" )

  echo "✅ Registered successfully!"
  echo "Credentials saved to:"
  echo "  • $CRED_FILE (skill-local)"
  echo "  • $USER_CRED_FILE (user backup)"
else
  echo "❌ Registration failed (HTTP $HTTP_CODE):" >&2
  echo "$BODY" >&2
  exit 1
fi

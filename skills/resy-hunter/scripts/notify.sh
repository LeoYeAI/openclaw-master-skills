#!/usr/bin/env bash
# notify.sh — Send a Telegram notification
# Usage: ./notify.sh "<message>"
#
# Pulls the bot token from OpenClaw's Telegram channel config.
# Falls back to TELEGRAM_BOT_TOKEN env var if config not found.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo '{"error": "Usage: notify.sh <message>"}' >&2
  exit 1
fi

MESSAGE="$1"

if [[ -z "${TELEGRAM_CHAT_ID:-}" ]]; then
  echo '{"error": "TELEGRAM_CHAT_ID is not set"}' >&2
  exit 1
fi
CHAT_ID="${TELEGRAM_CHAT_ID}"

# Resolve bot token: OpenClaw config → env var fallback
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"

if [[ -z "$BOT_TOKEN" ]]; then
  # Search OpenClaw config files for channels.telegram.botToken
  for cfg in \
    "$HOME/.openclaw/config.json" \
    "$HOME/.openclaw/openclaw.json" \
    "$HOME/.openclaw/gateway.json" \
    "$HOME/.config/openclaw/config.json" \
    "$HOME/.openclaw/config.yaml" \
    "$HOME/.openclaw/openclaw.yaml"; do
    if [[ -f "$cfg" ]]; then
      # Try JSON first
      if [[ "$cfg" == *.json ]]; then
        token=$(jq -r '.channels.telegram.botToken // empty' "$cfg" 2>/dev/null || true)
        if [[ -n "$token" ]]; then
          BOT_TOKEN="$token"
          break
        fi
      fi
      # Try YAML (grep-based, no yq dependency)
      if [[ "$cfg" == *.yaml || "$cfg" == *.yml ]]; then
        token=$(grep -A1 'botToken' "$cfg" 2>/dev/null | grep -oP ':\s*\K\S+' | tr -d '"'"'" || true)
        if [[ -n "$token" ]]; then
          BOT_TOKEN="$token"
          break
        fi
      fi
    fi
  done
fi

if [[ -z "$BOT_TOKEN" ]]; then
  echo '{"error": "Telegram bot token not found. Check OpenClaw config (channels.telegram.botToken) or set TELEGRAM_BOT_TOKEN."}' >&2
  exit 1
fi

response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg chat_id "$CHAT_ID" \
    --arg text "$MESSAGE" \
    '{chat_id: $chat_id, text: $text, parse_mode: "Markdown"}')")

ok=$(echo "$response" | jq -r '.ok // false')

if [[ "$ok" != "true" ]]; then
  echo "$response" | jq '{error: "Telegram send failed", details: .}' >&2
  exit 1
fi

echo "$response" | jq '{ok: true, message_id: .result.message_id}'

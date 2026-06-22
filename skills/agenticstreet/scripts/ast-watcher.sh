#!/usr/bin/env bash
# ast-watcher.sh — Agentic Street proposal watcher
# Runs via system crontab. Zero LLM tokens when idle.
# Dependencies: curl, bash (no jq needed)

set -euo pipefail

API_KEY="${AST_API_KEY:?Set AST_API_KEY}"
HOOK_TOKEN="${OPENCLAW_HOOK_TOKEN:?Set OPENCLAW_HOOK_TOKEN}"
API_URL="${AST_API_URL:-https://agenticstreet.ai/api}"
HOOK_URL="${OPENCLAW_HOOK_URL:-http://127.0.0.1:18789}"
CHANNEL="${AST_CHANNEL:-last}"

# Poll for pending events (silent exit on network error — cron retries)
RESPONSE=$(curl -sf --max-time 10 \
  -H "Authorization: Bearer $API_KEY" \
  "${API_URL}/notifications/pending" 2>/dev/null) || exit 0

# Extract count using bash pattern matching (no jq)
COUNT=$(echo "$RESPONSE" | grep -o '"count":[0-9]*' | grep -o '[0-9]*$')
[ -z "$COUNT" ] || [ "$COUNT" -eq 0 ] && exit 0

LAST_ID=$(echo "$RESPONSE" | grep -o '"lastEventId":[0-9]*' | grep -o '[0-9]*$')
[ -z "$LAST_ID" ] && exit 0

curl -sf --max-time 15 -X POST "${HOOK_URL}/hooks/agent" \
  -H "Authorization: Bearer $HOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"AGENTIC STREET ALERT: ${COUNT} pending event(s) in your vaults.\",
    \"name\": \"AgenticStreet\",
    \"sessionKey\": \"hook:agenticstreet:batch-${LAST_ID}\",
    \"wakeMode\": \"now\",
    \"deliver\": true,
    \"channel\": \"${CHANNEL}\",
    \"timeoutSeconds\": 90
  }" 2>/dev/null || true

# Acknowledge receipt (if this fails, next poll re-delivers — agent deduplicates via sessionKey)
curl -sf --max-time 5 -X POST "${API_URL}/notifications/ack" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"lastEventId\": $LAST_ID}" 2>/dev/null || true

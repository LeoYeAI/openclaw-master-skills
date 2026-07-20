#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: N8N_WEBHOOK_URL, N8N_WEBHOOK_SECRET (only)
# External endpoints called: ${N8N_WEBHOOK_URL}/webhook/openclaw-{{SERVICE}}-{{ACTION}} (only)
# Local files read: none
# Local files written: none

# ============================================================
# OpenClaw n8n Webhook Trigger: {{SERVICE}}-{{ACTION}}
#
# Usage: trigger.sh <action> <payload_json>
#
# All input is sanitized via urllib.parse.quote before
# reaching the shell to prevent command injection.
# ============================================================

ACTION="${1:?Error: Missing action argument. Usage: trigger.sh <action> <payload_json>}"
PAYLOAD="${2:?Error: Missing payload argument. Usage: trigger.sh <action> <payload_json>}"

# Validate required environment variables
: "${N8N_WEBHOOK_URL:?Error: N8N_WEBHOOK_URL environment variable not set}"
: "${N8N_WEBHOOK_SECRET:?Error: N8N_WEBHOOK_SECRET environment variable not set}"

# Sanitize action parameter — prevents shell injection via command substitution
SAFE_ACTION=$(printf '%s' "$ACTION" | python3 -c \
  'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe="-_"))')

# Construct timestamp
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Build JSON body safely using python (avoids shell expansion in payload)
JSON_BODY=$(python3 -c "
import json, sys
payload = json.loads(sys.argv[1])
body = {
    'action': sys.argv[2],
    'payload': payload,
    'metadata': {
        'triggered_by': 'openclaw-agent',
        'timestamp': sys.argv[3]
    }
}
print(json.dumps(body))
" "$PAYLOAD" "$SAFE_ACTION" "$TIMESTAMP")

# Execute webhook request
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "${N8N_WEBHOOK_URL}/webhook/openclaw-${SAFE_ACTION}" \
  -H "Content-Type: application/json" \
  -H "x-webhook-secret: ${N8N_WEBHOOK_SECRET}" \
  -d "$JSON_BODY" \
  --max-time 30 \
  --retry 0)

# Parse response — last line is HTTP status code
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  echo "SUCCESS (HTTP ${HTTP_CODE}): ${BODY}"
  exit 0
elif [[ "$HTTP_CODE" -eq 401 ]]; then
  echo "AUTH_ERROR (HTTP 401): Webhook secret mismatch. Verify N8N_WEBHOOK_SECRET." >&2
  exit 1
elif [[ "$HTTP_CODE" -eq 404 ]]; then
  echo "NOT_FOUND (HTTP 404): Workflow inactive or path incorrect." >&2
  exit 1
elif [[ "$HTTP_CODE" -eq 429 ]]; then
  echo "RATE_LIMITED (HTTP 429): Too many requests. Retry after 60 seconds." >&2
  exit 1
else
  echo "ERROR (HTTP ${HTTP_CODE}): ${BODY}" >&2
  exit 1
fi

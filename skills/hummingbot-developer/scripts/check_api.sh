#!/bin/bash
# check_api.sh — Check if Hummingbot API is running
# Shared script (same interface as lp-agent/scripts/check_api.sh)
# Usage: bash check_api.sh [--json]

JSON=false
for arg in "$@"; do
  [ "$arg" = "--json" ] && JSON=true
done

API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"

if curl -s --max-time 3 "$API_URL/health" &>/dev/null; then
  RUNNING=true
  DETAIL=$(curl -s --max-time 3 "$API_URL/health" 2>/dev/null)
else
  RUNNING=false
  DETAIL=""
fi

if [ "$JSON" = "true" ]; then
  echo "{\"running\": $RUNNING, \"url\": \"$API_URL\", \"detail\": $(echo "$DETAIL" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null || echo '""')}"
  exit $([ "$RUNNING" = "true" ] && echo 0 || echo 1)
fi

if [ "$RUNNING" = "true" ]; then
  echo "✓ Hummingbot API is running at $API_URL"
  exit 0
else
  echo "✗ Hummingbot API is not running at $API_URL"
  echo "  Start with: make run  (from hummingbot-api dir, dev mode)"
  echo "  Or:         make deploy  (Docker mode)"
  exit 1
fi

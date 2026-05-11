#!/bin/bash
# check_gateway.sh — Check if Gateway is running
# Shared script (same interface as lp-agent/scripts/check_gateway.sh)
# Usage: bash check_gateway.sh [--json]

JSON=false
for arg in "$@"; do
  [ "$arg" = "--json" ] && JSON=true
done

GATEWAY_URL="${GATEWAY_URL:-http://localhost:15888}"

if curl -s --max-time 3 "$GATEWAY_URL/" &>/dev/null; then
  RUNNING=true
else
  RUNNING=false
fi

if [ "$JSON" = "true" ]; then
  echo "{\"running\": $RUNNING, \"url\": \"$GATEWAY_URL\"}"
  exit $([ "$RUNNING" = "true" ] && echo 0 || echo 1)
fi

if [ "$RUNNING" = "true" ]; then
  echo "✓ Gateway is running at $GATEWAY_URL"
  exit 0
else
  echo "✗ Gateway is not running at $GATEWAY_URL"
  echo "  Start from source: cd <GATEWAY_DIR> && pnpm start --passphrase=hummingbot --dev"
  echo "  Or via API:        POST /gateway/start"
  exit 1
fi

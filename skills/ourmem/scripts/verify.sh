#!/bin/bash
# ourmem verification script
# Usage: OMEM_API_URL=https://api.ourmem.ai OMEM_API_KEY=xxx bash verify.sh
#
# Checks:
#   1. Server health
#   2. API key authentication
#   3. Memory store + search round-trip

set -euo pipefail

API_URL="${OMEM_API_URL:-http://localhost:8080}"
API_KEY="${OMEM_API_KEY:-}"
PASS=0
FAIL=0

green() { printf "\033[32m%s\033[0m\n" "$1"; }
red()   { printf "\033[31m%s\033[0m\n" "$1"; }
info()  { printf "\033[36m%s\033[0m\n" "$1"; }

check() {
  local name="$1"
  local result="$2"
  if [ "$result" = "OK" ]; then
    green "  [PASS] $name"
    PASS=$((PASS + 1))
  else
    red "  [FAIL] $name"
    FAIL=$((FAIL + 1))
  fi
}

info "ourmem verification"
info "Server: $API_URL"
echo ""

# --- Check 1: Health ---
info "1/3 Health check..."
HEALTH=$(curl -sf "$API_URL/health" 2>/dev/null && echo "OK" || echo "FAIL")
check "GET /health" "$HEALTH"

if [ "$HEALTH" != "OK" ]; then
  red "Server unreachable at $API_URL. Is it running?"
  exit 1
fi

# --- Check 2: API Key ---
if [ -z "$API_KEY" ]; then
  red "  [SKIP] No OMEM_API_KEY set. Skipping auth and memory tests."
  echo ""
  echo "Results: $PASS passed, $FAIL failed, 2 skipped"
  exit 0
fi

info "2/3 API key validation..."
AUTH=$(curl -sf -H "X-API-Key: $API_KEY" "$API_URL/v1/memories?limit=1" 2>/dev/null && echo "OK" || echo "FAIL")
check "GET /v1/memories (auth)" "$AUTH"

if [ "$AUTH" != "OK" ]; then
  red "API key rejected. Check OMEM_API_KEY value."
  echo ""
  echo "Results: $PASS passed, $FAIL failed"
  exit 1
fi

# --- Check 3: Store + Search ---
info "3/3 Memory store + search round-trip..."

STORE_RESP=$(curl -sX POST "$API_URL/v1/memories" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"content": "ourmem verify test marker 7f3a9b", "tags": ["verify-test"]}' 2>/dev/null)

STORE_ID=$(echo "$STORE_RESP" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$STORE_ID" ]; then
  check "POST /v1/memories (store)" "OK"
else
  check "POST /v1/memories (store)" "FAIL"
fi

# Brief pause for indexing
sleep 1

SEARCH_RESP=$(curl -s "$API_URL/v1/memories/search?q=verify+test+marker+7f3a9b&limit=1" \
  -H "X-API-Key: $API_KEY" 2>/dev/null)

if echo "$SEARCH_RESP" | grep -q "7f3a9b"; then
  check "GET /v1/memories/search (search)" "OK"
else
  check "GET /v1/memories/search (search)" "FAIL"
fi

# Clean up test memory
if [ -n "$STORE_ID" ]; then
  curl -sX DELETE "$API_URL/v1/memories/$STORE_ID" \
    -H "X-API-Key: $API_KEY" >/dev/null 2>&1 || true
fi

# --- Summary ---
echo ""
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
  green "All $TOTAL checks passed. ourmem is ready."
else
  red "$PASS/$TOTAL checks passed, $FAIL failed."
  exit 1
fi

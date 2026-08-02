#!/usr/bin/env bash
set -euo pipefail

# Fetch all devices with space info from Aqara Open API
# and write the response data array to data/devices.json.
#
# Usage:
#   bash scripts/fetch_all_devices.sh
#
# Requires env vars:
#   AQARA_ENDPOINT_URL   — API base URL
#   AQARA_OPEN_API_TOKEN — Bearer token (JWT)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$SKILL_ROOT/data"
OUT_FILE="$DATA_DIR/devices.json"

if [ -z "${AQARA_ENDPOINT_URL:-}" ]; then
  echo "ERROR: AQARA_ENDPOINT_URL is not set." >&2
  exit 1
fi
if [ -z "${AQARA_OPEN_API_TOKEN:-}" ]; then
  echo "ERROR: AQARA_OPEN_API_TOKEN is not set." >&2
  exit 1
fi

mkdir -p "$DATA_DIR"

RESPONSE=$(curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"GetAllDevicesWithSpaceRequest\",\"version\":\"v1\",\"msgId\":\"fetch-$(date +%s)\"}")

RESPONSE_CODE=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code','-1'))" 2>/dev/null || echo "-1")

if [ "$RESPONSE_CODE" != "0" ]; then
  echo "ERROR: API returned code=$RESPONSE_CODE" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

echo "$RESPONSE" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
data = resp.get('data', [])
print(json.dumps(data, ensure_ascii=False, indent=2))
" > "$OUT_FILE"

DEVICE_COUNT=$(python3 -c "import json; print(len(json.load(open('$OUT_FILE'))))" 2>/dev/null || echo "?")
echo "OK: wrote $DEVICE_COUNT devices to $OUT_FILE"

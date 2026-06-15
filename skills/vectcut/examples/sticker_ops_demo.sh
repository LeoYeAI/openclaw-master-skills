#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

echo "=== CREATE DRAFT ==="
CREATE_RES="$(curl --silent --show-error --location --request POST "${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}/create_draft" \
  --header "Authorization: Bearer ${VECTCUT_API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw '{"name":"demo","width":1080,"height":1920}')"
echo "CREATE => ${CREATE_RES}"
DRAFT_ID="$(json_get draft_id "$CREATE_RES")"
[[ -z "$DRAFT_ID" ]] && echo "No draft_id, stop." && exit 1

echo "=== OPS DEMO: search_sticker ==="
PAYLOAD='{"keywords":"生日快乐","count":3,"offset":2}'
RES="$("${ROOT}/scripts/sticker_ops.sh" search_sticker "$PAYLOAD")"
echo "search_sticker => $RES"

echo "=== OPS DEMO: add_sticker ==="
PAYLOAD='{"sticker_id":"7132097333466025252","start":0,"end":5,"draft_id":"__DRAFT_ID__","transform_y":0,"transform_x":0,"alpha":1,"flip_horizontal":false,"flip_vertical":false,"rotation":0,"scale_x":1,"scale_y":1,"track_name":"sticker_main","relative_index":0,"width":1080,"height":1920}'
PAYLOAD="${PAYLOAD//__DRAFT_ID__/${DRAFT_ID}}"
RES="$("${ROOT}/scripts/sticker_ops.sh" add_sticker "$PAYLOAD")"
echo "add_sticker => $RES"

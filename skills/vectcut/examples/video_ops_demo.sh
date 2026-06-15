#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

echo "=== OPS DEMO: add_video ==="
ADD_PAYLOAD='{"video_url":"https://player.install-ai-guider.top/example/VID_20260120_211842.mp4","start":0,"end":10,"target_start":0,"track_name":"video_main"}'
ADD_RES="$(${ROOT}/scripts/video_ops.sh add_video "$ADD_PAYLOAD")"
echo "add_video => $ADD_RES"
MATERIAL_ID="$(json_get material_id "$ADD_RES")"
DRAFT_ID="$(json_get draft_id "$ADD_RES")"
[[ -z "$MATERIAL_ID" || -z "$DRAFT_ID" ]] && echo "add_video missing material_id/draft_id" && exit 1

echo "=== OPS DEMO: modify_video ==="
MODIFY_PAYLOAD='{"draft_id":"'"$DRAFT_ID"'","material_id":"'"$MATERIAL_ID"'","video_url":"https://player.install-ai-guider.top/example/VID_20260120_211842.mp4","start":0,"end":8,"transform_x":0.2,"transform_y":0.2,"scale_x":1.05,"scale_y":1.05,"target_start":1}'
MODIFY_RES="$(${ROOT}/scripts/video_ops.sh modify_video "$MODIFY_PAYLOAD")"
echo "modify_video => $MODIFY_RES"

echo "=== OPS DEMO: remove_video ==="
REMOVE_PAYLOAD='{"material_id":"'"$MATERIAL_ID"'","draft_id":"'"$DRAFT_ID"'"}'
REMOVE_RES="$(${ROOT}/scripts/video_ops.sh remove_video "$REMOVE_PAYLOAD")"
echo "remove_video => $REMOVE_RES"

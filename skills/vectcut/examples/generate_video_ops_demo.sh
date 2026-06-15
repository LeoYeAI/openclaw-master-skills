#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT_ID="${1:-}"
RESOLUTION="${2:-1080P}"
FRAMERATE="${3:-30}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$DRAFT_ID" ]] && echo "Usage: examples/generate_video_ops_demo.sh <draft_id> [resolution] [framerate]" && exit 1

extract_json_string_from_text() {
  local text="$1"
  local key="$2"
  printf '%s' "$text" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

echo "=== GENERATE_VIDEO ==="
GEN_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"resolution\":\"${RESOLUTION}\",\"framerate\":\"${FRAMERATE}\"}"
GEN_RES="$(${ROOT}/scripts/generate_video_ops.sh generate_video "${GEN_PAYLOAD}")"
echo "generate_video => ${GEN_RES}"

TASK_ID="$(extract_json_string_from_text "$GEN_RES" task_id)"
[[ -z "$TASK_ID" ]] && echo "No task_id, stop." && exit 1

echo "=== RENDER_WAIT ==="
WAIT_PAYLOAD="{\"task_id\":\"${TASK_ID}\"}"
WAIT_RES="$(${ROOT}/scripts/generate_video_ops.sh render_wait "${WAIT_PAYLOAD}")"
echo "render_wait => ${WAIT_RES}"

PLAY_URL="$(extract_json_string_from_text "$WAIT_RES" result)"
if [[ -n "$PLAY_URL" ]]; then
  echo "PLAY_URL => $PLAY_URL"
fi
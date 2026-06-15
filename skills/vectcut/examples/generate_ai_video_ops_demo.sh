#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

echo "=== GENERATE_AI_VIDEO ==="
GEN_PAYLOAD='{"model":"veo3.1","prompt":"特写镜头下，两人凝视着墙上一幅神秘图案，火把光芒忽明忽暗摇曳。","resolution":"1280x720"}'
GEN_RES="$(${ROOT}/scripts/generate_ai_video_ops.sh generate_ai_video "$GEN_PAYLOAD")"
echo "generate_ai_video => ${GEN_RES}"

TASK_ID="$(printf '%s' "$GEN_RES" | sed -n 's/.*"task_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
[[ -z "$TASK_ID" ]] && echo "No task_id returned, stop" && exit 1

echo "=== AI_VIDEO_TASK_STATUS ==="
STATUS_PAYLOAD="{\"task_id\":\"${TASK_ID}\"}"
STATUS_RES="$(${ROOT}/scripts/generate_ai_video_ops.sh ai_video_task_status "$STATUS_PAYLOAD")"
echo "ai_video_task_status => ${STATUS_RES}"

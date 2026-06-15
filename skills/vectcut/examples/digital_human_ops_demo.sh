#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

echo "=== CREATE_DIGITAL_HUMAN ==="
CREATE_PAYLOAD='{"audio_url":"https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/d0f39150-7b57-4d0d-bfca-730901dca0da-c5ef496b-07b6.mp3","video_url":"https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/VID_20260114_231107.mp4"}'
CREATE_RES="$(${ROOT}/scripts/digital_human_ops.sh create_digital_human "$CREATE_PAYLOAD")"
echo "create_digital_human => ${CREATE_RES}"

TASK_ID="$(printf '%s' "$CREATE_RES" | sed -n 's/.*"task_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
if [[ -z "$TASK_ID" ]]; then
  TASK_ID="$(printf '%s' "$CREATE_RES" | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
fi
[[ -z "$TASK_ID" ]] && echo "No task_id returned, stop" && exit 1

echo "=== DIGITAL_HUMAN_TASK_STATUS ==="
STATUS_PAYLOAD="{\"task_id\":\"${TASK_ID}\"}"
STATUS_RES="$(${ROOT}/scripts/digital_human_ops.sh digital_human_task_status "$STATUS_PAYLOAD")"
echo "digital_human_task_status => ${STATUS_RES}"

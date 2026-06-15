#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT_ID="${1:-}"
TRACK_NAME="${2:-video_main}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$DRAFT_ID" ]] && echo "Usage: examples/keyframe_ops_demo.sh <draft_id> [track_name]" && exit 1

echo "=== SINGLE KEYFRAME ==="
SINGLE_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"track_name\":\"${TRACK_NAME}\",\"property_type\":\"alpha\",\"time\":0.0,\"value\":\"1.0\"}"
SINGLE_RES="$(${ROOT}/scripts/keyframe_ops.sh add_video_keyframe "${SINGLE_PAYLOAD}")"
echo "single => ${SINGLE_RES}"

echo "=== BATCH KEYFRAME ==="
BATCH_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"track_name\":\"${TRACK_NAME}\",\"property_types\":[\"alpha\",\"scale_x\",\"transform_x\"],\"times\":[0.0,1.2,2.4],\"values\":[\"1.0\",\"1.2\",\"0.15\"]}"
BATCH_RES="$(${ROOT}/scripts/keyframe_ops.sh add_video_keyframe "${BATCH_PAYLOAD}")"
echo "batch => ${BATCH_RES}"
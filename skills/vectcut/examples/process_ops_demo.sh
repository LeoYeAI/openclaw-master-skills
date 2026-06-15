#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIDEO_URL="${1:-https://example.com/demo.mp4}"
START="${2:-3.3}"
END="${3:-5.1}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

echo "=== EXTRACT_AUDIO ==="
EXTRACT_PAYLOAD="{\"video_url\":\"${VIDEO_URL}\"}"
EXTRACT_RES="$(${ROOT}/scripts/process_ops.sh extract_audio "${EXTRACT_PAYLOAD}")"
echo "extract_audio => ${EXTRACT_RES}"

echo "=== SPLIT_VIDEO ==="
SPLIT_PAYLOAD="{\"video_url\":\"${VIDEO_URL}\",\"start\":${START},\"end\":${END}}"
SPLIT_RES="$(${ROOT}/scripts/process_ops.sh split_video "${SPLIT_PAYLOAD}")"
echo "split_video => ${SPLIT_RES}"

echo "=== DONE ==="
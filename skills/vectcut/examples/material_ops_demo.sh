#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
URL_INPUT="${1:-https://example.com/demo.mp4}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

echo "=== CURL DEMO: get_duration ==="
CURL_PAYLOAD="{\"url\":\"${URL_INPUT}\"}"
CURL_RES_DURATION="$("${ROOT}/scripts/material_ops.sh" get_duration "${CURL_PAYLOAD}")"
echo "CURL get_duration => ${CURL_RES_DURATION}"

echo "=== CURL DEMO: get_resolution ==="
CURL_RES_RESOLUTION="$("${ROOT}/scripts/material_ops.sh" get_resolution "${CURL_PAYLOAD}")"
echo "CURL get_resolution => ${CURL_RES_RESOLUTION}"

echo "=== CURL DEMO: video_detail ==="
DETAIL_PAYLOAD="{\"video_url\":\"${URL_INPUT}\"}"
CURL_RES_DETAIL="$("${ROOT}/scripts/material_ops.sh" video_detail "${DETAIL_PAYLOAD}")"
echo "CURL video_detail => ${CURL_RES_DETAIL}"

echo "=== DONE ==="
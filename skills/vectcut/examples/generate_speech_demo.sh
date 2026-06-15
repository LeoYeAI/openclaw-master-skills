#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEXT="${1:-今天的视频，就给大家带来一个福利。}"
CLONE_FILE_URL="${2:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

PAYLOAD="{\"text\":\"${TEXT}\",\"provider\":\"minimax\",\"model\":\"speech-2.6-turbo\",\"voice_id\":\"audiobook_male_1\",\"volume\":10,\"target_start\":3,\"effect_type\":\"麦霸\",\"effect_params\":[45,80]}"

echo "=== SHELL DEMO ==="
RES="$(${ROOT}/scripts/generate_speech_ops.sh generate_speech "${PAYLOAD}")"
echo "generate_speech => ${RES}"

if [[ -n "$CLONE_FILE_URL" ]]; then
  echo "=== FISH CLONE DEMO ==="
  CLONE_PAYLOAD="{\"file_url\":\"${CLONE_FILE_URL}\",\"title\":\"demo_clone_voice\"}"
  CLONE_RES="$(${ROOT}/scripts/generate_speech_ops.sh fish_clone "${CLONE_PAYLOAD}")"
  echo "fish_clone => ${CLONE_RES}"
fi

echo "=== VOICE ASSETS DEMO ==="
ASSETS_PAYLOAD='{"limit":100,"offset":0,"provider":"fish"}'
ASSETS_RES="$(${ROOT}/scripts/generate_speech_ops.sh voice_assets "${ASSETS_PAYLOAD}")"
echo "voice_assets => ${ASSETS_RES}"

echo "=== DONE ==="
#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <generate_ai_video|ai_video_task_status> '<json_payload>'"
  exit 1
}

fail() {
  local error="$1"
  local output="${2:-\"\"}"
  printf '{"success":false,"error":"%s","output":%s}\n' "$error" "$output"
  exit 0
}

extract_json_string() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

extract_json_number() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p"
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

if [[ "$ACTION" == "generate_ai_video" ]]; then
  PROMPT="$(extract_json_string prompt)"
  MODEL="$(extract_json_string model)"
  RESOLUTION="$(extract_json_string resolution)"
  GEN_DURATION="$(extract_json_number gen_duration)"
  END_IMAGE="$(extract_json_string end_image)"
  [[ -z "$PROMPT" || -z "$MODEL" || -z "$RESOLUTION" ]] && fail "prompt/model/resolution is required"
  [[ ! "$MODEL" =~ ^(veo3.1|veo3.1-pro|seedance-1.5-pro|grok-video-3|sora2)$ ]] && fail "model must be one of: veo3.1, veo3.1-pro, seedance-1.5-pro, grok-video-3, sora2"
  [[ ! "$RESOLUTION" =~ ^[0-9]+x[0-9]+$ ]] && fail "resolution must match format: <width>x<height>"
  if [[ -n "$END_IMAGE" && ! "$MODEL" =~ ^(veo3.1|veo3.1-pro|seedance-1.5-pro)$ ]]; then
    fail "model ${MODEL} does not support end_image"
  fi
  if [[ -n "$GEN_DURATION" ]]; then
    if [[ "$MODEL" == "grok-video-3" && ! "$GEN_DURATION" =~ ^(6|10|15)$ ]]; then
      fail "gen_duration for grok-video-3 must be one of: 6,10,15"
    fi
    if [[ "$MODEL" == "sora2" && ! "$GEN_DURATION" =~ ^(10|15)$ ]]; then
      fail "gen_duration for sora2 must be one of: 10,15"
    fi
    if [[ "$MODEL" == "seedance-1.5-pro" && ! "$GEN_DURATION" =~ ^(4|5|6|7|8|9|10|11|12)$ ]]; then
      fail "gen_duration for seedance-1.5-pro must be one of: 4..12"
    fi
    if [[ "$MODEL" =~ ^(veo3.1|veo3.1-pro)$ ]]; then
      fail "model ${MODEL} does not support gen_duration"
    fi
  fi
  curl --silent --show-error --location --request POST "${BASE_URL}/generate_ai_video" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$PAYLOAD"
  echo
  exit 0
fi

if [[ "$ACTION" == "ai_video_task_status" ]]; then
  TASK_ID="$(extract_json_string task_id)"
  [[ -z "$TASK_ID" ]] && fail "task_id is required"
  curl --silent --show-error --location --request GET "${BASE_URL}/aivideo/task_status?task_id=${TASK_ID}" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json"
  echo
  exit 0
fi

usage

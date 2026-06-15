#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <create_digital_human|digital_human_task_status> '<json_payload>'"
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

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

if [[ "$ACTION" == "create_digital_human" ]]; then
  AUDIO_URL="$(extract_json_string audio_url)"
  VIDEO_URL="$(extract_json_string video_url)"
  [[ -z "$AUDIO_URL" || -z "$VIDEO_URL" ]] && fail "audio_url/video_url is required"
  [[ ! "$AUDIO_URL" =~ ^https?:// ]] && fail "audio_url must start with http:// or https://"
  [[ ! "$VIDEO_URL" =~ ^https?:// ]] && fail "video_url must start with http:// or https://"
  curl --silent --show-error --location --request POST "${BASE_URL}/digital_human/create" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$PAYLOAD"
  echo
  exit 0
fi

if [[ "$ACTION" == "digital_human_task_status" ]]; then
  TASK_ID="$(extract_json_string task_id)"
  URL="${BASE_URL}/digital_human/task_status"
  [[ -n "$TASK_ID" ]] && URL="${URL}?task_id=${TASK_ID}"
  curl --silent --show-error --location --request GET "$URL" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json"
  echo
  exit 0
fi

usage

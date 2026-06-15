#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_PROCESS_BASE_URL:-https://open.vectcut.com/process}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <extract_audio|split_video> '<json_payload>'"
  exit 1
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

extract_json_string() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

extract_json_number() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([-0-9.][0-9.]*\).*/\1/p"
}

post_json() {
  local endpoint="$1"; local body="$2"
  curl --silent --show-error --location --request POST "${BASE_URL}/${endpoint}" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$body"
  echo
}

VIDEO_URL="$(extract_json_string video_url)"
[[ -z "$VIDEO_URL" ]] && echo '{"success":false,"error":"video_url is required","output":""}' && exit 0
[[ ! "$VIDEO_URL" =~ ^https?:// ]] && echo '{"success":false,"error":"video_url must start with http:// or https://","output":""}' && exit 0

if [[ "$ACTION" == "extract_audio" ]]; then
  post_json extract_audio "{\"video_url\":\"$VIDEO_URL\"}"; exit 0
fi

if [[ "$ACTION" == "split_video" ]]; then
  START="$(extract_json_number start)"; END="$(extract_json_number end)"
  [[ -z "$START" || -z "$END" ]] && echo '{"success":false,"error":"start and end are required","output":""}' && exit 0
  awk -v s="$START" -v e="$END" 'BEGIN{if(s<0 || e<=s){exit 1}}' || { echo '{"success":false,"error":"invalid range: require 0 <= start < end","output":""}'; exit 0; }
  post_json split_video "{\"video_url\":\"${VIDEO_URL}\",\"start\":${START},\"end\":${END}}"
  exit 0
fi

usage
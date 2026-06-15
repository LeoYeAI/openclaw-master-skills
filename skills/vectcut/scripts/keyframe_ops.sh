#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <add_video_keyframe> '<json_payload>'"
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

extract_json_array() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\[\([^]]*\)\].*/\1/p"
}

array_count() {
  local arr="$1"
  [[ -z "${arr//[[:space:]]/}" ]] && { echo 0; return; }
  awk -v s="$arr" 'BEGIN{n=split(s,a,",");print n}'
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage
ACTION="$1"
PAYLOAD="$2"
[[ "$ACTION" != "add_video_keyframe" ]] && usage

DRAFT_ID="$(extract_json_string draft_id)"
[[ -z "$DRAFT_ID" ]] && fail "draft_id is required"

HAS_BATCH=0
[[ "$PAYLOAD" == *'"property_types"'* || "$PAYLOAD" == *'"times"'* || "$PAYLOAD" == *'"values"'* ]] && HAS_BATCH=1
if [[ "$HAS_BATCH" == "1" ]]; then
  PROPERTY_TYPES_RAW="$(extract_json_array property_types)"
  TIMES_RAW="$(extract_json_array times)"
  VALUES_RAW="$(extract_json_array values)"
  [[ -z "${PROPERTY_TYPES_RAW//[[:space:]]/}" || -z "${TIMES_RAW//[[:space:]]/}" || -z "${VALUES_RAW//[[:space:]]/}" ]] && fail "property_types/times/values must be non-empty arrays"
  C1="$(array_count "$PROPERTY_TYPES_RAW")"
  C2="$(array_count "$TIMES_RAW")"
  C3="$(array_count "$VALUES_RAW")"
  [[ "$C1" != "$C2" || "$C2" != "$C3" ]] && fail "property_types/times/values length must be equal"
else
  TIME_VAL="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"time"[[:space:]]*:[[:space:]]*\([-0-9.][0-9.]*\).*/\1/p')"
  [[ -n "$TIME_VAL" ]] && awk -v t="$TIME_VAL" 'BEGIN{if(t<0){exit 1}}' || true
fi

curl --silent --show-error --location --request POST "${BASE_URL}/add_video_keyframe" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "$PAYLOAD"
echo
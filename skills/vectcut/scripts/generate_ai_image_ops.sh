#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <generate_ai_image> '<json_payload>'"
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
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([-0-9.][0-9.]*\).*/\1/p"
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage
ACTION="$1"
PAYLOAD="$2"
[[ "$ACTION" != "generate_ai_image" ]] && usage

PROMPT="$(extract_json_string prompt)"
MODEL="$(extract_json_string model)"
SIZE="$(extract_json_string size)"
REFERENCE_IMAGE="$(extract_json_string reference_image)"

[[ -z "$PROMPT" || -z "$MODEL" ]] && fail "prompt/model is required"
[[ ! "$MODEL" =~ ^(nano_banana|nano_banana_2|nano_banana_pro|jimeng-4.5)$ ]] && fail "model must be one of: nano_banana, nano_banana_2, nano_banana_pro, jimeng-4.5"
[[ -n "$SIZE" && ! "$SIZE" =~ ^[0-9]+x[0-9]+$ ]] && fail "size must match format: <width>x<height>"
if [[ -n "$REFERENCE_IMAGE" ]]; then
  [[ ! "$REFERENCE_IMAGE" =~ ^https?:// ]] && fail "reference_image must start with http:// or https://"
fi

START_VAL="$(extract_json_number start)"
END_VAL="$(extract_json_number end)"
if [[ -n "$START_VAL" && -n "$END_VAL" ]]; then
  awk -v s="$START_VAL" -v e="$END_VAL" 'BEGIN{if(e<=s){exit 1}}' || fail "invalid range: require end > start"
fi

curl --silent --show-error --location --request POST "${BASE_URL}/generate_image" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "$PAYLOAD"
echo
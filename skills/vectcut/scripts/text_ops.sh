#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <add_text|modify_text|remove_text> '<json_payload>'"
  exit 1
}

fail() {
  local error="$1"
  local output="${2:-\"\"}"
  printf '{"success":false,"error":"%s","output":%s}\n' "$error" "$output"
  exit 0
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

if [[ "$ACTION" == "add_text" ]]; then
  TEXT="$(extract_json_string text)"
  START="$(extract_json_number start)"
  END="$(extract_json_number end)"
  [[ -z "$TEXT" ]] && fail "text is required"
  [[ -z "$START" || -z "$END" ]] && fail "start and end are required"
  awk -v s="$START" -v e="$END" 'BEGIN{if(e<=s){exit 1}}' || fail "invalid range: require end > start"
  curl --silent --show-error --location --request POST "${BASE_URL}/add_text" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$PAYLOAD"
  echo
  exit 0
fi

if [[ "$ACTION" == "modify_text" ]]; then
  DRAFT_ID="$(extract_json_string draft_id)"
  MATERIAL_ID="$(extract_json_string material_id)"
  TEXT="$(extract_json_string text)"
  START="$(extract_json_number start)"
  END="$(extract_json_number end)"
  [[ -z "$DRAFT_ID" || -z "$MATERIAL_ID" ]] && fail "draft_id and material_id are required"
  [[ -z "$TEXT" ]] && fail "text is required"
  [[ -z "$START" || -z "$END" ]] && fail "start and end are required"
  awk -v s="$START" -v e="$END" 'BEGIN{if(e<=s){exit 1}}' || fail "invalid range: require end > start"
  curl --silent --show-error --location --request POST "${BASE_URL}/modify_text" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$PAYLOAD"
  echo
  exit 0
fi

if [[ "$ACTION" == "remove_text" ]]; then
  DRAFT_ID="$(extract_json_string draft_id)"
  MATERIAL_ID="$(extract_json_string material_id)"
  [[ -z "$DRAFT_ID" || -z "$MATERIAL_ID" ]] && fail "draft_id and material_id are required"
  curl --silent --show-error --location --request POST "${BASE_URL}/remove_text" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$PAYLOAD"
  echo
  exit 0
fi

usage
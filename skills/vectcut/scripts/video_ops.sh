#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <add_video|modify_video|remove_video> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  add_video) ENDPOINT="add_video" ;;
  modify_video) ENDPOINT="modify_video" ;;
  remove_video) ENDPOINT="remove_video" ;;
  *) usage ;;
esac

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

if [[ "$ACTION" == "add_video" ]]; then
  VIDEO_URL="$(json_get video_url "$PAYLOAD")"
  [[ -z "$VIDEO_URL" ]] && echo '{"success":false,"error":"Missing required fields for add_video: video_url","output":""}' && exit 0
fi

if [[ "$ACTION" == "modify_video" || "$ACTION" == "remove_video" ]]; then
  DRAFT_ID="$(json_get draft_id "$PAYLOAD")"
  MATERIAL_ID="$(json_get material_id "$PAYLOAD")"
  [[ -z "$DRAFT_ID" || -z "$MATERIAL_ID" ]] && echo "{\"success\":false,\"error\":\"Missing required fields for ${ACTION}: draft_id/material_id\",\"output\":\"\"}" && exit 0
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo

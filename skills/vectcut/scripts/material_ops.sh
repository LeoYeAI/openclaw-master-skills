#!/usr/bin/env bash
set -euo pipefail

CUT_BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
LLM_BASE_URL="${VECTCUT_LLM_BASE_URL:-https://open.vectcut.com/llm}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <get_duration|get_resolution|video_detail> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  get_duration) ENDPOINT="get_duration" ;;
  get_resolution) ENDPOINT="get_resolution" ;;
  video_detail) ENDPOINT="video_detail" ;;
  *) usage ;;
esac

URL_VALUE="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
VIDEO_URL_VALUE="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"video_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
CLEAN_URL="${URL_VALUE//\`/}"
CLEAN_VIDEO_URL="${VIDEO_URL_VALUE//\`/}"

if [[ "$ACTION" == "video_detail" ]]; then
  FINAL_URL="${CLEAN_VIDEO_URL:-$CLEAN_URL}"
else
  FINAL_URL="${CLEAN_URL:-$CLEAN_VIDEO_URL}"
fi

if [[ -z "$FINAL_URL" ]]; then
  echo "{\"success\":false,\"error\":\"url/video_url is required\",\"output\":\"\"}"
  exit 0
fi

if [[ ! "$FINAL_URL" =~ ^https?:// ]]; then
  echo "{\"success\":false,\"error\":\"url/video_url must start with http:// or https://\",\"output\":\"\"}"
  exit 0
fi

if [[ "$ACTION" == "video_detail" ]]; then
  BASE_URL="$LLM_BASE_URL"
  NORMALIZED_PAYLOAD="{\"video_url\":\"${FINAL_URL}\"}"
else
  BASE_URL="$CUT_BASE_URL"
  NORMALIZED_PAYLOAD="{\"url\":\"${FINAL_URL}\"}"
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${NORMALIZED_PAYLOAD}"
echo
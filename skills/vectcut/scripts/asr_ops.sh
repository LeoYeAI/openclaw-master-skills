#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/llm}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <asr_basic|asr_nlp|asr_llm> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  asr_basic) ENDPOINT="asr_basic" ;;
  asr_nlp) ENDPOINT="asr_nlp" ;;
  asr_llm) ENDPOINT="asr_llm" ;;
  *) usage ;;
esac

URL_VALUE="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
CONTENT_VALUE="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"content"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"

if [[ -z "$URL_VALUE" ]]; then
  echo "{\"success\":false,\"error\":\"url is required\",\"output\":\"\"}"
  exit 0
fi

if [[ ! "$URL_VALUE" =~ ^https?:// ]]; then
  echo "{\"success\":false,\"error\":\"url must start with http:// or https://\",\"output\":\"\"}"
  exit 0
fi

if [[ "$PAYLOAD" == *"\"content\""* && -z "$CONTENT_VALUE" ]]; then
  echo "{\"success\":false,\"error\":\"content must be a non-empty string when provided\",\"output\":\"\"}"
  exit 0
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo
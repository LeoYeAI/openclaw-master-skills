#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <create|modify|remove|query> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  create) ENDPOINT="create_draft" ;;
  modify) ENDPOINT="modify_draft" ;;
  remove) ENDPOINT="remove_draft" ;;
  query) ENDPOINT="query_script" ;;
  *) usage ;;
esac

DRAFT_ID="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"draft_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
NAME_VALUE="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
COVER_VALUE="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"cover"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"

if [[ "$ACTION" == "modify" || "$ACTION" == "remove" || "$ACTION" == "query" ]]; then
  if [[ -z "$DRAFT_ID" ]]; then
    echo "{\"success\":false,\"error\":\"draft_id is required\",\"output\":\"\"}"
    exit 0
  fi
fi

if [[ "$ACTION" == "modify" ]]; then
  if [[ -z "$NAME_VALUE" && -z "$COVER_VALUE" ]]; then
    echo "{\"success\":false,\"error\":\"modify requires at least one of name or cover\",\"output\":\"\"}"
    exit 0
  fi
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo
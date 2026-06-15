#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"
ENUM_FILE="${ENUM_FILE:-$(cd "$(dirname "$0")/.." && pwd)/references/enums/filter_types.json}"

usage() {
  echo "Usage: $0 <add|modify|remove> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  add) ENDPOINT="add_filter" ;;
  modify) ENDPOINT="modify_filter" ;;
  remove) ENDPOINT="remove_filter" ;;
  *) usage ;;
esac

if [[ "$ACTION" == "add" || "$ACTION" == "modify" ]]; then
  FT="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"filter_type"[[:space:]]*:[[:space:]]*"$[^"]*$".*/\1/p')"
  if [[ -n "$FT" ]] && ! grep -Fq "\"name\": \"$FT\"" "$ENUM_FILE"; then
    echo "{\"success\":false,\"error\":\"Unknown filter type: $FT\",\"output\":\"\"}"
    exit 0
  fi
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo
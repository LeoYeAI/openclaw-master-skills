#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHAR_ENUM="${CHAR_ENUM:-${ROOT}/references/enums/character_effect_types.json}"
SCENE_ENUM="${SCENE_ENUM:-${ROOT}/references/enums/scene_effect_types.json}"

usage() {
  echo "Usage: $0 <add|modify|remove> '<json_payload>'"
  exit 1
}

[[ -z "${API_KEY}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

case "$ACTION" in
  add) ENDPOINT="add_effect" ;;
  modify) ENDPOINT="modify_effect" ;;
  remove) ENDPOINT="remove_effect" ;;
  *) usage ;;
esac

if [[ "$ACTION" == "add" || "$ACTION" == "modify" ]]; then
  ET="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"effect_type"[[:space:]]*:[[:space:]]*"$[^"]*$".*/\1/p')"
  if [[ -n "$ET" ]] && ! (grep -Fq "\"name\": \"$ET\"" "$CHAR_ENUM" || grep -Fq "\"name\": \"$ET\"" "$SCENE_ENUM"); then
    echo "{\"success\":false,\"error\":\"Unknown effect type: $ET\",\"output\":\"\"}"
    exit 0
  fi
fi

curl --silent --show-error --location --request POST "${BASE_URL}/${ENDPOINT}" \
  --header "Authorization: Bearer ${API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw "${PAYLOAD}"
echo
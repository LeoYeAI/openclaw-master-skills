#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\\1/p"
}

CREATE_PAYLOAD='{"width":1080,"height":1920,"name":"draft_ops_demo"}'
CREATE_RES="$("${ROOT}/scripts/draft_ops.sh" create "${CREATE_PAYLOAD}")"
echo "CREATE => ${CREATE_RES}"

DRAFT_ID="$(json_get draft_id "${CREATE_RES}")"
[[ -z "${DRAFT_ID}" ]] && echo "No draft_id, stop." && exit 1

MODIFY_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"name\":\"draft_ops_demo_updated\"}"
MODIFY_RES="$("${ROOT}/scripts/draft_ops.sh" modify "${MODIFY_PAYLOAD}")"
echo "MODIFY => ${MODIFY_RES}"

QUERY_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\"}"
QUERY_RES="$("${ROOT}/scripts/draft_ops.sh" query "${QUERY_PAYLOAD}")"
echo "QUERY => ${QUERY_RES}"

REMOVE_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\"}"
REMOVE_RES="$("${ROOT}/scripts/draft_ops.sh" remove "${REMOVE_PAYLOAD}")"
echo "REMOVE => ${REMOVE_RES}"
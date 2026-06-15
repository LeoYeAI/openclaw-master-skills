#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

pick_random_filter() {
  grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "${ROOT}/references/enums/filter_types.json" \
  | sed 's/.*"name"[[:space:]]*:[[:space:]]*"$[^"]*$".*/\1/' \
  | awk 'BEGIN{srand()} {a[NR]=$0} END{if(NR>0) print a[int(rand()*NR)+1]}'
}

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\$[^\"]*\$\".*/\\1/p"
}

FILTER_TYPE="$(pick_random_filter)"
echo "Use filter_type: ${FILTER_TYPE}"

CREATE_RES="$(curl --silent --show-error --location --request POST "${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}/create_draft" \
  --header "Authorization: Bearer ${VECTCUT_API_KEY}" \
  --header "Content-Type: application/json" \
  --data-raw '{"name":"filter_demo","width":1080,"height":1920}')"
echo "CREATE => ${CREATE_RES}"

DRAFT_ID="$(json_get draft_id "$CREATE_RES")"
[[ -z "$DRAFT_ID" ]] && echo "No draft_id, stop." && exit 1

ADD_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"filter_type\":\"${FILTER_TYPE}\",\"start\":0,\"end\":3,\"track_name\":\"filter_1\",\"relative_index\":1,\"intensity\":86}"
ADD_RES="$("${ROOT}/scripts/filter_ops.sh" add "$ADD_PAYLOAD")"
echo "ADD => ${ADD_RES}"

MATERIAL_ID="$(json_get material_id "$ADD_RES")"
[[ -z "$MATERIAL_ID" ]] && echo "No material_id, skip modify/remove." && exit 0

MOD_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"material_id\":\"${MATERIAL_ID}\",\"filter_type\":\"${FILTER_TYPE}\",\"start\":1,\"end\":4,\"track_name\":\"filter_1\",\"relative_index\":1,\"intensity\":45}"
echo "MODIFY => $("${ROOT}/scripts/filter_ops.sh" modify "$MOD_PAYLOAD")"

RM_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"material_id\":\"${MATERIAL_ID}\"}"
echo "REMOVE => $("${ROOT}/scripts/filter_ops.sh" remove "$RM_PAYLOAD")"
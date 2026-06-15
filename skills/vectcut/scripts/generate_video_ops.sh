#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <generate_video|task_status|render_wait> '<json_payload>'"
  exit 1
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage

ACTION="$1"
PAYLOAD="$2"

extract_json_string() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

extract_json_string_from_text() {
  local text="$1"; local key="$2"
  printf '%s' "$text" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

post_json() {
  local endpoint="$1"; local body="$2"
  curl --silent --show-error --location --request POST "${BASE_URL}/${endpoint}" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw "$body"
}

if [[ "$ACTION" == "generate_video" ]]; then
  DRAFT_ID="$(extract_json_string draft_id)"; RESOLUTION="$(extract_json_string resolution)"; FRAMERATE="$(extract_json_string framerate)"
  [[ -z "$DRAFT_ID" ]] && echo '{"success":false,"error":"draft_id is required","output":""}' && exit 0
  BODY="{\"draft_id\":\"$DRAFT_ID\""; [[ -n "$RESOLUTION" ]] && BODY+=",\"resolution\":\"$RESOLUTION\""; [[ -n "$FRAMERATE" ]] && BODY+=",\"framerate\":\"$FRAMERATE\""; BODY+="}"
  post_json generate_video "$BODY"; echo; exit 0
fi

if [[ "$ACTION" == "task_status" ]]; then
  TASK_ID="$(extract_json_string task_id)"; [[ -z "$TASK_ID" ]] && echo '{"success":false,"error":"task_id is required","output":""}' && exit 0
  post_json task_status "{\"task_id\":\"$TASK_ID\"}"; echo; exit 0
fi

if [[ "$ACTION" == "render_wait" ]]; then
  TASK_ID="$(extract_json_string task_id)"; DRAFT_ID="$(extract_json_string draft_id)"; RESOLUTION="$(extract_json_string resolution)"; FRAMERATE="$(extract_json_string framerate)"
  MAX_POLL="$(extract_json_string max_poll)"; POLL_INTERVAL="$(extract_json_string poll_interval)"; MAX_POLL="${MAX_POLL:-30}"; POLL_INTERVAL="${POLL_INTERVAL:-2}"
  if [[ -z "$TASK_ID" ]]; then
    [[ -z "$DRAFT_ID" ]] && echo '{"success":false,"error":"draft_id or task_id is required","output":""}' && exit 0
    GEN_PAYLOAD="{\"draft_id\":\"$DRAFT_ID\""; [[ -n "$RESOLUTION" ]] && GEN_PAYLOAD+=",\"resolution\":\"$RESOLUTION\""; [[ -n "$FRAMERATE" ]] && GEN_PAYLOAD+=",\"framerate\":\"$FRAMERATE\""; GEN_PAYLOAD+="}"
    GEN_RES="$(post_json generate_video "$GEN_PAYLOAD")"
    TASK_ID="$(extract_json_string_from_text "$GEN_RES" task_id)"
    [[ -z "$TASK_ID" ]] && echo "{\"success\":false,\"error\":\"Missing key field: output.task_id\",\"output\":${GEN_RES:-"\"\""}}" && exit 0
  fi
  LAST=""
  for ((i=0;i<MAX_POLL;i++)); do
    LAST="$(post_json task_status "{\"task_id\":\"$TASK_ID\"}")"
    STATUS="$(extract_json_string_from_text "$LAST" status)"; RESULT_URL="$(extract_json_string_from_text "$LAST" result)"
    [[ "$STATUS" == "SUCCESS" && -n "$RESULT_URL" ]] && echo "$LAST" && exit 0
    [[ "$STATUS" == "FAILURE" || "$STATUS" == "FAILED" ]] && echo "{\"success\":false,\"error\":\"Render failed\",\"output\":${LAST:-"\"\""}}" && exit 0
    sleep "$POLL_INTERVAL"
  done
  echo "{\"success\":false,\"error\":\"Render polling timeout\",\"output\":${LAST:-"\"\""}}"; exit 0
fi

usage
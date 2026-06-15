#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT_ID="${1:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$DRAFT_ID" ]] && echo "Usage: examples/text_ops_demo.sh <draft_id>" && exit 1

ADD_PAYLOAD="{\"text\":\"你好!Hello\",\"start\":0,\"end\":5,\"draft_id\":\"${DRAFT_ID}\",\"font\":\"文轩体\",\"font_color\":\"#FF0000\",\"font_size\":8.0,\"track_name\":\"text_main\",\"intro_animation\":\"向下飞入\",\"intro_duration\":0.5,\"outro_animation\":\"向下滑动\",\"outro_duration\":0.5}"

echo "=== ADD_TEXT ==="
ADD_RES="$(${ROOT}/scripts/text_ops.sh add_text "${ADD_PAYLOAD}")"
echo "add_text => ${ADD_RES}"
MATERIAL_ID="$(printf '%s' "$ADD_RES" | sed -n 's/.*"material_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
[[ -z "$MATERIAL_ID" ]] && echo "No material_id from add_text, stop" && exit 1

echo "=== MODIFY_TEXT ==="
MODIFY_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"material_id\":\"${MATERIAL_ID}\",\"text\":\"你好!Hello(已修改)\",\"start\":0,\"end\":5,\"font\":\"文轩体\",\"track_name\":\"text_main_2\"}"
MODIFY_RES="$(${ROOT}/scripts/text_ops.sh modify_text "${MODIFY_PAYLOAD}")"
echo "modify_text => ${MODIFY_RES}"

echo "=== REMOVE_TEXT ==="
REMOVE_PAYLOAD="{\"draft_id\":\"${DRAFT_ID}\",\"material_id\":\"${MATERIAL_ID}\"}"
REMOVE_RES="$(${ROOT}/scripts/text_ops.sh remove_text "${REMOVE_PAYLOAD}")"
echo "remove_text => ${REMOVE_RES}"
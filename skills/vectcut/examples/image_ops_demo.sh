#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

json_get() {
  local key="$1" data="$2"
  printf '%s' "$data" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

pick_random_intro_animation_type() {
  (
    grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "${ROOT}/references/enums/intro_animation_types.json" || true
  ) | sed 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' \
    | awk 'BEGIN{srand()} {a[NR]=$0} END{if(NR>0) print a[int(rand()*NR)+1]}'
}

pick_random_outro_animation_type() {
  (
    grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "${ROOT}/references/enums/outro_animation_types.json" || true
  ) | sed 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' \
    | awk 'BEGIN{srand()} {a[NR]=$0} END{if(NR>0) print a[int(rand()*NR)+1]}'
}


pick_random_combo_animation_type() {
  (
    grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "${ROOT}/references/enums/combo_animation_types.json" || true
  ) | sed 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' \
    | awk 'BEGIN{srand()} {a[NR]=$0} END{if(NR>0) print a[int(rand()*NR)+1]}'
}


pick_random_mask_types() {
  (
    grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "${ROOT}/references/enums/mask_types.json" || true
  ) | sed 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' \
    | awk 'BEGIN{srand()} {a[NR]=$0} END{if(NR>0) print a[int(rand()*NR)+1]}'
}


intro_animation=$(pick_random_intro_animation_type)
outro_animation=$(pick_random_outro_animation_type)
combo_animation=$(pick_random_combo_animation_type)
mask_type=$(pick_random_mask_types)



echo "=== OPS DEMO: add_image ==="
ADD_PAYLOAD='{"image_url":"https://pic1.imgdb.cn/item/68ba8fc058cb8da5c8801ab0.png","start":0,"end":5,"width":1920,"height":1080,"transform_x":0.2,"transform_y":0.2,"scale_x":1,"scale_y":1,"track_name":"video_main","relative_index":99,"intro_animation":"'"$intro_animation"'","intro_animation_duration":0.5,"outro_animation":"'"$outro_animation"'","outro_animation_duration":0.5,"combo_animation":"'"$combo_animation"'","combo_animation_duration":0.5,"mask_type":"'"$mask_type"'","mask_center_x":0.5,"mask_center_y":0.5,"mask_size":0.7,"mask_rotation":45,"mask_feather":2,"mask_invert":true,"mask_rect_width":8,"mask_round_corner":10}'
ADD_RES="$(${ROOT}/scripts/image_ops.sh add_image "$ADD_PAYLOAD")"
echo "add_image => $ADD_RES"
MATERIAL_ID="$(json_get material_id "$ADD_RES")"
DRAFT_ID="$(json_get draft_id "$ADD_RES")"
[[ -z "$MATERIAL_ID" || -z "$DRAFT_ID" ]] && echo "add_image missing material_id/draft_id" && exit 1

echo "=== OPS DEMO: modify_image ==="
MODIFY_PAYLOAD='{"material_id":"'"$MATERIAL_ID"'","draft_id":"'"$DRAFT_ID"'","image_url":"https://pic1.imgdb.cn/item/68ba8fc058cb8da5c8801ab0.png","start":1,"end":4.5,"scale_x":0.9,"scale_y":0.9,"transform_x":0.1,"transform_y":0.1,"outro_animation":"'"$outro_animation"'","alpha":0.85,"rotation":10}'
MODIFY_RES="$(${ROOT}/scripts/image_ops.sh modify_image "$MODIFY_PAYLOAD")"
echo "modify_image => $MODIFY_RES"

echo "=== OPS DEMO: remove_image ==="
REMOVE_PAYLOAD='{"material_id":"'"$MATERIAL_ID"'","draft_id":"'"$DRAFT_ID"'"}'
REMOVE_RES="$(${ROOT}/scripts/image_ops.sh remove_image "$REMOVE_PAYLOAD")"
echo "remove_image => $REMOVE_RES"

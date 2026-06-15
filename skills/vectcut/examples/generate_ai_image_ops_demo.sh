#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT_ID="${1:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$DRAFT_ID" ]] && echo "Usage: examples/generate_ai_image_ops_demo.sh <draft_id>" && exit 1

echo "=== TEXT TO IMAGE ==="
PAYLOAD_1=$(cat <<JSON
{"prompt":"绘制一张卡通风格教学卡片，主题是光合作用中的二氧化碳循环","model":"nano_banana_pro","size":"1376x768","draft_id":"${DRAFT_ID}","start":0,"end":4,"track_name":"video_main"}
JSON
)
RES_1="$(${ROOT}/scripts/generate_ai_image_ops.sh generate_ai_image "$PAYLOAD_1")"
echo "text_to_image => ${RES_1}"

echo "=== IMAGE TO IMAGE ==="
PAYLOAD_2=$(cat <<JSON
{"prompt":"把背景换成秋天的枫叶红色树林，画风保持一致","model":"nano_banana_2","reference_image":"https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/shuziren.jpg","size":"1024x1024","draft_id":"${DRAFT_ID}","start":4,"end":8,"track_name":"video_main"}
JSON
)
RES_2="$(${ROOT}/scripts/generate_ai_image_ops.sh generate_ai_image "$PAYLOAD_2")"
echo "image_to_image => ${RES_2}"
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT_ID="${1:-}"
REF_IMAGE_URL="${2:-https://images.unsplash.com/photo-1541701494587-cb58502866ab}"
API_BASE="${VECTCUT_API_BASE:-https://api.vectcut.com}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$DRAFT_ID" ]] && echo "Usage: examples/generate_ai_image_ops_demo.sh <draft_id> [reference_image_url]" && exit 1

echo "=== TEXT TO IMAGE ==="
PAYLOAD_1="$(cat <<JSON
{
  "prompt": "绘制一张卡通风格教学卡片，主题是光合作用中的二氧化碳循环",
  "model": "nano_banana_pro",
  "size": "1376x768",
  "draft_id": "$DRAFT_ID"
}
JSON
)"

curl -sS -X POST "$API_BASE/v1/generate_ai_image" \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_1"

echo
echo "=== IMAGE TO IMAGE ==="
PAYLOAD_2="$(cat <<JSON
{
  "prompt": "将画面改为赛博朋克夜景风格，保留主体构图与轮廓",
  "model": "nano_banana_pro",
  "size": "1376x768",
  "draft_id": "$DRAFT_ID",
  "image_url": "$REF_IMAGE_URL"
}
JSON
)"

curl -sS -X POST "$API_BASE/v1/generate_ai_image" \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_2"

echo#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT_ID="${1:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ -z "$DRAFT_ID" ]] && echo "Usage: examples/generate_ai_image_ops_demo.sh <draft_id>" && exit 1

API_URL="https://api.vectcut.com/v1/generate_ai_image"

echo "=== TEXT TO IMAGE ==="
PAYLOAD_1=$(cat <<JSON
{
  "prompt": "绘制一张卡通风格教学卡片，主题是光合作用中的二氧化碳循环",
  "model": "nano_banana_pro",
  "size": "1376x768",
  "draft_id": "$DRAFT_ID"
}
JSON
)

curl -sS "$API_URL" \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_1"

echo
echo "=== IMAGE TO IMAGE ==="
PAYLOAD_2=$(cat <<JSON
{
  "prompt": "将这张街景图改成赛博朋克夜景风格，保留建筑结构",
  "model": "nano_banana_pro",
  "size": "1376x768",
  "draft_id": "$DRAFT_ID",
  "image_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000"
}
JSON
)

curl -sS "$API_URL" \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD_2"

echo
echo "Done."
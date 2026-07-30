#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 拉取任务事件日志，支持增量游标，保存到 JSON 文件
#
# 用法：
#   # 全量拉取，保存到默认文件 /tmp/tabtab-events-<task_id>.json
#   TABTAB_TASK_ID=<uuid> bash get-events.sh
#
#   # 从指定事件 ID 之后拉取（增量）
#   TABTAB_TASK_ID=<uuid> TABTAB_FROM_EVENT_ID=<event_id> bash get-events.sh
#
#   # 自定义输出文件
#   TABTAB_TASK_ID=<uuid> TABTAB_EVENTS_FILE=/tmp/my-events.json bash get-events.sh
#
# 环境变量：
#   TABTAB_API_KEY        必填
#   TABTAB_BASE_URL       可选  默认 https://tabtabai.com
#   TABTAB_TASK_ID        必填
#   TABTAB_FROM_EVENT_ID  可选  增量起点事件 ID，空则返回全量
#   TABTAB_EVENTS_FILE    可选  输出文件路径，默认 /tmp/tabtab-events-<task_id>.json
#
# 输出：
#   stdout — 保存的 JSON 文件路径
#   stderr — 进度信息

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY}"
TASK_ID="${TABTAB_TASK_ID:?请设置 TABTAB_TASK_ID}"
FROM="${TABTAB_FROM_EVENT_ID:-}"
OUT_FILE="${TABTAB_EVENTS_FILE:-/tmp/tabtab-events-${TASK_ID}.json}"

URL="$BASE/open/apis/v1/tasks/$TASK_ID/events"
[ -n "$FROM" ] && URL="${URL}?from_event_id=${FROM}"

echo "拉取事件: $URL" >&2
curl -sf "$URL" -H "Authorization: Bearer $KEY" | jq '.' > "$OUT_FILE"

EVENT_COUNT=$(jq '.events | length' "$OUT_FILE")
echo "已保存 $EVENT_COUNT 个事件 → $OUT_FILE" >&2

echo "$OUT_FILE"

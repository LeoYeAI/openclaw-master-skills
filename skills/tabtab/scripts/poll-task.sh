#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 轮询任务直到结束，输出最终状态
#
# 用法：
#   TABTAB_TASK_ID=<uuid> bash poll-task.sh
#   TABTAB_TASK_ID=<uuid> TABTAB_TIMEOUT=300 bash poll-task.sh
#
# 环境变量：
#   TABTAB_API_KEY   必填
#   TABTAB_BASE_URL  可选  默认 https://tabtabai.com
#   TABTAB_TASK_ID   必填
#   TABTAB_INTERVAL  可选  轮询间隔秒数，默认 5
#   TABTAB_TIMEOUT   可选  最大等待秒数，默认 600
#
# 退出码：
#   0  任务 completed
#   1  任务 failed / cancelled / timeout / hitl

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY}"
TASK_ID="${TABTAB_TASK_ID:?请设置 TABTAB_TASK_ID}"
INTERVAL="${TABTAB_INTERVAL:-5}"
TIMEOUT="${TABTAB_TIMEOUT:-600}"

ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
    RESP=$(curl -sf "$BASE/open/apis/v1/tasks/$TASK_ID/status" \
        -H "Authorization: Bearer $KEY")
    STATUS=$(echo "$RESP" | jq -r '.status')
    MSG=$(echo "$RESP" | jq -r '.status_message // ""')

    echo "[${ELAPSED}s] $STATUS${MSG:+ — $MSG}" >&2

    case "$STATUS" in
        completed)
            echo "completed"
            exit 0
            ;;
        failed|cancelled)
            echo "$STATUS"
            exit 1
            ;;
        hitl)
            echo "hitl — 任务等待人工干预，请前往 TabTab UI 处理" >&2
            echo "hitl"
            exit 1
            ;;
    esac

    sleep "$INTERVAL"
    ELAPSED=$((ELAPSED + INTERVAL))
done

echo "timeout — 超过 ${TIMEOUT}s 仍未结束" >&2
echo "timeout"
exit 1

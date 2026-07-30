#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 查询单个任务的状态
#
# 用法：
#   TABTAB_TASK_ID=<uuid> bash get-status.sh
#
# 环境变量：
#   TABTAB_API_KEY   必填
#   TABTAB_BASE_URL  可选  默认 https://tabtabai.com
#   TABTAB_TASK_ID   必填

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY}"
TASK_ID="${TABTAB_TASK_ID:?请设置 TABTAB_TASK_ID}"

curl -sf "$BASE/open/apis/v1/tasks/$TASK_ID/status" \
    -H "Authorization: Bearer $KEY" | jq '.'

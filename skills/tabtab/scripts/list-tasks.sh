#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 列出当前用户的任务
#
# 用法：
#   bash list-tasks.sh
#   TABTAB_PAGE_SIZE=50 bash list-tasks.sh
#
# 环境变量：
#   TABTAB_API_KEY    必填
#   TABTAB_BASE_URL   可选  默认 https://tabtabai.com
#   TABTAB_PAGE       可选  页码，默认 1
#   TABTAB_PAGE_SIZE  可选  每页数量，默认 20（最大 100）

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY}"
PAGE="${TABTAB_PAGE:-1}"
PAGE_SIZE="${TABTAB_PAGE_SIZE:-20}"

curl -sf "$BASE/open/apis/v1/tasks?page=${PAGE}&page_size=${PAGE_SIZE}" \
    -H "Authorization: Bearer $KEY" | jq '.'

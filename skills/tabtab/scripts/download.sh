#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 下载任务沙箱数据为 ZIP 文件
#
# 用法：
#   TABTAB_TASK_ID=<uuid> bash download.sh
#   TABTAB_TASK_ID=<uuid> TABTAB_DIR=output TABTAB_OUT=/tmp/result.zip bash download.sh
#
# 环境变量：
#   TABTAB_API_KEY   必填
#   TABTAB_BASE_URL  可选  默认 https://tabtabai.com
#   TABTAB_TASK_ID   必填
#   TABTAB_DIR       可选  沙箱子目录，空则下载整个沙箱
#   TABTAB_OUT       可选  输出文件路径，默认 /tmp/tabtab-<task_id>.zip
#
# 输出：下载文件的绝对路径（stdout）

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY}"
TASK_ID="${TABTAB_TASK_ID:?请设置 TABTAB_TASK_ID}"
DIR="${TABTAB_DIR:-}"
OUT="${TABTAB_OUT:-/tmp/tabtab-${TASK_ID}.zip}"

URL="$BASE/open/apis/v1/tasks/$TASK_ID/download"
[ -n "$DIR" ] && URL="${URL}?dir=${DIR}"

HTTP_CODE=$(curl -s -o "$OUT" -w "%{http_code}" \
    "$URL" -H "Authorization: Bearer $KEY")

if [ "$HTTP_CODE" != "200" ]; then
    echo "下载失败 HTTP $HTTP_CODE:" >&2
    cat "$OUT" | jq '.' 2>/dev/null || cat "$OUT" >&2
    rm -f "$OUT"
    exit 1
fi

SIZE=$(du -sh "$OUT" | cut -f1)
echo "已下载: $OUT ($SIZE)" >&2

# 仅输出文件路径，便于其他脚本捕获
echo "$OUT"

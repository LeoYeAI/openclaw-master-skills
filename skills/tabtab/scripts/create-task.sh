#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 创建一个 TabTab 任务并输出 task_id
#
# 用法：
#   TABTAB_MESSAGE="分析销售数据" bash create-task.sh
#   TABTAB_MESSAGE="生成报告" TABTAB_MODE="deep_research" bash create-task.sh
#
# 环境变量：
#   TABTAB_API_KEY   必填  sk-… API Key
#   TABTAB_BASE_URL  可选  默认 https://tabtabai.com
#   TABTAB_MESSAGE   必填  任务描述
#   TABTAB_MODE      可选  默认 general（可选 data_analysis/deep_research/ppt/charts/chat_db/html/flash）
#   TABTAB_RUN_MODE  可选  默认 agent（可选 chat）
#   TABTAB_PARAMS    可选  JSON 字符串，额外参数，如 '{"output":"report"}'
#   TABTAB_FILES     可选  JSON 字符串，已上传文件列表，如 '[{"file_id":"...","file_name":"...","content_type":"..."}]'
#   TABTAB_UPLOAD_FILE 可选  文件路径，先上传文件再创建任务（仅单个文件，内部调用 upload-files.sh）

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY 环境变量}"
MSG="${TABTAB_MESSAGE:?请设置 TABTAB_MESSAGE 环境变量}"
MODE="${TABTAB_MODE:-general}"
RUN_MODE="${TABTAB_RUN_MODE:-agent}"
PARAMS="${TABTAB_PARAMS:-{}}"
FILES="${TABTAB_FILES:-[]}"
UPLOAD_FILE="${TABTAB_UPLOAD_FILE:-}"

# 如果提供了 TABTAB_UPLOAD_FILE，先上传文件
if [ -n "$UPLOAD_FILE" ]; then
    echo "正在上传文件: $UPLOAD_FILE" >&2
    UPLOAD_RESP=$(TABTAB_FILES="$UPLOAD_FILE" bash "$(dirname "$0")/upload-files.sh")
    # upload-files.sh 返回 {"files": [...]}，提取 files 数组
    FILES=$(echo "$UPLOAD_RESP" | jq -c '.files')
fi

BODY=$(jq -n \
    --arg message "$MSG" \
    --arg mode "$MODE" \
    --arg run_mode "$RUN_MODE" \
    --argjson params "$PARAMS" \
    --argjson files "$FILES" \
    '{message: $message, mode: $mode, run_mode: $run_mode, params: $params, files: $files}')

RESP=$(curl -sf -X POST "$BASE/open/apis/v1/tasks" \
    -H "Authorization: Bearer $KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY")

TASK_ID=$(echo "$RESP" | jq -r '.task_id')

# 仅输出 task_id，便于其他脚本捕获
echo "$TASK_ID"

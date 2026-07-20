#!/bin/bash
# 任务提醒脚本
# 用途: 每日检查任务清单并发送提醒

set -euo pipefail

TASK_FILE="${1:-tasks/today.json}"
LOG_FILE="logs/reminder_$(date +%Y%m%d).log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

log() { echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"; }

mkdir -p logs tasks

log "检查今日任务..."

if [ ! -f "$TASK_FILE" ]; then
    log "任务文件不存在: $TASK_FILE"
    exit 1
fi

# 读取任务并检查是否到期
TASKS=$(cat "$TASK_FILE")
COUNT=$(echo "$TASKS" | jq 'length')

log "今日任务数量: $COUNT"

# 显示优先级最高的任务
TOP_TASKS=$(echo "$TASKS" | jq -r '.[] | select(.priority <= 1) | "- [\(if .done then "x" else " " fi)] \(.name) (P\(.priority))"' 2>/dev/null || echo "无法解析任务")

echo "=========================================="
echo "今日待办提醒 - $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="
echo "$TOP_TASKS"
echo "=========================================="

# 标记超时任务
OVERDUE=$(echo "$TASKS" | jq -r --arg now "$(date -u +%Y-%m-%d)" \
    '.[] | select(.due_date < $now and .done == false) | "\(.name) - 已超时 (\(.due_date))"' 2>/dev/null || echo "")

if [ -n "$OVERDUE" ]; then
    echo "⚠️  超时任务:"
    echo "$OVERDUE"
fi

log "提醒完成"

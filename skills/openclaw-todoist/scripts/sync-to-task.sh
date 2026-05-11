#!/bin/bash
# Sync Todoist tasks to TASK.md
# Called by heartbeat to keep tasks in sync

set -e

TASK_FILE="$HOME/.openclaw/workspace/TASK.md"
TODOIST_SCRIPT="$HOME/.openclaw/workspace/skills/openclaw-todoist/todoist.sh"
TOKEN_FILE="$HOME/.openclaw/workspace/.todoist-token"

# Skip if Todoist not configured
[ ! -f "$TOKEN_FILE" ] && exit 0

# Get tasks from Todoist API
TOKEN=$(cat "$TOKEN_FILE")
API_BASE="https://api.todoist.com/api/v1"

# Fetch today's tasks and overdue tasks
today=$(date +%Y-%m-%d)
all_tasks=$(curl -s "$API_BASE/tasks" -H "Authorization: Bearer $TOKEN")

today_tasks=$(echo "$all_tasks" | jq -r ".results[] | select(.due.date == \"$today\") | .content" 2>/dev/null || true)
overdue_tasks=$(echo "$all_tasks" | jq -r ".results[] | select(.due.date < \"$today\" and .due.date != null) | \"\(.content) (逾期: \(.due.date))\"" 2>/dev/null || true)
no_due_tasks=$(echo "$all_tasks" | jq -r ".results[] | select(.due.date == null) | .content" 2>/dev/null || true)

# Check if we have any tasks
has_today=$(echo "$today_tasks" | grep -v '^$' | head -1 || true)
has_overdue=$(echo "$overdue_tasks" | grep -v '^$' | head -1 || true)
has_nodue=$(echo "$no_due_tasks" | grep -v '^$' | head -1 || true)

# No tasks at all - remove TASK.md if exists
if [ -z "$has_today" ] && [ -z "$has_overdue" ] && [ -z "$has_nodue" ]; then
    [ -f "$TASK_FILE" ] && rm "$TASK_FILE"
    exit 0
fi

# Build TASK.md content
{
    echo "# 当前任务"
    echo ""
    echo "_自动同步自 Todoist ($(date '+%Y-%m-%d %H:%M'))_"
    echo ""

    if [ -n "$has_overdue" ]; then
        echo "## ⚠️ 逾期任务"
        echo ""
        echo "$overdue_tasks" | while read -r line; do
            [ -n "$line" ] && echo "- [ ] $line"
        done
        echo ""
    fi

    if [ -n "$has_today" ]; then
        echo "## 📅 今日任务"
        echo ""
        echo "$today_tasks" | while read -r line; do
            [ -n "$line" ] && echo "- [ ] $line"
        done
        echo ""
    fi

    if [ -n "$has_nodue" ]; then
        echo "## 📌 待办（无日期）"
        echo ""
        echo "$no_due_tasks" | while read -r line; do
            [ -n "$line" ] && echo "- [ ] $line"
        done
        echo ""
    fi

    echo "---"
    echo "完成或修改任务请使用 Todoist 命令或 App"
} > "$TASK_FILE"

# Return status for heartbeat
if [ -n "$has_overdue" ]; then
    echo "⚠️ 有 $(echo "$overdue_tasks" | grep -v '^$' | wc -l | tr -d ' ') 个逾期任务"
    exit 0
fi
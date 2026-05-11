#!/bin/bash
# Heartbeat task check - runs periodically

IDENTITY_FILE="$HOME/.openclaw/workspace/.agent-identity.json"
TOKEN_FILE="$HOME/.openclaw/workspace/.todoist-token"
LOG_FILE="$HOME/.openclaw/workspace/memory/heartbeat-tasks.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# Check if enabled
if [ ! -f "$TOKEN_FILE" ]; then
    log "⚠️ Todoist token not found"
    exit 0
fi

TOKEN=$(cat "$TOKEN_FILE")
TODAY=$(date +%Y-%m-%d)

# Get identity
INSTANCE_ID=$(cat "$IDENTITY_FILE" | jq -r '.instance_id')
CURRENT_AGENT=$(cat "$IDENTITY_FILE" | jq -r '.current_agent')
AGENT_LABEL=$(cat "$IDENTITY_FILE" | jq -r ".agents.$CURRENT_AGENT.todoist_label")

log "🔍 检查任务 (实例: $INSTANCE_ID, Agent: $CURRENT_AGENT)"

# Get tasks due today
TODAY_TASKS=$(curl -s "https://api.todoist.com/api/v1/tasks" \
    -H "Authorization: Bearer $TOKEN" | \
    jq -r ".results[] | select(.due.date == \"$TODAY\") | .content")

if [ -n "$TODAY_TASKS" ]; then
    log "📅 今日任务:"
    echo "$TODAY_TASKS" | while read task; do
        log "  ⬜ $task"
    done
else
    log "✅ 今日无待办任务"
fi

# Get agent-specific tasks
AGENT_TASKS=$(curl -s "https://api.todoist.com/api/v1/tasks" \
    -H "Authorization: Bearer $TOKEN" | \
    jq -r ".results[] | select(.labels | index(\"$AGENT_LABEL\")) | .content")

if [ -n "$AGENT_TASKS" ]; then
    log ""
    log "🤖 Agent 任务 ($CURRENT_AGENT):"
    echo "$AGENT_TASKS" | while read task; do
        log "  ⬜ $task"
    done
fi

# Get overdue tasks
OVERDUE=$(curl -s "https://api.todoist.com/api/v1/tasks" \
    -H "Authorization: Bearer $TOKEN" | \
    jq -r ".results[] | select(.due.date < \"$TODAY\") | .content")

if [ -n "$OVERDUE" ]; then
    log ""
    log "⚠️ 逾期任务:"
    echo "$OVERDUE" | while read task; do
        log "  🔴 $task"
    done
fi
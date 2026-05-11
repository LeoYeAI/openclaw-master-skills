#!/bin/bash
# Agent Identity Configuration Tool

IDENTITY_FILE="$HOME/.openclaw/workspace/.agent-identity.json"

# Ensure file exists
if [ ! -f "$IDENTITY_FILE" ]; then
    INSTANCE_ID=$(hostname | shasum -a 256 | cut -c1-8)
    cat > "$IDENTITY_FILE" << EOF
{
  "instance_id": "$INSTANCE_ID",
  "instance_name": "$(hostname)",
  "user": "$(whoami)",
  "current_agent": "main",
  "todoist": {
    "daily_reminder_time": "09:00",
    "heartbeat_check_interval_hours": 4
  },
  "agents": {
    "main": {
      "name": "main",
      "full_id": "$INSTANCE_ID:main",
      "todoist_label": "agent-$INSTANCE_ID-main"
    }
  }
}
EOF
    echo "✅ 已创建身份配置: $IDENTITY_FILE"
fi

show_config() {
    echo "📋 当前配置:"
    echo ""
    cat "$IDENTITY_FILE" | jq -C '.'
}

set_reminder_time() {
    local time="$1"
    if [[ ! "$time" =~ ^[0-2][0-9]:[0-5][0-9]$ ]]; then
        echo "❌ 时间格式错误，应为 HH:MM (如 09:00)"
        exit 1
    fi
    cat "$IDENTITY_FILE" | jq ".todoist.daily_reminder_time = \"$time\"" > /tmp/identity.tmp
    mv /tmp/identity.tmp "$IDENTITY_FILE"
    echo "✅ 每日提醒时间已设置为: $time"
}

set_heartbeat_interval() {
    local hours="$1"
    if [[ ! "$hours" =~ ^[0-9]+$ ]]; then
        echo "❌ 间隔应为小时数 (如 4)"
        exit 1
    fi
    cat "$IDENTITY_FILE" | jq ".todoist.heartbeat_check_interval_hours = $hours" > /tmp/identity.tmp
    mv /tmp/identity.tmp "$IDENTITY_FILE"
    echo "✅ 心跳检查间隔已设置为: ${hours} 小时"
}

set_current_agent() {
    local agent="$1"
    # Check if agent exists
    if ! cat "$IDENTITY_FILE" | jq -e ".agents.$agent" > /dev/null 2>&1; then
        echo "❌ Agent 不存在: $agent"
        echo "可用 agents: $(cat "$IDENTITY_FILE" | jq -r '.agents | keys[]' | tr '\n' ' ')"
        exit 1
    fi
    cat "$IDENTITY_FILE" | jq ".current_agent = \"$agent\"" > /tmp/identity.tmp
    mv /tmp/identity.tmp "$IDENTITY_FILE"
    echo "✅ 当前 Agent 已切换为: $agent"
}

add_agent() {
    local name="$1"
    local instance_id=$(cat "$IDENTITY_FILE" | jq -r '.instance_id')
    local label="agent-$instance_id-$name"
    
    cat "$IDENTITY_FILE" | jq ".agents.$name = {\"name\": \"$name\", \"full_id\": \"$instance_id:$name\", \"todoist_label\": \"$label\"}" > /tmp/identity.tmp
    mv /tmp/identity.tmp "$IDENTITY_FILE"
    echo "✅ 已添加 Agent: $name (标签: $label)"
    
    # Create label in Todoist
    TOKEN=$(cat ~/.openclaw/workspace/.todoist-token 2>/dev/null)
    if [ -n "$TOKEN" ]; then
        curl -s -X POST "https://api.todoist.com/api/v1/labels" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"$label\"}" > /dev/null 2>&1
        echo "   已在 Todoist 创建标签"
    fi
}

case "${1:-show}" in
    show|config)
        show_config
        ;;
    set-time)
        set_reminder_time "$2"
        ;;
    set-interval)
        set_heartbeat_interval "$2"
        ;;
    set-agent)
        set_current_agent "$2"
        ;;
    add-agent)
        add_agent "$2"
        ;;
    *)
        echo "用法: agent-config.sh <command> [args]"
        echo ""
        echo "Commands:"
        echo "  show              显示当前配置"
        echo "  set-time HH:MM    设置每日提醒时间"
        echo "  set-interval N    设置心跳检查间隔(小时)"
        echo "  set-agent <name>  切换当前 Agent"
        echo "  add-agent <name>  添加新 Agent"
        ;;
esac
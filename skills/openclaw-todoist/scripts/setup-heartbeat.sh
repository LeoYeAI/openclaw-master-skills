#!/bin/bash
# Setup Todoist heartbeat checks in HEARTBEAT.md

HEARTBEAT_FILE="$HOME/.openclaw/workspace/HEARTBEAT.md"
TODOIST_CHECK='~/.openclaw/workspace/skills/todoist/todoist.sh'

# Check if already configured
if grep -q "todoist.sh list" "$HEARTBEAT_FILE" 2>/dev/null; then
    echo "✅ Todoist 心跳检查已配置"
    exit 0
fi

# Create or append to HEARTBEAT.md
if [ ! -f "$HEARTBEAT_FILE" ]; then
    cat > "$HEARTBEAT_FILE" << 'EOF'
# 心跳任务

## 每次心跳检查

1. **Todoist 任务**
   - 检查今日任务
   - 检查过期任务
   - 有紧急事项时提醒用户

```bash
~/.openclaw/workspace/skills/todoist/todoist.sh list today
~/.openclaw/workspace/skills/todoist/todoist.sh list overdue
```

## 静默条件
- 无任务时回复 HEARTBEAT_OK
- 有过期任务或重要截止日期时主动提醒
EOF
    echo "✅ 已创建 HEARTBEAT.md 并配置 Todoist 心跳检查"
else
    # Append to existing file
    cat >> "$HEARTBEAT_FILE" << 'EOF'

## Todoist 任务检查

```bash
~/.openclaw/workspace/skills/todoist/todoist.sh list today
~/.openclaw/workspace/skills/todoist/todoist.sh list overdue
```

有紧急事项时主动提醒，否则静默。
EOF
    echo "✅ 已添加 Todoist 心跳检查到现有 HEARTBEAT.md"
fi

echo ""
echo "📌 下次心跳时会自动检查 Todoist 任务"
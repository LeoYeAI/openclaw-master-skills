#!/usr/bin/env bash
set -euo pipefail

# agent-autopilot 初始化脚本
# 用法: bash init.sh <agent工作空间路径>
# 示例: bash init.sh ~/.openclaw/workspace-wangyi

WORKSPACE="${1:?用法: bash init.sh <agent工作空间路径>}"
MAIN_WORKSPACE="$HOME/.openclaw/workspace"
TODO_SKILL="todo-management"

echo "🚀 agent-autopilot 初始化: $WORKSPACE"

# 1. 确保工作空间存在
mkdir -p "$WORKSPACE/skills" "$WORKSPACE/memory"

# 2. 检查并安装 todo-management skill
if [ -d "$WORKSPACE/skills/$TODO_SKILL" ]; then
    echo "✅ $TODO_SKILL 已存在"
else
    # 从主工作空间复制
    if [ -d "$MAIN_WORKSPACE/skills/$TODO_SKILL" ]; then
        cp -r "$MAIN_WORKSPACE/skills/$TODO_SKILL" "$WORKSPACE/skills/$TODO_SKILL"
        echo "✅ $TODO_SKILL 已从主工作空间复制"
    else
        # 尝试全局 skills 目录
        GLOBAL_SKILLS="$(npm root -g 2>/dev/null)/openclaw/skills/$TODO_SKILL"
        if [ -d "$GLOBAL_SKILLS" ]; then
            cp -r "$GLOBAL_SKILLS" "$WORKSPACE/skills/$TODO_SKILL"
            echo "✅ $TODO_SKILL 已从全局安装复制"
        else
            echo "❌ 找不到 $TODO_SKILL skill，请先安装"
            exit 1
        fi
    fi
fi

# 3. 检查 todo.db 是否存在（不存在会在首次使用时自动创建）
if [ -f "$WORKSPACE/todo.db" ]; then
    echo "✅ todo.db 已存在"
else
    echo "ℹ️  todo.db 将在首次使用 todo.sh 时自动创建"
fi

# 4. 初始化 report-state.json（汇报 + 记忆维护状态跟踪）
REPORT_STATE="$WORKSPACE/memory/report-state.json"
if [ -f "$REPORT_STATE" ]; then
    echo "✅ report-state.json 已存在"
else
    cat > "$REPORT_STATE" << 'EOF'
{
  "lastReportTime": null,
  "lastReportDate": null,
  "todayReportCount": 0,
  "lastMemoryReview": null
}
EOF
    echo "✅ report-state.json 已创建"
fi

# 5. 检查核心文件
for f in IDENTITY.md SOUL.md USER.md MEMORY.md HEARTBEAT.md; do
    if [ -f "$WORKSPACE/$f" ]; then
        echo "✅ $f 已存在"
    else
        echo "⚠️  缺少 $f — 需要手动创建"
    fi
done

echo ""
echo "🎯 初始化完成！"
echo "   下一步："
echo "   1. 确保 IDENTITY.md / SOUL.md / USER.md / MEMORY.md / HEARTBEAT.md 已配置"
echo "   2. 参考 references/example-setup.md 了解配置模板"
echo "   3. 在 HEARTBEAT.md 中设定汇报间隔（白天每 N 小时）"
echo "   4. 用 todo.sh 创建初始任务"

#!/bin/bash
# 会话快速恢复脚本
# 功能：一键恢复会话上下文

echo "⚡ 会话快速恢复..."
echo "=================="
echo ""

# 1. 显示 STATUS.md（状态看板）
echo "📊 当前状态："
echo "----------------------------------------"
if [ -f "STATUS.md" ]; then
    head -30 STATUS.md
else
    echo "⚠️  STATUS.md 不存在"
fi
echo ""

# 2. 显示待办事项
echo "📋 待办事项："
echo "----------------------------------------"
grep -A 20 "## 📋 待办" STATUS.md 2>/dev/null || echo "无待办事项"
echo ""

# 3. 显示最近工作记录
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="memory/$TODAY.md"

if [ -f "$MEMORY_FILE" ]; then
    echo "📝 今日工作 ($TODAY)："
    echo "----------------------------------------"
    head -50 "$MEMORY_FILE"
else
    echo "⚠️  今日工作记录不存在: $MEMORY_FILE"
fi

echo ""
echo "=================="
echo "✅ 恢复完成！"
echo ""
echo "📚 详细文档："
echo "   • 快速索引: QUICK_RECOVERY.md"
echo "   • 详细记录: memory/$TODAY.md"
echo "   • 优化建议: SESSION_RECOVERY_OPTIMIZATION.md"

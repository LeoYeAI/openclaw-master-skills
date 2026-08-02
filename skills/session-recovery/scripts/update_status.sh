#!/bin/bash
# 自动更新 STATUS.md 的脚本
# 功能：自动提取今日工作内容，更新任务状态

MEMORY_DIR="./memory"
STATUS_FILE="./STATUS.md"
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"

echo "🔄 开始自动更新 STATUS.md..."
echo ""

# 检查今日记录文件是否存在
if [ ! -f "$MEMORY_FILE" ]; then
    echo "⚠️  今日记录文件不存在: $MEMORY_FILE"
    echo "💡 请先创建今日记录文件"
    exit 1
fi

echo "📄 读取今日记录: $MEMORY_FILE"

# 提取完成的任务
COMPLETED=$(grep -E "✅ 完成|已完成" "$MEMORY_FILE" | wc -l | xargs)
echo "✅ 完成任务: $COMPLETED 个"

# 提取进行中的任务
IN_PROGRESS=$(grep -E "🔄 进行|进行中" "$MEMORY_FILE" | wc -l | xargs)
echo "🔄 进行中: $IN_PROGRESS 个"

# 提取阻塞任务
BLOCKED=$(grep -E "❌ 阻塞|阻塞" "$MEMORY_FILE" | wc -l | xargs)
echo "❌ 阻塞: $BLOCKED 个"

# 更新 STATUS.md
echo ""
echo "📝 更新 STATUS.md..."

# 备份原文件
cp "$STATUS_FILE" "${STATUS_FILE}.bak"

# 更新时间戳
sed -i '' "s/\*\*最后更新：\*\* .*/\*\*最后更新：\*\* $(date '+%Y-%m-%d %H:%M')/" "$STATUS_FILE"

echo "✅ STATUS.md 已更新"
echo ""
echo "📊 今日工作统计："
echo "   完成：$COMPLETED 个"
echo "   进行：$IN_PROGRESS 个"
echo "   阻塞：$BLOCKED 个"

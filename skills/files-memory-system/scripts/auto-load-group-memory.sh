#!/bin/bash
# auto-load-group-memory.sh - 自动加载群记忆（带防重复标记）
#
# 用法: ./auto-load-group-memory.sh <channel> <group_id>
#
# 功能:
# - 检查今天是否已经加载过群记忆
# - 如果没有，加载 GLOBAL.md + 今日/昨日记录
# - 创建标记文件避免重复加载

set -e

CHANNEL="${1:-feishu}"
GROUP_ID="${2:-}"

if [ -z "$GROUP_ID" ]; then
    echo "❌ 错误: 需要提供 group_id"
    echo "用法: $0 <channel> <group_id>"
    exit 1
fi

GROUP_DIR="memory/group_${CHANNEL}_${GROUP_ID}"
MARKER_FILE="${GROUP_DIR}/.memory-loaded"
TODAY=$(date +%Y-%m-%d)

# 检查是否已经加载过（今天）
if [ -f "$MARKER_FILE" ]; then
    LAST_LOADED=$(cat "$MARKER_FILE" 2>/dev/null || echo "")
    if [ "$LAST_LOADED" = "$TODAY" ]; then
        echo "✅ 群记忆今天已加载 ($TODAY)"
        exit 0
    fi
fi

# 加载群记忆
echo "📚 正在加载群记忆..."

if [ -f "${GROUP_DIR}/GLOBAL.md" ]; then
    echo "✅ GLOBAL.md"
fi

if [ -f "${GROUP_DIR}/${TODAY}.md" ]; then
    echo "✅ ${TODAY}.md (今日)"
fi

YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
if [ -f "${GROUP_DIR}/${YESTERDAY}.md" ]; then
    echo "✅ ${YESTERDAY}.md (昨日)"
fi

if [ -f "memory/global/GLOBAL.md" ]; then
    echo "✅ global/GLOBAL.md"
fi

# 更新标记
echo "$TODAY" > "$MARKER_FILE"
echo "📝 已更新加载标记: $MARKER_FILE"

echo "✅ 群记忆加载完成"
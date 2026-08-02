#!/bin/bash
# ensure-private-memory.sh - 确保私聊记忆目录存在（方案 B：按需自动创建）
# 当检测到私聊上下文时调用，自动初始化缺失的目录和文件

set -e

PRIVATE_DIR="${1:-memory/private}"
TODAY=$(date +%Y-%m-%d)

echo "🔍 检查私聊记忆目录..."

# 创建基础目录
if [ ! -d "$PRIVATE_DIR" ]; then
    echo "⚠️  私聊记忆目录不存在，正在初始化..."
    mkdir -p "$PRIVATE_DIR"
    echo "✅ 创建 $PRIVATE_DIR"
fi

# 创建 GLOBAL.md（如果不存在）
if [ ! -f "$PRIVATE_DIR/GLOBAL.md" ]; then
    cat > "$PRIVATE_DIR/GLOBAL.md" << EOF
# GLOBAL.md - 私聊记忆

## 私聊信息
- **类型**: 1对1私聊
- **用途**: 记录私聊中的重要信息和对话

## 重要信息
_(私聊中的重要决定、偏好设置、个人笔记等)_

## 常用资源
_(私聊中分享的链接、工具、参考资料等)_

## 跨群组资源

📚 **跨群组全局记忆**: \`memory/global/GLOBAL.md\`

包含跨所有群组共享的信息。

---
Last updated: $TODAY
EOF
    echo "✅ 创建 $PRIVATE_DIR/GLOBAL.md"
fi

# 创建今日记录文件（如果不存在）
if [ ! -f "$PRIVATE_DIR/$TODAY.md" ]; then
    cat > "$PRIVATE_DIR/$TODAY.md" << EOF
# $TODAY - 私聊记录

## 今日概要
_(简要总结今天的重要事项)_

## 详细记录

### 事件/话题 1
_(详细描述)_

## 学到的/记住的
_(值得记录的经验、决策、信息)_

---
Stored at: $(date '+%Y-%m-%d %H:%M:%S')
Location: $PRIVATE_DIR/
EOF
    echo "✅ 创建 $PRIVATE_DIR/$TODAY.md"
fi

# 如果需要 repos 子目录，也确保它存在
if [ ! -d "$PRIVATE_DIR/repos" ]; then
    mkdir -p "$PRIVATE_DIR/repos"
    echo "✅ 创建 $PRIVATE_DIR/repos"
fi

echo "✅ 私聊记忆目录检查完成"

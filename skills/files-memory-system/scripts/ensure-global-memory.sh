#!/bin/bash
# ensure-global-memory.sh - 确保全局记忆目录存在（方案 B：按需自动创建）
# 当需要记录跨群组信息时调用，自动初始化缺失的目录和文件

set -e

GLOBAL_DIR="${1:-memory/global}"
TODAY=$(date +%Y-%m-%d)

echo "🔍 检查全局记忆目录: ${GLOBAL_DIR}..."

# 创建基础目录
if [ ! -d "$GLOBAL_DIR" ]; then
    echo "⚠️  全局目录不存在，正在初始化..."
    mkdir -p "$GLOBAL_DIR"
    echo "✅ 创建 ${GLOBAL_DIR}"
fi

# 创建 GLOBAL.md（如果不存在）
if [ ! -f "$GLOBAL_DIR/GLOBAL.md" ]; then
    cat > "$GLOBAL_DIR/GLOBAL.md" << EOF
# GLOBAL.md - 跨群组全局记忆

## 概述
本文件包含跨所有群组共享的信息，所有群组都可以访问。

## 重要工具与凭证

_(记录跨群组的工具链接、配置说明、共享资源等)_

## 跨群组通用规则

_(所有群组都应遵守的规则和标准)_

## 全局项目

_(跨群组共享的项目信息)_

---
Last updated: ${TODAY}
EOF
    echo "✅ 创建 ${GLOBAL_DIR}/GLOBAL.md"
fi

# 创建今日记录文件（如果不存在）
if [ ! -f "$GLOBAL_DIR/${TODAY}.md" ]; then
    cat > "$GLOBAL_DIR/${TODAY}.md" << EOF
# ${TODAY} - 全局记录

## 今日概要
_(简要总结今天的跨群组事项)_

## 详细记录

### 事件/话题 1
_(详细描述)_

## 学到的/记住的
_(值得记录的全局经验、决策、信息)_

---
Stored at: $(date '+%Y-%m-%d %H:%M:%S')
Location: ${GLOBAL_DIR}/
EOF
    echo "✅ 创建 ${GLOBAL_DIR}/${TODAY}.md"
fi

echo "✅ 全局记忆目录检查完成"

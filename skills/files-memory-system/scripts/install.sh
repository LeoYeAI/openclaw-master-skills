#!/bin/bash
# install.sh - Install files-memory-system to standard location with self-registration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="/workspace/skills/files-memory-system"

echo "🧠 Installing files-memory-system..."

# 检查是否在正确的上下文
if [ ! -d "/workspace" ]; then
    echo "❌ Error: /workspace not found"
    echo "   This skill must be installed in an OpenClaw workspace"
    exit 1
fi

# 创建目标目录
mkdir -p /workspace/skills

# 初始化私聊记忆目录（方案 A：安装时自动创建）
echo "📝 初始化私聊记忆目录..."
mkdir -p /workspace/memory/private
if [ ! -f "/workspace/memory/private/GLOBAL.md" ]; then
    cat > /workspace/memory/private/GLOBAL.md << EOF
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
Last updated: $(date +%Y-%m-%d)
EOF
    echo "✅ 创建 /workspace/memory/private/GLOBAL.md"
else
    echo "✅ 私聊记忆目录已存在"
fi

# 初始化全局记忆目录（方案 A：安装时自动创建）
echo "📝 初始化全局记忆目录..."
mkdir -p /workspace/memory/global
if [ ! -f "/workspace/memory/global/GLOBAL.md" ]; then
    cat > /workspace/memory/global/GLOBAL.md << EOF
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
Last updated: $(date +%Y-%m-%d)
EOF
    echo "✅ 创建 /workspace/memory/global/GLOBAL.md"
else
    echo "✅ 全局记忆目录已存在"
fi

# 复制 skill 到标准位置
if [ -d "$TARGET_DIR" ]; then
    echo ""
    echo "⚠️  检测到已存在的安装"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "目标目录: $TARGET_DIR"
    echo "目录内容:"
    ls -la "$TARGET_DIR" | head -10
    echo ""
    echo "❓ 为什么要删除?"
    echo "   重新安装/升级需要删除旧版本，避免文件冲突"
    echo "   删除后将从当前目录复制最新版本"
    echo ""
    echo "⚠️  即将删除: $TARGET_DIR"
    echo "   (仅删除此 skill 目录，不影响记忆数据和其他文件)"
    echo ""
    read -p "   确认删除并重新安装? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "   已取消，保留现有版本"
        exit 0
    fi
    echo "   正在删除: $TARGET_DIR ..."
    # 使用 trash 命令安全删除（移到回收站），如不可用则回退到 rm
    if command -v trash &> /dev/null; then
        trash "$TARGET_DIR"
        echo "   ✅ 已移至回收站 (trash)"
    else
        rm -rf "$TARGET_DIR"
        echo "   ✅ 已删除 (rm -rf)"
    fi
fi

cp -r "$SCRIPT_DIR/.." "$TARGET_DIR"
echo "✅ Copied skill to $TARGET_DIR"

# 运行自注册
cd "$TARGET_DIR"
if [ -f "scripts/post-install.sh" ]; then
    bash scripts/post-install.sh
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. The agent will now auto-discover files-memory-system on startup"
echo "2. Check AGENTS.md to see the registration"
echo "3. Initialize your first group memory with:"
echo "   ./scripts/init-group-memory.sh <channel> <group-id> <name>"

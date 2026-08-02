#!/bin/bash
# ensure-group-memory.sh - 确保群组记忆目录存在（方案 B：按需自动创建）
# 当检测到群组上下文时调用，自动初始化缺失的目录和文件

set -e

GROUP_CHANNEL="${1:-feishu}"
GROUP_ID="${2:-}"
GROUP_NAME="${3:-}"

if [ -z "$GROUP_ID" ]; then
    echo "❌ 错误: 需要提供群组 ID"
    echo "用法: $0 <channel> <group_id> [group_name]"
    echo "示例: $0 feishu oc_xxx '小说创作群组'"
    exit 1
fi

GROUP_DIR="memory/group_${GROUP_CHANNEL}_${GROUP_ID}"
TODAY=$(date +%Y-%m-%d)

echo "🔍 检查群组记忆目录: ${GROUP_DIR}..."

# 创建基础目录
if [ ! -d "$GROUP_DIR" ]; then
    echo "⚠️  群组目录不存在，正在初始化..."
    mkdir -p "$GROUP_DIR"
    echo "✅ 创建 ${GROUP_DIR}"
fi

# 确保子目录存在
mkdir -p "$GROUP_DIR/skills"
mkdir -p "$GROUP_DIR/repos"
echo "✅ 确保 skills/ 和 repos/ 子目录存在"

# 创建 GLOBAL.md（如果不存在）
if [ ! -f "$GROUP_DIR/GLOBAL.md" ]; then
    cat > "$GROUP_DIR/GLOBAL.md" << EOF
# GLOBAL.md - ${GROUP_NAME:-群组 ${GROUP_ID}}

## 群组信息
- **主题**: ${GROUP_NAME:-待填写}
- **平台**: ${GROUP_CHANNEL}
- **ID**: ${GROUP_ID}

## 关键信息
_(重要规则、常用信息、决策记录等)_

## 成员
_(重要成员信息)_

## 常用资源
_(工具链接、参考资料、模板等)_

## 重要决策
_(群组内做出的重要决定)_

## 已安装的群组专属 Skills

| Skill | 版本 | 来源 | 描述 |
|-------|------|------|------|
| _(待添加)_ | - | - | - |

## 群组项目 (repos/)

| 项目名称 | 类型 | 描述 | 位置 |
|---------|------|------|------|
| _(待添加)_ | own/cloned | - | repos/xxx/ |

## 跨群组资源

📚 **跨群组全局记忆**: \`memory/global/GLOBAL.md\`

包含跨所有群组共享的信息。

---
Last updated: ${TODAY}
EOF
    echo "✅ 创建 ${GROUP_DIR}/GLOBAL.md"
fi

# 创建今日记录文件（如果不存在）
if [ ! -f "$GROUP_DIR/${TODAY}.md" ]; then
    cat > "$GROUP_DIR/${TODAY}.md" << EOF
# ${TODAY} - 群组记录

## 今日概要
_(简要总结今天的重要事项)_

## 详细记录

### 事件/话题 1
_(详细描述)_

## 学到的/记住的
_(值得记录的经验、决策、信息)_

---
Stored at: $(date '+%Y-%m-%d %H:%M:%S')
Location: ${GROUP_DIR}/
EOF
    echo "✅ 创建 ${GROUP_DIR}/${TODAY}.md"
fi

echo "✅ 群组记忆目录检查完成"

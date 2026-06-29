#!/bin/bash
# init-group-memory.sh - 初始化群组记忆结构

GROUP_CHANNEL="$1"  # e.g., "feishu"
GROUP_ID="$2"       # e.g., "oc_xxx"
GROUP_NAME="$3"     # e.g., "小说创作群组"

if [ -z "$GROUP_CHANNEL" ] || [ -z "$GROUP_ID" ]; then
    echo "Usage: $0 <channel> <group_id> [group_name]"
    echo "Example: $0 feishu oc_xxx '小说创作群组'"
    exit 1
fi

GROUP_DIR="memory/group_${GROUP_CHANNEL}_${GROUP_ID}"

echo "📁 创建群组记忆目录: ${GROUP_DIR}"
mkdir -p "${GROUP_DIR}/skills"
mkdir -p "${GROUP_DIR}/repos"

echo "📝 创建 GLOBAL.md..."
cat > "${GROUP_DIR}/GLOBAL.md" << EOF
# GLOBAL.md - ${GROUP_NAME:-群组}

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
Last updated: $(date +%Y-%m-%d)
EOF

echo "📝 创建今日记录文件..."
TODAY=$(date +%Y-%m-%d)
cat > "${GROUP_DIR}/${TODAY}.md" << EOF
# ${TODAY} - 群组初始化

## 今日概要
群组记忆系统初始化完成。

## 详细记录

### 群组信息
- **主题**: ${GROUP_NAME:-待填写}
- **平台**: ${GROUP_CHANNEL}
- **ID**: ${GROUP_ID}

---
Stored at: $(date '+%Y-%m-%d %H:%M:%S')
Location: ${GROUP_DIR}/
EOF

echo "✅ 群组记忆初始化完成！"
echo ""
echo "📂 目录结构:"
tree -L 2 "${GROUP_DIR}" 2>/dev/null || ls -la "${GROUP_DIR}"

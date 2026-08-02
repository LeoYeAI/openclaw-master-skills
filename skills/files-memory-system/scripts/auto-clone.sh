#!/bin/bash
# auto-clone.sh - 自动克隆项目到正确的目录
# 根据当前上下文决定克隆位置
#
# 用法:
#   方式1 - 参数传入 (推荐):
#     ./auto-clone.sh --group <channel> <group_id> <repo_url> [project_name]
#
#   方式2 - 参数传入 (私聊):
#     ./auto-clone.sh --private <repo_url> [project_name]
#
#   方式3 - 环境变量 (向后兼容):
#     GROUP_ID="oc_xxx" CHANNEL="feishu" ./auto-clone.sh <repo_url> [project_name]
#
#   方式4 - 全局 (无上下文):
#     ./auto-clone.sh <repo_url> [project_name]

set -e

# 解析参数
GROUP_CHANNEL=""
GROUP_ID=""
IS_PRIVATE=""
REPO_URL=""
PROJECT_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --group)
            GROUP_CHANNEL="$2"
            GROUP_ID="$3"
            shift 3
            ;;
        --private)
            IS_PRIVATE="1"
            shift
            ;;
        --help|-h)
            echo "用法: $0 [选项] <repo_url> [project_name]"
            echo ""
            echo "选项:"
            echo "  --group <channel> <group_id>  克隆到指定群组目录"
            echo "  --private                    克隆到私聊目录"
            echo "  --help, -h                   显示帮助"
            echo ""
            echo "示例:"
            echo "  $0 --group feishu oc_xxx https://github.com/user/repo"
            echo "  $0 --private https://github.com/user/repo my-project"
            echo "  $0 https://github.com/user/repo  # 克隆到全局 repos/"
            exit 0
            ;;
        -*)
            echo "❌ 未知选项: $1"
            echo "用法: $0 --help 查看帮助"
            exit 1
            ;;
        *)
            # 第一个非选项参数是 repo_url
            if [ -z "$REPO_URL" ]; then
                REPO_URL="$1"
            else
                # 第二个非选项参数是 project_name
                PROJECT_NAME="$1"
            fi
            shift
            ;;
    esac
done

# 验证必需参数
if [ -z "$REPO_URL" ]; then
    echo "❌ 错误: 需要提供仓库 URL"
    echo "用法: $0 [选项] <repo_url> [project_name]"
    exit 1
fi

# 如果 project_name 没提供，从 URL 提取
if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME=$(basename "$REPO_URL" .git)
fi

# 如果命令行没传，从环境变量获取 (向后兼容)
if [ -z "$GROUP_CHANNEL" ] && [ -n "$CHANNEL" ]; then
    GROUP_CHANNEL="$CHANNEL"
fi
if [ -z "$GROUP_ID" ] && [ -n "$GROUP_ID" ]; then
    # 注意：这里用 GROUP_ID 环境变量
    GROUP_ID="$GROUP_ID"
fi

# 确定目标位置
if [ -n "$GROUP_CHANNEL" ] && [ -n "$GROUP_ID" ]; then
    # 在群组上下文中 - 先确保目录存在
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$SCRIPT_DIR/ensure-group-memory.sh" "$GROUP_CHANNEL" "$GROUP_ID"

    GROUP_DIR="memory/group_${GROUP_CHANNEL}_${GROUP_ID}"
    TARGET_DIR="${GROUP_DIR}/repos/${PROJECT_NAME}"

    echo "📁 检测到群组上下文，克隆到: ${TARGET_DIR}"

elif [ -n "$IS_PRIVATE" ]; then
    # 在私聊上下文中 - 先确保目录存在
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$SCRIPT_DIR/ensure-private-memory.sh"

    PRIVATE_DIR="memory/private"
    TARGET_DIR="${PRIVATE_DIR}/repos/${PROJECT_NAME}"

    echo "📁 检测到私聊上下文，克隆到: ${TARGET_DIR}"

else
    # 默认到全局 - 先确保全局记忆目录存在
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$SCRIPT_DIR/ensure-global-memory.sh"

    TARGET_DIR="repos/${PROJECT_NAME}"

    # 确保目录存在
    mkdir -p "repos"

    echo "📁 未检测到特定上下文，克隆到全局: ${TARGET_DIR}"
fi

# 检查目标是否已存在
if [ -d "$TARGET_DIR" ]; then
    echo "⚠️  目标目录已存在: ${TARGET_DIR}"
    echo "💡 如需重新克隆，请先删除该目录"
    exit 1
fi

# 克隆
echo "🔄 正在克隆 ${REPO_URL}..."
git clone "$REPO_URL" "$TARGET_DIR"

echo ""
echo "✅ 克隆完成: ${TARGET_DIR}"
echo "📝 记得更新 GLOBAL.md 记录此项目！"
echo ""
echo "项目内容:"
ls -la "$TARGET_DIR"
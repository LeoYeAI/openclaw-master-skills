#!/bin/bash
# create_workspace.sh — 创建 Agent workspace 目录结构
# 用法：bash create_workspace.sh <agentId> [--type human|functional]
#
# --type human       人伴型 Agent（默认）：创建完整骨架，包含 USER.md / BOOTSTRAP.md 占位提示
# --type functional  功能型 Agent：只创建核心文件，跳过 USER.md / BOOTSTRAP.md

set -e

AGENT_ID="${1}"
if [ -z "$AGENT_ID" ]; then
  echo "❌ 用法：bash create_workspace.sh <agentId> [--type human|functional]"
  exit 1
fi

# 解析 --type 参数（默认 human）
AGENT_TYPE="human"
shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      AGENT_TYPE="$2"
      shift 2
      ;;
    *)
      echo "❌ 未知参数：$1"
      exit 1
      ;;
  esac
done

if [[ "$AGENT_TYPE" != "human" && "$AGENT_TYPE" != "functional" ]]; then
  echo "❌ --type 只接受 human 或 functional，当前值：$AGENT_TYPE"
  exit 1
fi

BASE_DIR="$HOME/.openclaw/agency-agents"
WORKSPACE="$BASE_DIR/$AGENT_ID"

if [ -d "$WORKSPACE" ]; then
  echo "⚠️  workspace 已存在：$WORKSPACE"
  read -p "继续会覆盖部分文件，确认？(y/N) " confirm
  [[ "$confirm" != "y" ]] && echo "已取消" && exit 0
fi

echo "=== 创建 workspace: $WORKSPACE ==="
echo "=== Agent 类型: $AGENT_TYPE ==="

mkdir -p "$WORKSPACE/memory"
mkdir -p "$WORKSPACE/skills"

echo "✅ 目录结构创建完成"
echo ""

if [ "$AGENT_TYPE" = "human" ]; then
  echo "接下来需要写入的文件（人伴型 Agent）："
  echo "  $WORKSPACE/IDENTITY.md"
  echo "  $WORKSPACE/SOUL.md          ← 骨架，BOOTSTRAP 阶段填充"
  echo "  $WORKSPACE/AGENTS.md"
  echo "  $WORKSPACE/TOOLS.md"
  echo "  $WORKSPACE/USER.md          ← 骨架，BOOTSTRAP 阶段填充"
  echo "  $WORKSPACE/MEMORY.md"
  echo "  $WORKSPACE/HEARTBEAT.md"
  echo "  $WORKSPACE/BOOTSTRAP.md     ← 动态对话协议，首次对话后自删"
else
  echo "接下来需要写入的文件（功能型 Agent）："
  echo "  $WORKSPACE/IDENTITY.md"
  echo "  $WORKSPACE/SOUL.md          ← 直接写完整版，体现专业判断倾向"
  echo "  $WORKSPACE/AGENTS.md        ← 重点写任务接口规范"
  echo "  $WORKSPACE/TOOLS.md"
  echo "  $WORKSPACE/MEMORY.md"
  echo "  $WORKSPACE/HEARTBEAT.md"
  echo ""
  echo "⚠️  功能型 Agent 不需要 USER.md 和 BOOTSTRAP.md"
fi

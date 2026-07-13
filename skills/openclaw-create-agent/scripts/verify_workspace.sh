#!/bin/bash
# verify_workspace.sh — 验证 Agent workspace 文件完整性
# 用法：bash verify_workspace.sh <agentId> [--type human|functional]
#
# Phase 4 收尾时调用，确认 workspace 不只是空骨架。
# 检查必须文件是否存在、是否有实质内容（不是空文件或纯模板）。

set -e

AGENT_ID="${1}"
if [ -z "$AGENT_ID" ]; then
  echo "❌ 用法：bash verify_workspace.sh <agentId> [--type human|functional]"
  exit 1
fi

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

WORKSPACE="$HOME/.openclaw/agency-agents/$AGENT_ID"

if [ ! -d "$WORKSPACE" ]; then
  echo "❌ workspace 不存在：$WORKSPACE"
  exit 1
fi

echo "=== 验证 workspace: $WORKSPACE ==="
echo "=== Agent 类型: $AGENT_TYPE ==="
echo ""

PASS=0
FAIL=0

check_file() {
  local filepath="$1"
  local label="$2"
  local min_lines="${3:-3}"   # 默认至少 3 行有实质内容

  if [ ! -f "$filepath" ]; then
    echo "  ❌ 缺失：$label"
    FAIL=$((FAIL + 1))
    return
  fi

  # 统计非空、非注释行数
  local content_lines
  content_lines=$(grep -cv '^\s*$\|^\s*#\|^\s*>\|^---' "$filepath" 2>/dev/null || true)

  if [ "$content_lines" -lt "$min_lines" ]; then
    echo "  ⚠️  疑似空骨架（有效行 ${content_lines} < ${min_lines}）：$label"
    FAIL=$((FAIL + 1))
  else
    echo "  ✅ $label（有效行 ${content_lines}）"
    PASS=$((PASS + 1))
  fi
}

# ── 两类 Agent 共同必须文件 ──
echo "[ 公共文件 ]"
check_file "$WORKSPACE/IDENTITY.md"   "IDENTITY.md"  2
check_file "$WORKSPACE/SOUL.md"       "SOUL.md"       8
check_file "$WORKSPACE/AGENTS.md"     "AGENTS.md"     8
check_file "$WORKSPACE/TOOLS.md"      "TOOLS.md"      3
check_file "$WORKSPACE/MEMORY.md"     "MEMORY.md"     4
check_file "$WORKSPACE/HEARTBEAT.md"  "HEARTBEAT.md"  3

# ── 人伴型专属 ──
if [ "$AGENT_TYPE" = "human" ]; then
  echo ""
  echo "[ 人伴型专属 ]"
  check_file "$WORKSPACE/USER.md"     "USER.md"       3

  # BOOTSTRAP.md 在初次对话完成后会被删除，这里只检查"要么存在要么已完成"
  if [ -f "$WORKSPACE/BOOTSTRAP.md" ]; then
    echo "  ℹ️  BOOTSTRAP.md 存在（首次对话尚未完成，属正常）"
  else
    echo "  ✅ BOOTSTRAP.md 已删除（首次对话已完成）"
    PASS=$((PASS + 1))
  fi
fi

# ── memory/ 目录 ──
echo ""
echo "[ 目录结构 ]"
if [ -d "$WORKSPACE/memory" ]; then
  echo "  ✅ memory/ 目录存在"
  PASS=$((PASS + 1))
else
  echo "  ❌ memory/ 目录缺失"
  FAIL=$((FAIL + 1))
fi

# ── 汇总 ──
echo ""
echo "=== 验证结果 ==="
echo "  通过：$PASS　失败/警告：$FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✅ workspace 完整，可以继续 Phase 4 重启验证。"
  exit 0
else
  echo "❌ 有 $FAIL 项未通过，请补充缺失内容后重新验证。"
  exit 1
fi

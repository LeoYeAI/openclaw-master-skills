#!/bin/bash
# 简化的自动审查脚本 - 用于测试

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/repos.conf"

# 加载 Token
if [ -f "$SCRIPT_DIR/config/gitcode.conf" ]; then
  source "$SCRIPT_DIR/config/gitcode.conf"
fi

# 读取第一个有效的仓库
REPO=$(grep -v '^#' "$CONFIG_FILE" | grep -v '^$' | head -1)

if [ -z "$REPO" ]; then
  echo "❌ 未配置审查仓库"
  exit 1
fi

OWNER=$(echo "$REPO" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO" | cut -d'/' -f2)

echo "🤖 CANN 自动审查（简化版）"
echo "=========================="
echo "审查仓库: $REPO"
echo ""

# 获取 PR 列表
echo "📋 获取开放的 PR 列表..."
PR_LIST=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
  "https://api.gitcode.com/api/v5/repos/$OWNER/$REPO_NAME/pulls?state=opened&per_page=5")

PR_COUNT=$(echo "$PR_LIST" | grep -o '"number":[0-9]*' | wc -l | tr -d ' ')

if [ "$PR_COUNT" -eq 0 ]; then
  echo "✅ 没有找到开放的 PR"
  exit 0
fi

echo "找到 $PR_COUNT 个开放的 PR："
echo ""

# 显示前 5 个 PR
echo "$PR_LIST" | grep -o '"number":[0-9]*\|"title":"[^"]*"' | \
  paste - - | head -5 | while read LINE; do
  PR_NUM=$(echo "$LINE" | grep -o '"number":[0-9]*' | grep -o '[0-9]*')
  TITLE=$(echo "$LINE" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
  echo "  • PR #$PR_NUM - $TITLE"
  echo "    链接: https://gitcode.com/$REPO/merge_requests/$PR_NUM"
done

echo ""
echo "✅ 扫描完成"
echo ""
echo "💡 提示：使用以下命令审查单个 PR："
echo "   审查这个 PR: https://gitcode.com/$REPO/merge_requests/<编号>"

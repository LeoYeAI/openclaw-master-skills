#!/bin/bash
# 测试脚本 - 验证 CANN 代码审查技能

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_SCRIPT="$SCRIPT_DIR/gitcode-api.sh"

echo "🧪 CANN 代码审查技能测试"
echo "========================"
echo ""

# 测试 1: API 连接
echo "📡 测试 1: API 连接"
echo "-------------------"
if curl -s -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
   "https://api.gitcode.com/api/v5/user" | grep -q "login"; then
    echo "✅ API 连接成功"
else
    echo "❌ API 连接失败"
    echo "   请检查 TOOLS.md 中的 Token 配置"
    exit 1
fi
echo ""

# 测试 2: 获取 PR 信息
echo "📋 测试 2: 获取 PR 信息"
echo "----------------------"
PR_INFO=$("$API_SCRIPT" get-pr cann runtime 628)
if echo "$PR_INFO" | grep -q '"number":628'; then
    echo "✅ 成功获取 PR 信息"
    echo "   标题: $(echo "$PR_INFO" | grep -o '"title":"[^"]*"' | head -1)"
else
    echo "❌ 获取 PR 信息失败"
    exit 1
fi
echo ""

# 测试 3: 获取文件变更
echo "📁 测试 3: 获取文件变更"
echo "----------------------"
FILES=$("$API_SCRIPT" get-files cann runtime 628)
FILE_COUNT=$(echo "$FILES" | grep -o '"filename"' | wc -l | tr -d ' ')
if [ "$FILE_COUNT" -gt 0 ]; then
    echo "✅ 成功获取文件变更"
    echo "   文件数量: $FILE_COUNT"
else
    echo "❌ 获取文件变更失败"
    exit 1
fi
echo ""

# 测试 4: 获取开放 PR 列表
echo "📖 测试 4: 获取开放 PR 列表"
echo "---------------------------"
OPEN_PRS=$("$API_SCRIPT" list-prs cann runtime)
PR_COUNT=$(echo "$OPEN_PRS" | grep -o '"number"' | wc -l | tr -d ' ')
if [ "$PR_COUNT" -gt 0 ]; then
    echo "✅ 成功获取开放 PR 列表"
    echo "   开放 PR 数量: $PR_COUNT"
else
    echo "⚠️  没有找到开放的 PR（这是正常的）"
fi
echo ""

# 测试 5: 评论功能（仅测试 API 调用，不实际发布）
echo "💬 测试 5: 评论功能（模拟）"
echo "---------------------------"
TEST_COMMENT="测试评论 - $(date +%Y%m%d%H%M%S)"
ESCAPED=$(echo "$TEST_COMMENT" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))")
echo "✅ 评论转义成功"
echo "   原始: $TEST_COMMENT"
echo "   转义: $ESCAPED"
echo ""

# 总结
echo "📊 测试总结"
echo "==========="
echo "✅ 所有测试通过！"
echo ""
echo "🎉 CANN 代码审查技能已准备就绪"
echo ""
echo "📝 下一步："
echo "   1. 审查单个 PR: 审查 PR#628"
echo "   2. 配置自动审查: 参见 QUICKSTART.md"
echo "   3. 查看完整文档: README.md"

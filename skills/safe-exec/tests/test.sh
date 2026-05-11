#!/bin/bash
# SafeExec Skill 测试脚本

echo "🧪 SafeExec Skill - 功能测试"
echo "================================"
echo ""

# 测试 1: 安全命令
echo "✅ 测试 1: 安全命令（应该直接执行）"
safe-exec "echo 'Hello, SafeExec!' && date"
echo ""

# 测试 2: 危险命令 - 会被拦截
echo "⚠️  测试 2: 危险命令（应该请求批准）"
echo "命令: rm -rf /tmp/test-safe-exec"
safe-exec "rm -rf /tmp/test-safe-exec"
echo ""

# 检查是否有待处理的请求
echo ""
echo "📋 检查待处理的请求..."
if [[ -f ~/.openclaw/safe-exec/pending/req_*.json ]]; then
    echo "发现待处理的请求！"
    safe-exec-list
else
    echo "没有待处理的请求"
fi

echo ""
echo "================================"
echo "测试完成！"
echo ""
echo "💡 使用方法:"
echo "  查看待处理请求: safe-exec-list"
echo "  批准命令: safe-exec-approve <request_id>"
echo "  拒绝命令: safe-exec-reject <request_id>"

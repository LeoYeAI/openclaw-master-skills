#!/bin/bash
# Setup script for 腾讯文档 MCP Skill (内部 OpenClaw 版本)

set -e

echo "🚀 设置腾讯文档 MCP Skill（OpenClaw 版本）..."
echo ""

# 检查 mcporter
if ! command -v mcporter &> /dev/null; then
    echo "⚠️  未找到 mcporter，正在安装..."
    npm install -g mcporter
    echo "✅ mcporter 安装完成"
fi

# 添加 MCP 配置
echo "🔧 配置 mcporter..."

# 从环境变量中读取用户填写的 Token
mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" \
    --header "Authorization=$TENCENT_DOCS_TOKEN" \
    --transport http \
    --scope home

echo ""
echo "✅ 配置完成！"
echo ""
echo "ℹ️  TENCENT_DOCS_TOKEN 环境变量由 OpenClaw runtime 自动提供"
echo ""

# 验证配置
echo "🧪 验证配置..."
if mcporter list 2>&1 | grep -q "tencent-docs"; then
    echo "✅ 配置验证成功！"
    echo ""
    mcporter list | grep -A 1 "tencent-docs" || true
else
    echo "⚠️  配置验证失败，请检查网络或 Token 是否有效"
    echo ""
    echo "如有问题，请访问 https://docs.qq.com/open/document/mcp/get-token/ 获取 Token"
fi

echo ""
echo "─────────────────────────────────────"
echo "🎉 设置完成！"
echo ""
echo "📖 使用方法："
echo "   mcporter call tencent-docs.create_smartcanvas_by_markdown"
echo ""
echo "🏠 腾讯文档主页：https://docs.qq.com/home"
echo ""
echo "📖 更多信息请查看 SKILL.md"
echo ""
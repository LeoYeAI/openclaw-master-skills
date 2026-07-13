#!/bin/bash
# publish-to-clawhub.sh - 发布 SidecarOneStep skill 到 ClawHub

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="sidecar-onestep"
VERSION="1.3.9"

echo "📦 Publishing $SKILL_NAME v$VERSION to ClawHub..."

# 1. 检查登录状态
echo "🔍 Checking login status..."
if ! clawhub whoami &> /dev/null; then
    echo "⚠️  Not logged in. Starting login process..."
    clawhub login
fi

# 2. 验证 skill 文件
echo "✅ Validating skill files..."
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "❌ SKILL.md not found!"
    exit 1
fi

if [ ! -f "$SKILL_DIR/package.json" ]; then
    echo "❌ package.json not found!"
    exit 1
fi

# 3. 发布
echo "🚀 Publishing to ClawHub..."
clawhub publish "$SKILL_DIR" \
  --slug "$SKILL_NAME" \
  --name "SidecarOneStep" \
  --version "$VERSION" \
  --changelog "v1.3.9 - Added MCP integration with 10 tools, async connection support, RunLoop deadlock fix" \
  --tags latest,stable,mcp

# 4. 验证
echo "✅ Verifying publication..."
clawhub info "$SKILL_NAME"

echo ""
echo "🎉 Successfully published $SKILL_NAME v$VERSION to ClawHub!"
echo ""
echo "📥 Users can now install:"
echo "   clawhub install $SKILL_NAME"
echo ""

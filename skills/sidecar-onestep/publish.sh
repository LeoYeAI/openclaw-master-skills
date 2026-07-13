#!/bin/bash
# Quick publish script for SidecarOneStep skill

cd ~/.openclaw/workspace/skills/sidecar-onestep-clawhub

# 检查登录
echo "Checking ClawHub login status..."
if ! clawhub whoami 2>/dev/null; then
    echo "Please login to ClawHub first:"
    echo "  clawhub login"
    exit 1
fi

# 发布
echo "Publishing SidecarOneStep skill to ClawHub..."
clawhub publish . \
  --slug sidecar-onestep \
  --name "SidecarOneStep" \
  --version 1.3.9 \
  --changelog "v1.3.9 - Fixed stdio MCP RunLoop deadlock, async connection with immediate status, 10 MCP tools" \
  --tags latest,stable,mcp

echo ""
echo "✅ Published successfully!"
echo ""
echo "Users can install with:"
echo "  clawhub install sidecar-onestep"

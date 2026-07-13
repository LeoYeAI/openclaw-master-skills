#!/bin/bash

# Video Summary - Setup Entry Point
# This script checks configuration status and triggers conversational setup
# 非交互式：创建配置状态，让 OpenClaw 发起对话式配置

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

# Config paths
CONFIG_DIR="$HOME/.config/video-summary"
CONFIG_FILE="$CONFIG_DIR/config.sh"
STATE_FILE="$CONFIG_DIR/setup-state.json"

# Check if already configured
if [[ -f "$CONFIG_FILE" ]]; then
    # Source and check if API key exists
    source "$CONFIG_FILE" 2>/dev/null || true
    if [[ -n "$OPENAI_API_KEY" ]]; then
        echo -e "${GREEN}✓ video-summary already configured${NC}"
        exit 0
    fi
fi

# Create config directory
mkdir -p "$CONFIG_DIR"

# Create initial setup state
cat > "$STATE_FILE" << 'EOF'
{
  "status": "pending",
  "current_step": "api_provider",
  "steps": {
    "api_provider": { "status": "pending", "question": "你想使用哪个 AI 服务？" },
    "api_key": { "status": "pending", "question": "请输入你的 API Key" },
    "whisper_model": { "status": "pending", "question": "选择 Whisper 模型" },
    "cookies": { "status": "pending", "question": "是否配置 Cookies" }
  }
}
EOF

# Output configuration prompt
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         🎬 Video Summary 需要配置                          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${DIM}配置状态文件已创建：$STATE_FILE${NC}"
echo ""
echo -e "${YELLOW}请通过对话完成配置。你可以问：${NC}"
echo -e "  ${CYAN}「帮我配置 video-summary」${NC}"
echo ""

#!/bin/bash
# 依赖检查脚本（仅检查，不自动安装）
# 需要用户手动安装 wechat-md-publisher

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 需要的版本
REQUIRED_VERSION="0.8.8"

echo -e "${BLUE}检查 wechat-md-publisher 依赖...${NC}"

# 检查是否安装
if ! command -v wechat-pub &> /dev/null; then
    echo -e "${RED}❌ wechat-md-publisher 未安装${NC}"
    echo ""
    echo -e "${YELLOW}请手动运行以下命令安装：${NC}"
    echo ""
    echo "    npm install -g wechat-md-publisher@${REQUIRED_VERSION}"
    echo ""
    echo "此 skill 需要用户确认后才能安装依赖包。"
    exit 1
fi

# 获取当前安装的版本
CURRENT_VERSION=$(wechat-pub --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${RED}❌ 无法检测当前版本${NC}"
    echo ""
    echo -e "${YELLOW}请手动运行以下命令重新安装：${NC}"
    echo ""
    echo "    npm install -g wechat-md-publisher@${REQUIRED_VERSION}"
    echo ""
    exit 1
fi

# 比较版本
if [ "$CURRENT_VERSION" != "$REQUIRED_VERSION" ]; then
    echo -e "${YELLOW}⚠️  版本不匹配${NC}"
    echo -e "当前版本: v${CURRENT_VERSION}"
    echo -e "推荐版本: v${REQUIRED_VERSION}"
    echo ""
    echo -e "${YELLOW}如需更新，请手动运行：${NC}"
    echo ""
    echo "    npm install -g wechat-md-publisher@${REQUIRED_VERSION}"
    echo ""
    echo "继续使用当前版本..."
fi

echo -e "${GREEN}✓ wechat-pub 已安装: v${CURRENT_VERSION}${NC}"

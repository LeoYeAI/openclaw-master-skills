#!/bin/bash
# 依赖检查和自动安装脚本
# 确保 wechat-md-publisher 是最新版本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 需要的版本（从 config.json 读取）
REQUIRED_VERSION="0.3.6"

echo -e "${BLUE}检查 wechat-md-publisher 依赖...${NC}"

# 检查是否安装
if ! command -v wechat-pub &> /dev/null; then
    echo -e "${YELLOW}wechat-md-publisher 未安装，正在安装 v${REQUIRED_VERSION}...${NC}"
    npm install -g wechat-md-publisher@${REQUIRED_VERSION}
    echo -e "${GREEN}✓ 安装成功${NC}"
    exit 0
fi

# 获取当前安装的版本
CURRENT_VERSION=$(wechat-pub --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${YELLOW}无法检测当前版本，重新安装...${NC}"
    npm install -g wechat-md-publisher@${REQUIRED_VERSION}
    echo -e "${GREEN}✓ 安装成功${NC}"
    exit 0
fi

# 比较版本
if [ "$CURRENT_VERSION" != "$REQUIRED_VERSION" ]; then
    echo -e "${YELLOW}当前版本: v${CURRENT_VERSION}${NC}"
    echo -e "${YELLOW}需要版本: v${REQUIRED_VERSION}${NC}"
    echo -e "${YELLOW}正在更新...${NC}"
    
    # 卸载旧版本
    npm uninstall -g wechat-md-publisher &>/dev/null || true
    
    # 安装新版本
    npm install -g wechat-md-publisher@${REQUIRED_VERSION}
    
    NEW_VERSION=$(wechat-pub --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo -e "${GREEN}✓ 更新成功: v${CURRENT_VERSION} → v${NEW_VERSION}${NC}"
else
    echo -e "${GREEN}✓ 版本正确: v${CURRENT_VERSION}${NC}"
fi

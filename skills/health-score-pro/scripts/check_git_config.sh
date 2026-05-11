#!/bin/bash

# Git配置检查脚本
# 用途：检查用户环境是否支持Git备份功能

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取 OpenClaw 称呼（从 IDENTITY.md 读取）
get_openclaw_name() {
    local identity_file="$HOME/.openclaw/workspace/IDENTITY.md"
    if [ -f "$identity_file" ]; then
        # 提取 Name 字段
        local name=$(grep -E "^\s*-\s*\*\*Name:\*\*" "$identity_file" | sed 's/.*\*\*Name:\*\*\s*//' | tr -d ' ')
        if [ -n "$name" ]; then
            echo "@$name"
        else
            echo "OpenClaw"
        fi
    else
        echo "OpenClaw"
    fi
}

# OpenClaw 称呼
OPENCLAW_NAME=$(get_openclaw_name)

# 检查结果
CHECK_PASSED=true
ERRORS=()
WARNINGS=()

echo "=================================================="
echo "🔍 Git环境检查工具"
echo "=================================================="
echo ""

# 1. 检查Git是否已安装
echo "📋 检查Git安装状态..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✅ Git已安装${NC}"
    echo "   版本：$GIT_VERSION"
else
    echo -e "${RED}❌ Git未安装${NC}"
    ERRORS+=("Git未安装")
    CHECK_PASSED=false
fi
echo ""

# 2. 检查Git用户信息
echo "📋 检查Git用户配置..."
GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -n "$GIT_NAME" ] && [ -n "$GIT_EMAIL" ]; then
    echo -e "${GREEN}✅ Git用户信息已配置${NC}"
    echo "   用户名：$GIT_NAME"
    echo "   邮箱：$GIT_EMAIL"
else
    echo -e "${YELLOW}⚠️  Git用户信息未配置${NC}"
    WARNINGS+=("Git用户信息未配置（user.name、user.email）")
fi
echo ""

# 3. 检查SSH密钥
echo "📋 检查SSH密钥..."
if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
    echo -e "${GREEN}✅ SSH密钥已存在${NC}"
    if [ -f ~/.ssh/id_ed25519.pub ]; then
        echo "   类型：ED25519"
    else
        echo "   类型：RSA"
    fi
else
    echo -e "${YELLOW}⚠️  SSH密钥未找到${NC}"
    WARNINGS+=("SSH密钥未生成（需要配置GitHub SSH访问）")
fi
echo ""

# 4. 检查gh CLI（可选）
echo "📋 检查GitHub CLI..."
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version | head -n 1)
    echo -e "${GREEN}✅ GitHub CLI已安装${NC}"
    echo "   版本：$GH_VERSION"
    
    # 检查gh是否已认证
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}   认证状态：已认证${NC}"
    else
        echo -e "${YELLOW}   认证状态：未认证${NC}"
        WARNINGS+=("GitHub CLI未认证（运行 gh auth login）")
    fi
else
    echo -e "${YELLOW}⚠️  GitHub CLI未安装（可选）${NC}"
    WARNINGS+=("GitHub CLI未安装（可选，用于自动创建仓库）")
fi
echo ""

# 5. 检查workspace Git仓库
echo "📋 检查workspace Git仓库..."
WORKSPACE_ROOT="$HOME/.openclaw/workspace"
if [ -d "$WORKSPACE_ROOT/.git" ]; then
    echo -e "${GREEN}✅ Workspace已初始化Git仓库${NC}"
    
    # 检查远程仓库
    REMOTE_URL=$(cd "$WORKSPACE_ROOT" && git remote get-url origin 2>/dev/null || echo "")
    if [ -n "$REMOTE_URL" ]; then
        echo -e "${GREEN}   远程仓库：已配置${NC}"
        echo "   地址：$REMOTE_URL"
    else
        echo -e "${YELLOW}   远程仓库：未配置${NC}"
        WARNINGS+=("Workspace未配置远程仓库")
    fi
else
    echo -e "${YELLOW}⚠️  Workspace未初始化Git仓库${NC}"
    WARNINGS+=("Workspace未初始化Git仓库")
fi
echo ""

# 6. 检查健康数据目录
echo "📋 检查健康数据目录..."
HEALTH_DATA_DIR="$WORKSPACE_ROOT/memory/health-users"
if [ -d "$HEALTH_DATA_DIR" ]; then
    USER_COUNT=$(find "$HEALTH_DATA_DIR" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
    echo -e "${GREEN}✅ 健康数据目录存在${NC}"
    echo "   路径：$HEALTH_DATA_DIR"
    echo "   用户数：$USER_COUNT"
else
    echo -e "${YELLOW}⚠️  健康数据目录不存在${NC}"
    echo "   将在首次使用时创建"
fi
echo ""

# 7. 总结检查结果
echo "=================================================="
echo "📊 检查结果"
echo "=================================================="
echo ""

if [ "$CHECK_PASSED" = true ]; then
    echo -e "${GREEN}✅ Git配置检查完成！${NC}"
    
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  警告（不影响基本使用）：${NC}"
        for i in "${!WARNINGS[@]}"; do
            echo "   $((i+1)). ${WARNINGS[$i]}"
        done
        echo ""
        echo "💡 建议："
        echo "   虽然可以跳过备份配置直接使用，但建议配置备份功能"
        echo "   配置备份：$OPENCLAW_NAME 配置健康数据备份"
    else
        echo ""
        echo "🎉 所有检查通过！可以启用备份功能！"
    fi
else
    echo -e "${RED}❌ Git配置检查失败${NC}"
    echo ""
    echo "❌ 错误："
    for i in "${!ERRORS[@]}"; do
        echo "   $((i+1)). ${ERRORS[$i]}"
    done
    
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  警告：${NC}"
        for i in "${!WARNINGS[@]}"; do
            echo "   $((i+1)). ${WARNINGS[$i]}"
        done
    fi
    
    echo ""
    echo "💡 建议："
    echo "   请先安装Git，然后重新运行检查"
    echo "   安装Git："
    echo "   - macOS: brew install git"
    echo "   - Linux: sudo apt-get install git"
    echo "   - Windows: https://git-scm.com/download/win"
    echo ""
    echo "   你可以暂时跳过备份配置，直接使用健康记录功能"
    echo "   稍后配置：$OPENCLAW_NAME 配置健康数据备份"
fi

echo ""
echo "=================================================="

# 返回检查结果（供其他脚本调用）
if [ "$CHECK_PASSED" = true ]; then
    exit 0
else
    exit 1
fi

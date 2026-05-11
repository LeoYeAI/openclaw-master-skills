#!/bin/bash

# 健康数据备份配置脚本
# 用途：引导用户配置备份功能

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

# 配置文件路径
CONFIG_FILE="$HOME/.openclaw/workspace/memory/health-users/.backup_config"
DEFAULT_BACKUP_PATH="$HOME/Documents/health-data-backup"

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

# 引入时区工具函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/timezone_utils.sh"

# 获取当前用户时间
get_current_time() {
    get_formatted_time
}

# 显示欢迎语
echo "=================================================="
echo "💾 健康数据备份配置工具"
echo "=================================================="
echo ""

# 读取现有配置（如果存在）
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}检测到已有备份配置${NC}"
    source "$CONFIG_FILE"
    echo ""
    echo "当前配置："
    echo "  备份路径： $BACKUP_REPO_PATH"
    echo "  远程仓库： $BACKUP_REMOTE_URL"
    echo "  自动备份： $([ "$BACKUP_ENABLED" = "true" ] && echo "已启用" || echo "已暂停")"
    echo ""
    read -p "是否重新配置？(y/n)" CHOICE
    if [[ "$CHOICE" =~ ^[YYYy] ]]; then
        echo -e "${GREEN}好的，开始重新配置...${NC}"
        echo ""
    else
        echo -e "${GREEN}保持当前配置，退出${NC}"
        exit 0
    fi
else
    echo "未检测到备份配置，开始引导配置流程..."
    echo ""
fi

echo ""
echo "=================================================="
echo ""

# 第1步：选择备份路径
echo "📁 第1步：选择备份路径"
echo ""
echo "默认路径：$DEFAULT_BACKUP_PATH"
echo ""
echo "你也可以选择其他路径，例如："
echo "  ~/Documents/health-backup"
echo "  ~/Backup/health-data"
echo "  或任何你喜欢的路径"
echo ""
echo "请选择："
echo "1. 使用默认路径"
echo "2. 自定义路径"
echo ""
read -p "请输入选择 (1/2/自定义路径): " CHOICE
echo ""

case "$CHOICE" in
    1)
        BACKUP_PATH="$DEFAULT_BACKUP_PATH"
        echo -e "${GREEN}✅ 使用默认路径${NC}"
        ;;
    2)
        read -p "请输入自定义路径（例如 ~/Documents/health-backup）: " BACKUP_PATH
        # 展开 ~ 路径
        BACKUP_PATH="${BACKUP_PATH/#\~/$HOME}"
        echo -e "${GREEN}✅ 使用自定义路径： $BACKUP_PATH${NC}"
        ;;
    *)
        # 直接作为路径处理
        BACKUP_PATH="${CHOICE/#\~/$HOME}"
        echo -e "${GREEN}✅ 使用路径：$BACKUP_PATH${NC}"
        ;;
esac

echo ""

# 第2步：检查Git配置
echo "🔍 第2步：检查Git配置..."
echo ""

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git未安装${NC}"
    echo ""
    echo "请先安装Git："
    echo "  macOS: brew install git"
    echo "  Linux: sudo apt-get install git"
    echo "  Windows: https://git-scm.com/download/win"
    echo ""
    echo "安装完成后，重新运行配置："
    echo "  bash scripts/configure_backup.sh"
    echo ""
    exit 1
fi

# 检查备份路径是否存在
if [ ! -d "$BACKUP_PATH" ]; then
    echo -e "${YELLOW}路径不存在，创建目录...${NC}"
    mkdir -p "$BACKUP_PATH"
    echo -e "${GREEN}✅ 目录已创建${NC}"
fi

# 检查是否已初始化Git仓库
cd "$BACKUP_PATH"
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}备份路径尚未初始化Git仓库${NC}"
    echo ""
    read -p "是否初始化Git仓库？(y/n)" INIT_GIT
    
    if [[ "$INIT_GIT" =~ ^[yYyY] ]]; then
        echo -e "${GREEN}开始初始化Git仓库...${NC}"
        git init
        
        # 获取Git用户信息
        GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
        GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")
        
        if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
            echo -e "${YELLOW}检测到全局Git配置未设置${NC}"
            read -p "请输入Git用户名（例如：John Doe）: " GIT_NAME
            read -p "请输入Git邮箱（例如：john.doe@example.com）: " GIT_EMAIL
            git config user.name "$GIT_NAME"
            git config user.email "$GIT_EMAIL"
            echo -e "${GREEN}✅ Git配置已设置${NC}"
        else
            echo -e "${GREEN}✅ 使用全局Git配置${NC}"
            echo "   用户名：$GIT_NAME"
            echo "   邮箱：$GIT_EMAIL"
            # 使用全局配置
            git config user.name "$GIT_NAME"
            git config user.email "$GIT_EMAIL"
        fi
        echo -e "${GREEN}✅ Git仓库初始化完成${NC}"
    else
        echo -e "${GREEN}✅ Git仓库已存在${NC}"
    fi
fi

echo ""

# 第3步：检查远程仓库
echo "🔍 第3步：检查远程仓库..."
echo ""

REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo -e "${YELLOW}未检测到远程仓库${NC}"
    echo ""
    read -p "是否创建GitHub仓库？(y/n)" CREATE_REPO
    
    if [[ "$CREATE_REPO" =~ ^[yYyY] ]]; then
        echo ""
        echo "有两种方式创建GitHub仓库："
        echo ""
        
        # 检查gh CLI
        if command -v gh &> /dev/null; then
            echo -e "${GREEN}方式1：使用GitHub CLI（推荐，最快）${NC}"
            echo ""
            echo "检测到GitHub CLI已安装，我可以自动帮你创建仓库。"
            echo ""
            read -p "请输入仓库名称（默认：health-data-backup）: " REPO_NAME
            REPO_NAME=${REPO_NAME:-health-data-backup}
            
            echo ""
            echo "将执行以下命令："
            echo "  gh repo create $REPO_NAME --private --source=$BACKUP_PATH --remote=origin --push"
            echo ""
            read -p "是否执行？ (y/n)" CONFIRM_CREATE
            
            if [[ "$CONFIRM_CREATE" =~ ^[yYyY] ]]; then
                echo -e "${GREEN}开始创建仓库...${NC}"
                if gh repo create "$REPO_NAME" --private --source="$BACKUP_PATH" --remote=origin --push 2>&1; then
                    echo -e "${GREEN}✅ GitHub仓库创建成功${NC}"
                    REMOTE_URL=$(git remote get-url origin)
                    echo "   仓库地址：$REMOTE_URL"
                else
                    echo -e "${RED}❌ 仓库创建失败${NC}"
                    echo ""
                    echo "请尝试手动创建（方式2）"
                    CREATE_REPO="manual"
                fi
            else
                echo -e "${YELLOW}已取消自动创建${NC}"
                CREATE_REPO="manual"
            fi
        else
            echo -e "${YELLOW}方式2：手动创建仓库${NC}"
            CREATE_REPO="manual"
        fi
        
        if [ "$CREATE_REPO" = "manual" ]; then
            echo ""
            echo "请按照以下步骤操作："
            echo ""
            echo "步骤1：在GitHub创建仓库"
            echo ""
            echo "1. 访问：https://github.com/new"
            echo "2. 仓库名称：health-data-backup（或你喜欢的名称）"
            echo "3. 描述：健康数据备份"
            echo "4. 设置为：Private（私密仓库）⭐"
            echo "5. 不要勾选：Initialize with README"
            echo "6. 点击：Create repository"
            echo ""
            echo "步骤2：添加远程仓库"
            echo ""
            echo "复制仓库的SSH地址（例如：git@github.com:YOUR_USERNAME/YOUR_REPO.git）"
            echo ""
            read -p "请输入SSH地址: " REMOTE_URL
            git remote add origin "$REMOTE_URL"
            echo -e "${GREEN}✅ 远程仓库已添加${NC}"
        fi
    else
        echo -e "${GREEN}✅ 远程仓库已配置${NC}"
        echo "   地址：$REMOTE_URL"
    fi
fi
echo ""

# 第4步：保存配置
echo "💾 第4步：保存配置..."
echo ""

# 创建配置目录
mkdir -p "$(dirname "$CONFIG_FILE")"

# 保存配置
cat > "$CONFIG_FILE" << EOF
# 健康数据备份配置
# 创建时间：$(get_beijing_time)

# 备份仓库路径（本地）
BACKUP_REPO_PATH=$BACKUP_PATH
# GitHub远程仓库地址（SSH）
BACKUP_REMOTE_URL=$REMOTE_URL
# 是否启用自动备份（true/false）
BACKUP_ENABLED=true
# 最后备份时间
LAST_BACKUP_TIME=$(get_beijing_time)
EOF

echo -e "${GREEN}✅ 配置已保存${NC}"
echo "   配置文件：$CONFIG_FILE"
echo ""

# 第5步：测试备份
echo "🧪 第5步：测试备份..."
echo ""

read -p "是否测试备份功能？ (y/n)" TEST_BACKUP

if [[ "$TEST_BACKUP" =~ ^[yYyY] ]]; then
    echo -e "${GREEN}开始测试备份...${NC}"
    echo ""
    
    # 执行备份脚本
    bash "$(dirname "$0")/backup_health_data.sh"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ 备份测试成功${NC}"
    else
        echo ""
        echo -e "${RED}❌ 备份测试失败${NC}"
        echo "请检查Git配置和网络连接"
    fi
else
    echo -e "${YELLOW}已跳过测试${NC}"
fi
echo ""

# 完成
echo "=================================================="
echo ""
echo -e "${GREEN}🎉 夁份配置完成！${NC}"
echo ""
echo "配置信息："
echo "  备份路径：$BACKUP_PATH"
echo "  远程仓库：$REMOTE_URL"
echo "  自动备份：已启用"
echo ""
echo "管理命令："
echo "  查看配置：$OPENCLAW_NAME 查看备份配置"
echo "  修改路径：$OPENCLAW_NAME 修改备份路径"
echo "  暂停备份：$OPENCLAW_NAME 暂停自动备份"
echo "  恢复备份：$OPENCLAW_NAME 恢复自动备份"
echo "  立即备份：$OPENCLAW_NAME 立即备份健康数据"
echo ""
echo "=================================================="

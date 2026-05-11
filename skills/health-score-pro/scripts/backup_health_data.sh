#!/bin/bash

# 健康数据自动备份脚本
# 参考：充电管理技能的备份逻辑

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 引入工具函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/timezone_utils.sh"
source "$SCRIPT_DIR/language_utils.sh"

# 工作目录
WORKSPACE_ROOT="$HOME/.openclaw/workspace"
HEALTH_DATA_SOURCE="$WORKSPACE_ROOT/memory/health-users"

# 读取备份配置（动态路径）
BACKUP_CONFIG="$WORKSPACE_ROOT/memory/health-users/.backup_config"
if [ -f "$BACKUP_CONFIG" ]; then
    source "$BACKUP_CONFIG"
    BACKUP_REPO="$BACKUP_REPO_PATH"
    
    # 检查是否启用备份
    if [ "$BACKUP_ENABLED" != "true" ]; then
        echo "⚠️  自动备份已暂停，跳过备份"
        echo "   恢复备份：bash scripts/manage_backup.sh resume"
        exit 0
    fi
else
    # 未配置备份，使用默认路径（向后兼容）
    BACKUP_REPO="$HOME/Documents/health-data-backup"
    
    # 检查默认路径是否存在
    if [ ! -d "$BACKUP_REPO/.git" ]; then
        echo "⚠️  未配置备份功能，跳过备份"
        echo "   配置备份：bash scripts/configure_backup.sh"
        exit 0
    fi
fi

# 获取当前用户时间（使用用户配置的时区）
CURRENT_TIME=$(get_formatted_time)

# 获取用户语言（用于多语言输出）
USER_LANGUAGE=$(get_user_language)

echo "=================================================="
echo "🏥 健康数据备份工具"
echo "=================================================="
echo "⏰ 执行时间：$CURRENT_TIME"
echo "📁 源目录：$HEALTH_DATA_SOURCE"
echo "📁 备份仓库：$BACKUP_REPO"
echo ""

# 检查备份仓库是否存在
if [ ! -d "$BACKUP_REPO/.git" ]; then
    echo -e "${RED}❌ 备份仓库不存在：$BACKUP_REPO${NC}"
    echo "💡 请先创建备份仓库"
    exit 1
fi

# 切换到备份仓库
cd "$BACKUP_REPO"

# 同步健康数据（使用 rsync 保持目录结构）
echo "🔄 同步健康数据..."
rsync -av --delete --exclude='.DS_Store' "$HEALTH_DATA_SOURCE/" "$BACKUP_REPO/health-users/" > /dev/null 2>&1
echo "✅ 数据同步完成"

# 检查是否有需要提交的更改（排除 .DS_Store）
# 添加 .gitignore 规则（临时）
echo ".DS_Store" > .gitignore 2>/dev/null || true

# 检查是否有变更
if git diff-index --quiet HEAD -- "health-users" ".gitignore" 2>/dev/null; then
    # 检查是否有 untracked 文件（排除 .DS_Store）
    UNTRACKED=$(git ls-files --others --exclude-standard "health-users" | grep -v '\.DS_Store' | wc -l | tr -d ' ')
    if [ "$UNTRACKED" -eq 0 ]; then
        echo -e "${YELLOW}ℹ️  没有需要备份的更改${NC}"
        exit 0
    fi
fi

# 获取变更统计
CHANGED_FILES=$(git diff --name-only HEAD -- "health-users" | wc -l | tr -d ' ')
UNTRACKED_FILES=$(git ls-files --others --exclude-standard "health-users" | grep -v '\.DS_Store' | wc -l | tr -d ' ')
TOTAL_FILES=$((CHANGED_FILES + UNTRACKED_FILES))

echo ""
echo "📊 变更统计："
echo "   • 修改文件：$CHANGED_FILES 个"
echo "   • 新增文件：$UNTRACKED_FILES 个"
echo "   • 总计：$TOTAL_FILES 个"
echo ""

# Git 操作
echo "🔄 执行 Git 操作..."

# 1. 添加所有更改（包括 .gitignore）
git add "health-users/" ".gitignore" 2>/dev/null || true

# 2. 创建提交
COMMIT_MSG="🏥 健康数据备份 - $CURRENT_TIME

变更文件：$TOTAL_FILES 个
- 修改：$CHANGED_FILES 个
- 新增：$UNTRACKED_FILES 个"

git commit -m "$COMMIT_MSG" || {
    echo -e "${YELLOW}ℹ️  没有需要提交的更改${NC}"
    exit 0
}

# 获取提交哈希（短版本）
COMMIT_HASH=$(git rev-parse --short HEAD)

echo -e "${GREEN}✅ Git Commit 成功${NC}"
echo "   提交哈希：$COMMIT_HASH"

# 3. 推送到远程仓库
echo ""
echo "🚀 推送到 GitHub..."

if git push origin main 2>&1; then
    echo -e "${GREEN}✅ Git Push 成功${NC}"
    PUSH_STATUS="成功"
else
    echo -e "${RED}❌ Git Push 失败${NC}"
    PUSH_STATUS="失败"
    # 不退出，继续执行验证
fi

# 4. 验证推送结果（使用 gh 命令）
echo ""
echo "🔍 验证推送结果..."

if command -v gh &> /dev/null; then
    REPO_INFO=$(gh repo view --json updatedAt,homepageUrl 2>&1)
    
    if [ $? -eq 0 ]; then
        LAST_UPDATE=$(echo "$REPO_INFO" | jq -r '.updatedAt')
        REPO_URL=$(echo "$REPO_INFO" | jq -r '.homepageUrl')
        
        echo -e "${GREEN}✅ 验证成功${NC}"
        echo "   仓库地址：$REPO_URL"
        echo "   最后更新：$LAST_UPDATE"
    else
        echo -e "${YELLOW}⚠️  gh 验证失败，请手动检查${NC}"
        REPO_URL="未配置"
        LAST_UPDATE="未知"
    fi
else
    echo -e "${YELLOW}⚠️  gh 命令未安装，跳过验证${NC}"
    REPO_URL="未配置"
    LAST_UPDATE="未知"
fi

# 5. 输出备份结果
echo ""
echo "=================================================="
echo "📋 备份结果"
echo "=================================================="
echo ""
echo "📝 提交信息："
echo "   • 提交哈希：$COMMIT_HASH"
echo "   • 推送状态：$PUSH_STATUS"
echo "   • 备份路径：$BACKUP_REPO"
echo "   • 仓库地址：$REPO_URL"
echo "   • 最后更新：$LAST_UPDATE"
echo ""

if [ "$PUSH_STATUS" = "成功" ]; then
    SUCCESS_MSG=$(get_localized_text "backup.success" "$USER_LANGUAGE")
    echo -e "${GREEN}$SUCCESS_MSG${NC}"
else
    FAILED_MSG=$(get_localized_text "backup.failed" "$USER_LANGUAGE")
    echo -e "${RED}$FAILED_MSG${NC}"
    exit 1
fi

echo ""
echo "=================================================="

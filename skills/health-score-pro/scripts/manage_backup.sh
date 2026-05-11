#!/bin/bash

# 健康数据备份管理脚本
# 用途：查看、修改、暂停/恢复备份配置

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置文件路径
CONFIG_FILE="$HOME/.openclaw/workspace/memory/health-users/.backup_config"

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

# 引入时区工具函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/timezone_utils.sh"

# 获取当前用户时间
get_current_time() {
    get_formatted_time
}

# 显示帮助信息
show_help() {
    echo "用法："
    echo "  $0 view              查看备份配置"
    echo "  $0 path <path>      修改备份路径"
    echo "  $0 pause            暂停自动备份"
    echo "  $0 resume           恢复自动备份"
    echo "  $0 status           查看备份状态"
    echo ""
    echo "示例："
    echo "  $0 view"
    echo "  $0 path ~/Documents/new-backup"
    echo "  $0 pause"
    echo "  $0 resume"
}

# 查看配置
view_config() {
    echo "=================================================="
    echo "💾 健康数据备份配置"
    echo "=================================================="
    echo ""
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}⚠️  未配置备份功能${NC}"
        echo ""
        echo "配置备份："
        echo "  bash scripts/configure_backup.sh"
        echo ""
        return
    fi
    
    source "$CONFIG_FILE"
    
    echo "配置信息："
    echo "  备份路径：$BACKUP_REPO_PATH"
    echo "  远程仓库：$BACKUP_REMOTE_URL"
    echo "  自动备份：$([ "$BACKUP_ENABLED" = "true" ] && echo "已启用" || echo "已暂停")"
    echo "  最后备份：$LAST_BACKUP_TIME"
    echo ""
    
    # 检查备份路径是否存在
    if [ -d "$BACKUP_REPO_PATH" ]; then
        echo "备份路径状态："
        echo "  路径存在：✅"
        
        # 检查Git仓库
        if [ -d "$BACKUP_REPO_PATH/.git" ]; then
            echo "  Git仓库：✅"
            
            # 检查远程仓库
            REMOTE_URL=$(cd "$BACKUP_REPO_PATH" && git remote get-url origin 2>/dev/null || echo "")
            if [ -n "$REMOTE_URL" ]; then
                echo "  远程仓库：✅"
            else
                echo "  远程仓库：❌ 未配置"
            fi
        else
            echo "  Git仓库：❌ 未初始化"
        fi
    else
        echo "备份路径状态："
        echo "  路径存在：❌ 路径不存在"
    fi
    echo ""
    echo "管理命令："
    echo "  修改路径：bash $0 path <新路径>"
    echo "  暂停备份：bash $0 pause"
    echo "  恢复备份：bash $0 resume"
    echo "  查看状态：bash $0 status"
    echo ""
    echo "=================================================="
}

# 修改备份路径
change_path() {
    local NEW_PATH="$1"
    
    if [ -z "$NEW_PATH" ]; then
        echo -e "${RED}❌ 请提供新路径${NC}"
        echo "示例：$0 path ~/Documents/new-backup"
        exit 1
    fi
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ 未配置备份功能${NC}"
        echo "请先配置：bash scripts/configure_backup.sh"
        exit 1
    fi
    
    # 展开 ~ 路径
    NEW_PATH="${NEW_PATH/#\~/$HOME}"
    
    echo "=================================================="
    echo "📁 修改备份路径"
    echo "=================================================="
    echo ""
    
    source "$CONFIG_FILE"
    echo "当前路径：$BACKUP_REPO_PATH"
    echo "新路径：$NEW_PATH"
    echo ""
    
    read -p "确认修改？ (y/n): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[yYyY] ]]; then
        echo -e "${YELLOW}已取消${NC}"
        exit 0
    fi
    
    # 创建新目录（如果不存在）
    mkdir -p "$NEW_PATH"
    
    # 更新配置文件
    sed -i.bak "s|BACKUP_REPO_PATH=.*|BACKUP_REPO_PATH=$NEW_PATH|" "$CONFIG_FILE"
    
    echo -e "${GREEN}✅ 备份路径已更新${NC}"
    echo ""
    echo "新配置："
    echo "  备份路径：$NEW_PATH"
    echo ""
    echo "💡 建议：手动迁移旧数据到新路径"
    echo "  cp -r $BACKUP_REPO_PATH/* $NEW_PATH/"
    echo ""
    echo "=================================================="
}

# 暂停自动备份
pause_backup() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ 未配置备份功能${NC}"
        exit 1
    fi
    
    echo "=================================================="
    echo "⏸️  暂停自动备份"
    echo "=================================================="
    echo ""
    
    source "$CONFIG_FILE"
    
    if [ "$BACKUP_ENABLED" = "false" ]; then
        echo -e "${YELLOW}⚠️  自动备份已经是暂停状态${NC}"
        exit 0
    fi
    
    # 更新配置
    sed -i.bak "s|BACKUP_ENABLED=.*|BACKUP_ENABLED=false|" "$CONFIG_FILE"
    
    echo -e "${GREEN}✅ 自动备份已暂停${NC}"
    echo ""
    echo "数据将不再自动备份到GitHub。"
    echo ""
    echo "恢复备份：bash $0 resume"
    echo ""
    echo "=================================================="
}

# 恢复自动备份
resume_backup() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ 未配置备份功能${NC}"
        exit 1
    fi
    
    echo "=================================================="
    echo "▶️  恢复自动备份"
    echo "=================================================="
    echo ""
    
    source "$CONFIG_FILE"
    
    if [ "$BACKUP_ENABLED" = "true" ]; then
        echo -e "${YELLOW}⚠️  自动备份已经是启用状态${NC}"
        exit 0
    fi
    
    # 更新配置
    sed -i.bak "s|BACKUP_ENABLED=.*|BACKUP_ENABLED=true|" "$CONFIG_FILE"
    
    echo -e "${GREEN}✅ 自动备份已恢复${NC}"
    echo ""
    echo "数据将在下次操作后自动备份到GitHub。"
    echo ""
    echo "暂停备份：bash $0 pause"
    echo ""
    echo "=================================================="
}

# 查看备份状态
show_status() {
    echo "=================================================="
    echo "📊 备份状态"
    echo "=================================================="
    echo ""
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}⚠️  未配置备份功能${NC}"
        exit 0
    fi
    
    source "$CONFIG_FILE"
    
    if [ "$BACKUP_ENABLED" != "true" ]; then
        echo "自动备份：❌ 已暂停"
        echo ""
        echo "恢复备份：bash $0 resume"
        exit 0
    fi
    
    # 检查备份路径
    if [ ! -d "$BACKUP_REPO_PATH" ]; then
        echo -e "${RED}❌ 备份路径不存在${NC}"
        echo "  路径：$BACKUP_REPO_PATH"
        exit 1
    fi
    
    cd "$BACKUP_REPO_PATH"
    
    # 检查Git仓库
    if [ ! -d ".git" ]; then
        echo -e "${RED}❌ 未初始化Git仓库${NC}"
        exit 1
    fi
    
    # 检查远程仓库
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
    if [ -z "$REMOTE_URL" ]; then
        echo -e "${RED}❌ 未配置远程仓库${NC}"
        exit 1
    fi
    
    # 获取Git状态
    echo "备份路径：$BACKUP_REPO_PATH"
    echo "远程仓库：$REMOTE_URL"
    echo ""
    
    # 获取最后提交
    LAST_COMMIT=$(git log -1 --format="%H %ai %s" 2>/dev/null || echo "无提交记录")
    echo "最后提交：$LAST_COMMIT"
    
    # 获取未推送的提交数
    UNPUSHED=$(git log @{u} --oneline 2>/dev/null | wc -l | tr -d ' ')
    if [ "$UNPUSHED" -gt 0 ]; then
        echo "未推送提交：$UNPUSHED 个"
    else
        echo "未推送提交：0 个"
    fi
    
    # 获取工作区状态
    if git diff-index --quiet HEAD --; then
        echo "工作区状态：✅ 干净"
    else
        CHANGES=$(git diff --name-only | wc -l | tr -d ' ')
        echo "工作区状态：⚠️  有 $CHANGES 个未提交的更改"
    fi
    
    echo ""
    echo "=================================================="
}

# 主逻辑
case "$1" in
    view)
        view_config
        ;;
    path)
        change_path "$2"
        ;;
    pause)
        pause_backup
        ;;
    resume)
        resume_backup
        ;;
    status)
        show_status
        ;;
    *)
        show_help
        ;;
esac

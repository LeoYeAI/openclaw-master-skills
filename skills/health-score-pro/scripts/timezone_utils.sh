#!/bin/bash

# 时区工具函数库（简化版）
# 用途：提供统一的时区获取和格式化功能

# 获取用户时区
# 优先级：profile.md > 默认值(UTC)
get_user_timezone() {
    local username="${1:-}"
    local profile_file
    
    # 如果提供了用户名，读取用户的 profile.md
    if [ -n "$username" ]; then
        profile_file="$HOME/.openclaw/workspace/memory/health-users/$username/profile.md"
    else
        # 尝试从当前用户目录读取
        profile_file="$HOME/.openclaw/workspace/memory/health-users/.default_timezone"
    fi
    
    # 从 profile.md 读取时区
    if [ -f "$profile_file" ]; then
        local timezone=$(grep -E "^\s*-\s*\*\*Timezone\*\*:" "$profile_file" | sed 's/.*\*\*Timezone\*\*:\s*//' | tr -d ' ')
        if [ -n "$timezone" ]; then
            echo "$timezone"
            return 0
        fi
    fi
    
    # 默认值：Asia/Shanghai（北京时间）
    echo "Asia/Shanghai"
}

# 获取格式化的当前时间（使用用户时区）
get_formatted_time() {
    local username="${1:-}"
    local timezone=$(get_user_timezone "$username")
    
    # 使用用户时区格式化时间
    TZ="$timezone" date '+%Y年%m月%d日 %H:%M:%S %Z'
}

# 获取 ISO 格式时间（用于文件命名）
get_iso_time() {
    local username="${1:-}"
    local timezone=$(get_user_timezone "$username")
    
    TZ="$timezone" date '+%Y-%m-%d'
}

# 验证时区是否有效
validate_timezone() {
    local timezone="$1"
    
    # 尝试使用该时区，如果失败则无效
    if TZ="$timezone" date >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

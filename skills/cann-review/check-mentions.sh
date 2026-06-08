#!/bin/bash
# -*- coding: utf-8 -*-
#
# 检查@你的评论并自动审查相关PR
#

set -e

TOKEN="5_EtXLq3jGyQvb6tWwrN3byz"
API_BASE="https://api.gitcode.com/api/v5"
USER="newstarzj"
STATE_FILE="$HOME/.openclaw/workspace/skills/cann-review/.mention-state.json"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN:${NC} $1"
}

# 初始化状态文件
init_state() {
    if [ ! -f "$STATE_FILE" ]; then
        echo '{"checked_comments": [], "last_check": ""}' > "$STATE_FILE"
    fi
}

# 检查仓库中的@评论
check_repo_mentions() {
    local repo=$1
    log "检查仓库 $repo 中的@评论..."
    
    # 获取开放的PR
    local prs=$(curl -s -H "Authorization: Bearer $TOKEN" \
        "$API_BASE/repos/$repo/pulls?state=open&per_page=50" | \
        jq -r '.[].number')
    
    if [ -z "$prs" ]; then
        log "仓库 $repo 没有开放的PR"
        return
    fi
    
    local count=0
    for pr_num in $prs; do
        # 获取PR评论
        local comments=$(curl -s -H "Authorization: Bearer $TOKEN" \
            "$API_BASE/repos/$repo/pulls/$pr_num/comments")
        
        # 检查评论中是否@了用户
        if echo "$comments" | jq -e ".[] | select(.body | contains(\"@$USER\"))" > /dev/null 2>&1; then
            # 获取评论详情
            local comment_info=$(echo "$comments" | jq -r ".[] | select(.body | contains(\"@$USER\")) | {id: .id, body: .body, created_at: .created_at, user: .user.login} | @base64" | head -1)
            
            if [ -n "$comment_info" ]; then
                local comment_data=$(echo "$comment_info" | base64 -d)
                local comment_id=$(echo "$comment_data" | jq -r '.id')
                local comment_time=$(echo "$comment_data" | jq -r '.created_at')
                local comment_user=$(echo "$comment_data" | jq -r '.user')
                
                # 检查是否已经处理过
                if jq -e ".checked_comments | index($comment_id)" "$STATE_FILE" > /dev/null 2>&1; then
                    log "评论 $comment_id 已处理过，跳过"
                    continue
                fi
                
                log "发现新的@评论: PR #$pr_num, 评论者: $comment_user"
                
                # 输出PR信息供后续处理
                echo "$repo|$pr_num|$comment_id|$comment_time"
                
                # 记录到状态文件
                local temp_file=$(mktemp)
                jq ".checked_comments += [$comment_id] | .last_check = \"$(date -Iseconds)\"" "$STATE_FILE" > "$temp_file"
                mv "$temp_file" "$STATE_FILE"
                
                count=$((count + 1))
            fi
        fi
    done
    
    log "仓库 $repo 发现 $count 个新的@评论"
}

# 主函数
main() {
    log "========== 开始检查@评论 =========="
    
    init_state
    
    # 检查配置的仓库
    REPOS=(
        "cann/runtime"
        "cann/oam-tools"
        "cann/oam-tools-diag"
    )
    
    local new_mentions=()
    
    for repo in "${REPOS[@]}"; do
        local mentions=$(check_repo_mentions "$repo")
        if [ -n "$mentions" ]; then
            new_mentions+=("$mentions")
        fi
    done
    
    # 如果有新的@，输出供后续处理
    if [ ${#new_mentions[@]} -gt 0 ]; then
        log "发现 ${#new_mentions[@]} 个需要审查的PR"
        printf '%s\n' "${new_mentions[@]}"
    else
        log "没有发现新的@评论"
    fi
    
    log "========== 检查完成 =========="
}

main "$@"

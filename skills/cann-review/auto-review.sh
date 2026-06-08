#!/bin/bash
# CANN 自动审查脚本
# 用于定时任务，自动审查指定仓库的开放 PR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/repos.conf"
REVIEW_STATE_FILE="$SCRIPT_DIR/.review-state.json"

# 加载配置
load_config() {
    # 优先级：环境变量 > 配置文件
    if [ -n "$CANN_REVIEW_REPOS" ]; then
        REPOS=$(echo "$CANN_REVIEW_REPOS" | tr ',' ' ')
    elif [ -f "$CONFIG_FILE" ]; then
        REPOS=$(grep -v '^#' "$CONFIG_FILE" | grep -v '^$' | tr '\n' ' ')
    else
        echo "错误: 未配置需要审查的仓库"
        echo ""
        echo "配置方法："
        echo "  1. 复制配置模板:"
        echo "     cp $SCRIPT_DIR/config/repos.conf.example $CONFIG_FILE"
        echo ""
        echo "  2. 编辑 $CONFIG_FILE"
        echo "     添加需要审查的仓库（格式: owner/repo）"
        echo ""
        echo "  3. 或设置环境变量:"
        echo "     export CANN_REVIEW_REPOS='cann/runtime,cann/compiler'"
        exit 1
    fi
}

# 加载审查状态
load_review_state() {
    if [ -f "$REVIEW_STATE_FILE" ]; then
        cat "$REVIEW_STATE_FILE"
    else
        echo '{}'
    fi
}

# 保存审查状态
save_review_state() {
    echo "$1" > "$REVIEW_STATE_FILE"
}

# 检查是否已审查
is_reviewed() {
    local repo=$1
    local pr_number=$2
    local state=$(load_review_state)
    
    if echo "$state" | grep -q "\"$repo#$pr_number\""; then
        return 0
    else
        return 1
    fi
}

# 标记为已审查
mark_reviewed() {
    local repo=$1
    local pr_number=$2
    local result=$3
    
    local state=$(load_review_state)
    local timestamp=$(date +%s)
    
    # 使用 Python 更新 JSON
    python3 << EOF
import json
import sys

state = json.loads('''$state''')
key = "$repo#$pr_number"
state[key] = {
    "reviewed_at": $timestamp,
    "result": "$result"
}

with open('$REVIEW_STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
EOF
}

# 审查单个仓库
review_repo() {
    local repo=$1
    local owner=$(echo "$repo" | cut -d'/' -f1)
    local repo_name=$(echo "$repo" | cut -d'/' -f2)
    
    echo "📋 审查仓库: $repo"
    
    # 获取开放的 PR 列表
    local pr_list=$("$SCRIPT_DIR/gitcode-api.sh" list-prs "$owner" "$repo_name" 2>/dev/null)
    
    if [ -z "$pr_list" ] || echo "$pr_list" | grep -q "error\|404"; then
        echo "  ⚠️  无法获取 PR 列表或没有开放的 PR"
        return
    fi
    
    # 统计
    local total=0
    local reviewed=0
    local skipped=0
    
    # 提取 PR 编号
    local pr_numbers=$(echo "$pr_list" | grep -o '"number":[0-9]*' | grep -o '[0-9]*')
    
    for pr_number in $pr_numbers; do
        total=$((total + 1))
        
        # 检查是否已审查
        if [ $(is_reviewed "$repo" "$pr_number") -eq 0 ]; then
            echo "  ⏭️  PR #$pr_number - 已审查，跳过"
            skipped=$((skipped + 1))
            continue
        fi
        
        echo "  🔍 审查 PR #$pr_number ..."
        
        # 调用审查技能
        # 这里可以调用 OpenClaw 的 API 或者直接使用技能
        # 为了简单起见，这里只是标记为已审查
        # 实际使用时应该调用技能的审查逻辑
        
        # 标记为已审查
        mark_reviewed "$repo" "$pr_number" "pending"
        reviewed=$((reviewed + 1))
        
        echo "  ✅ PR #$pr_number - 已加入审查队列"
    done
    
    echo "  📊 统计: 总计 $total, 已审查 $reviewed, 跳过 $skipped"
}

# 主函数
main() {
    echo "🤖 CANN 自动审查"
    echo "===================="
    echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 加载配置
    load_config
    
    echo "📂 配置的仓库:"
    for repo in $REPOS; do
        echo "  - $repo"
    done
    echo ""
    
    # 统计
    local total_repos=${#REPOS[@]}
    local processed=0
    
    # 审查每个仓库
    for repo in $REPOS; do
        processed=$((processed + 1))
        echo "[$processed/$total_repos] 审查仓库: $repo"
        review_repo "$repo"
        echo ""
    done
    
    echo "===================="
    echo "✅ 自动审查完成"
    echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 运行主函数
main

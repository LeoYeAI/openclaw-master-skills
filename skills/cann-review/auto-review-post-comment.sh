#!/bin/bash
# 真正的单次自动审查 - 会实际发布评论到 PR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/repos.conf"
STATE_FILE="$SCRIPT_DIR/.review-state.json"

# 加载 Token
if [ -f "$SCRIPT_DIR/config/gitcode.conf" ]; then
  source "$SCRIPT_DIR/config/gitcode.conf"
fi

if [ -z "$GITCODE_API_TOKEN" ]; then
  echo "❌ 错误: 未配置 GitCode API Token"
  exit 1
fi

# 读取审查状态
load_state() {
  if [ -f "$STATE_FILE" ]; then
    cat "$STATE_FILE"
  else
    echo '{"reviewed": []}'
  fi
}

# 检查 PR 是否已审查
is_reviewed() {
  local repo=$1
  local pr_number=$2
  local state=$(load_state)
  
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
  
  python3 << EOF
import json
from datetime import datetime

try:
    state = json.loads('''$(load_state)''')
except:
    state = {"reviewed": []}

key = "$repo#$pr_number"
if "reviewed" not in state:
    state["reviewed"] = []
if key not in state["reviewed"]:
    state["reviewed"].append(key)
    state["last_review"] = {
        "repo": "$repo",
        "pr": $pr_number,
        "time": datetime.now().isoformat()
    }

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
EOF
}

# 发布简单的审查评论
post_review_comment() {
  local owner=$1
  local repo_name=$2
  local pr_number=$3
  local title=$4
  
  # 生成简单的审查报告
  local comment="## 🤖 CANN 自动审查通知

**PR**: #$pr_number
**标题**: $title
**时间**: $(date '+%Y-%m-%d %H:%M:%S')

### ✅ 审查状态

本 PR 已被自动审查系统标记。

**注意**: 这是自动审查的初步标记。完整的代码审查报告将由人工审查或后续的详细审查流程生成。

---
*此评论由 CANN 自动审查系统自动生成*"
  
  # 转义并发布评论
  local escaped_comment=$(echo "$comment" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))")
  
  local response=$(curl -s -X POST \
    -H "Authorization: Bearer $GITCODE_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"body\":$escaped_comment}" \
    "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls/$pr_number/comments")
  
  # 检查是否成功
  if echo "$response" | grep -q '"id"'; then
    local comment_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "✅ 评论发布成功 (ID: $comment_id)"
    return 0
  else
    echo "❌ 评论发布失败"
    echo "响应: $response"
    return 1
  fi
}

# 主函数
main() {
  echo "🤖 CANN 真正的单次自动审查"
  echo "=========================="
  echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
  
  # 统计仓库数量
  REPO_COUNT=$(grep -v '^#' "$CONFIG_FILE" | grep -v '^$' | wc -l | tr -d ' ')
  echo "📊 配置信息:"
  echo "  仓库数量: $REPO_COUNT"
  echo ""
  
  # 遍历仓库
  echo "🔍 扫描仓库..."
  local found=false
  
  while IFS= read -r repo; do
    # 跳过注释和空行
    [[ "$repo" =~ ^#.*$ ]] && continue
    [[ -z "$repo" ]] && continue
    
    local owner=$(echo "$repo" | cut -d'/' -f1)
    local repo_name=$(echo "$repo" | cut -d'/' -f2)
    
    echo "  检查: $repo"
    
    # 获取开放的 PR（只获取前 5 个）
    local pr_list=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
      "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls?state=opened&per_page=5")
    
    # 提取 PR 编号
    local pr_numbers=$(echo "$pr_list" | grep -o '"number":[0-9]*' | grep -o '[0-9]*')
    
    for pr_number in $pr_numbers; do
      if ! is_reviewed "$repo" "$pr_number"; then
        # 找到未审查的 PR
        found=true
        
        echo ""
        echo "✅ 找到需要审查的 PR:"
        echo "  仓库: $repo"
        echo "  PR: #$pr_number"
        echo ""
        
        # 获取 PR 详情
        local pr_info=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
          "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls/$pr_number")
        
        # 提取标题
        local title=$(echo "$pr_info" | grep -o '"title":"[^"]*"' | head -1 | cut -d'"' -f4)
        
        echo "  标题: $title"
        echo ""
        echo "📝 发布审查评论..."
        
        # 发布评论
        if post_review_comment "$owner" "$repo_name" "$pr_number" "$title"; then
          # 标记为已审查
          mark_reviewed "$repo" "$pr_number"
          echo "✅ 已标记为已审查"
        else
          echo "⚠️  评论发布失败，但仍标记为已审查（避免重复）"
          mark_reviewed "$repo" "$pr_number"
        fi
        
        # 找到第一个就退出
        break 2
      fi
    done
  done < "$CONFIG_FILE"
  
  if [ "$found" = false ]; then
    echo ""
    echo "✅ 所有 PR 都已审查完毕"
  fi
  
  echo ""
  echo "=========================="
  echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 运行主函数
main

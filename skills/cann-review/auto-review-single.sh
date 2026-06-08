#!/bin/bash
# 单次自动审查脚本 - 每次只审查一个 PR
# 避免上下文窗口超限

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/repos.conf"
STATE_FILE="$SCRIPT_DIR/.review-state.json"

# 加载 Token
if [ -f "$SCRIPT_DIR/config/gitcode.conf" ]; then
  source "$SCRIPT_DIR/config/gitcode.conf"
fi

if [ -z "$GITCODE_API_TOKEN" ]; then
  echo "❌ 错误: 未配置 GitCode API Token"
  echo "请运行: ./gitcode-api.sh setup"
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

# 保存审查状态
save_state() {
  echo "$1" > "$STATE_FILE"
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

state = json.loads('''$(load_state)''')
key = "$repo#$pr_number"

if key not in state.get("reviewed", []):
    if "reviewed" not in state:
        state["reviewed"] = []
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

# 查找下一个需要审查的 PR
find_next_pr() {
  while IFS= read -r repo; do
    # 跳过注释和空行
    [[ "$repo" =~ ^#.*$ ]] && continue
    [[ -z "$repo" ]] && continue
    
    local owner=$(echo "$repo" | cut -d'/' -f1)
    local repo_name=$(echo "$repo" | cut -d'/' -f2)
    
    echo "📋 检查仓库: $repo" >&2
    
    # 获取开放的 PR（只获取前 10 个）
    local pr_list=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
      "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls?state=opened&per_page=10")
    
    # 提取 PR 编号
    local pr_numbers=$(echo "$pr_list" | grep -o '"number":[0-9]*' | grep -o '[0-9]*')
    
    for pr_number in $pr_numbers; do
      if ! is_reviewed "$repo" "$pr_number"; then
        # 找到未审查的 PR
        echo "$repo|$pr_number"
        return 0
      fi
    done
  done < "$CONFIG_FILE"
  
  # 没有找到需要审查的 PR
  return 1
}

# 主函数
main() {
  echo "🤖 CANN 自动审查（单次模式）"
  echo "================================"
  echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
  
  # 检查配置文件
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 未配置审查仓库"
    echo "请创建配置文件: config/repos.conf"
    exit 1
  fi
  
  # 查找下一个需要审查的 PR
  echo "🔍 查找下一个需要审查的 PR..."
  local result=$(find_next_pr)
  
  if [ -z "$result" ]; then
    echo ""
    echo "✅ 所有 PR 都已审查完毕"
    echo "没有需要审查的 PR"
    exit 0
  fi
  
  # 解析结果
  local repo=$(echo "$result" | cut -d'|' -f1)
  local pr_number=$(echo "$result" | cut -d'|' -f2)
  
  echo ""
  echo "📝 找到需要审查的 PR:"
  echo "  仓库: $repo"
  echo "  PR: #$pr_number"
  echo ""
  
  # 获取 PR 详情
  local owner=$(echo "$repo" | cut -d'/' -f1)
  local repo_name=$(echo "$repo" | cut -d'/' -f2)
  
  local pr_info=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
    "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls/$pr_number")
  
  local title=$(echo "$pr_info" | grep -o '"title":"[^"]*"' | head -1 | cut -d'"' -f4)
  local author=$(echo "$pr_info" | grep -o '"user":{[^}]*"name":"[^"]*"' | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
  local html_url=$(echo "$pr_info" | grep -o '"html_url":"[^"]*"' | cut -d'"' -f4)
  
  echo "  标题: $title"
  echo "  作者: $author"
  echo "  链接: $html_url"
  echo ""
  
  # 标记为已审查（避免重复）
  mark_reviewed "$repo" "$pr_number"
  
  echo "✅ 已标记为待审查"
  echo ""
  echo "💡 提示: 这个 PR 已加入审查队列"
  echo "   链接: $html_url"
  echo ""
  echo "下次定时任务触发时，会自动审查下一个 PR"
  echo ""
  echo "================================"
  echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 运行主函数
main

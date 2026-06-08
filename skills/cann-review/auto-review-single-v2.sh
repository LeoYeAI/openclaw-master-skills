#!/bin/bash
# 优化的单次审查脚本 - 修复 URL 提取问题

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

# 查找下一个需要审查的 PR
find_next_pr() {
  while IFS= read -r repo; do
    # 跳过注释和空行
    [[ "$repo" =~ ^#.*$ ]] && continue
    [[ -z "$repo" ]] && continue
    
    local owner=$(echo "$repo" | cut -d'/' -f1)
    local repo_name=$(echo "$repo" | cut -d'/' -f2)
    
    echo "  检查: $repo" >&2
    
    # 获取开放的 PR（只获取前 5 个）
    local pr_list=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
      "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls?state=opened&per_page=5")
    
    # 使用 Python 提取 PR 信息
    echo "$pr_list" | python3 << 'PYEOF' "$repo"
import sys, json

repo = sys.argv[1]
try:
    data = json.load(sys.stdin)
    for pr in data:
        pr_number = pr.get('number')
        print(f"{repo}|{pr_number}")
except:
    pass
PYEOF
    
  done < "$CONFIG_FILE"
}

# 主函数
main() {
  echo "🤖 CANN 自动审查（单次模式 - 优化版）"
  echo "======================================"
  echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
  
  # 检查配置文件
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 未配置审查仓库"
    exit 1
  fi
  
  # 统计仓库数量
  REPO_COUNT=$(grep -v '^#' "$CONFIG_FILE" | grep -v '^$' | wc -l | tr -d ' ')
  echo "📊 配置信息:"
  echo "  仓库数量: $REPO_COUNT"
  echo ""
  
  # 查找下一个需要审查的 PR
  echo "🔍 扫描仓库..."
  local pr_list=$(find_next_pr)
  
  if [ -z "$pr_list" ]; then
    echo ""
    echo "✅ 所有 PR 都已审查完毕"
    exit 0
  fi
  
  # 找到第一个未审查的 PR
  local found=false
  while IFS='|' read -r repo pr_number; do
    if ! is_reviewed "$repo" "$pr_number"; then
      # 找到了
      found=true
      
      local owner=$(echo "$repo" | cut -d'/' -f1)
      local repo_name=$(echo "$repo" | cut -d'/' -f2)
      
      echo ""
      echo "✅ 找到需要审查的 PR:"
      echo "  仓库: $repo"
      echo "  PR: #$pr_number"
      echo ""
      
      # 获取 PR 详情
      local pr_info=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
        "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls/$pr_number")
      
      # 使用 Python 提取信息
      echo "$pr_info" | python3 << 'PYEOF'
import sys, json

try:
    data = json.load(sys.stdin)
    title = data.get('title', 'N/A')
    author = data.get('user', {}).get('name', 'N/A')
    html_url = data.get('html_url', 'N/A')
    
    print(f"  标题: {title}")
    print(f"  作者: {author}")
    print(f"  链接: {html_url}")
except:
    print("  无法获取详细信息")
PYEOF
      
      echo ""
      echo "💡 审查命令:"
      echo "  审查这个 PR: $html_url"
      echo ""
      
      # 标记为已审查（避免下次重复）
      python3 << PYEOF
import json
from datetime import datetime

state = json.loads('''$(load_state)''')
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

print("✅ 已标记为已审查")
PYEOF
      
      break
    fi
  done <<< "$pr_list"
  
  if [ "$found" = false ]; then
    echo ""
    echo "✅ 所有 PR 都已审查完毕"
  fi
  
  echo ""
  echo "======================================"
  echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 运行主函数
main

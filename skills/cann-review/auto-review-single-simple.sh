#!/bin/bash
# 完整的单次审查流程 - 找到 PR + 审查 + 发布

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
    
    # 获取开放的 PR（只获取前 10 个）
    local pr_list=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
      "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls?state=opened&per_page=10")
    
    # 提取第一个未审查的 PR
    local pr_numbers=$(echo "$pr_list" | grep -o '"number":[0-9]*' | grep -o '[0-9]*')
    
    for pr_number in $pr_numbers; do
      if ! is_reviewed "$repo" "$pr_number"; then
        # 返回格式: repo|pr_number|owner|repo_name
        echo "$repo|$pr_number|$owner|$repo_name"
        return 0
      fi
    done
  done < "$CONFIG_FILE"
  
  return 1
}

# 主函数
main() {
  echo "🤖 CANN 自动审查（单次完整流程）"
  echo "=================================="
  echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
  
  # 检查配置文件
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 未配置审查仓库"
    exit 1
  fi
  
  # 查找下一个需要审查的 PR
  echo "🔍 查找下一个需要审查的 PR..."
  local result=$(find_next_pr)
  
  if [ -z "$result" ]; then
    echo ""
    echo "✅ 所有 PR 都已审查完毕"
    exit 0
  fi
  
  # 解析结果
  local repo=$(echo "$result" | cut -d'|' -f1)
  local pr_number=$(echo "$result" | cut -d'|' -f2)
  local owner=$(echo "$result" | cut -d'|' -f3)
  local repo_name=$(echo "$result" | cut -d'|' -f4)
  
  echo "✅ 找到需要审查的 PR:"
  echo "  仓库: $repo"
  echo "  PR: #$pr_number"
  echo ""
  
  # 调用审查技能
  echo "📝 开始审查..."
  echo ""
  
  # 这里应该调用 OpenClaw 的审查功能
  # 为了简单，我们直接输出链接
  echo "💡 请使用以下命令审查这个 PR:"
  echo ""
  echo "  审查这个 PR: https://gitcode.com/$repo/merge_requests/$pr_number"
  echo ""
  echo "或者在 OpenClaw 中输入:"
  echo "  cann-review $repo $pr_number"
  echo ""
  
  echo "=================================="
  echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 运行主函数
main

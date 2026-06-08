#!/bin/bash
# 自动审查脚本 - 每10分钟扫描过去10分钟内新提交的 PR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config/repos.conf"
PENDING_FILE="$SCRIPT_DIR/.pending-reviews.json"

# 加载 Token
if [ -f "$SCRIPT_DIR/config/gitcode.conf" ]; then
  source "$SCRIPT_DIR/config/gitcode.conf"
fi

if [ -z "$GITCODE_API_TOKEN" ]; then
  echo "❌ 错误: 未配置 GitCode API Token"
  exit 1
fi

# 计算10分钟时间范围
# 获取上一个10分钟区间的开始和结束时间
# 例如：16:21执行时，扫描16:10:00 ~ 16:19:59
CURRENT_MINUTE=$(date '+%-M')
CURRENT_HOUR=$(date '+%-H')
CURRENT_DATE=$(date '+%Y-%m-%d')

# 计算当前10分钟区间的起始分钟（0, 10, 20, 30, 40, 50）
INTERVAL_START_MINUTE=$((CURRENT_MINUTE / 10 * 10))

# 计算上一个10分钟区间的起始和结束
PREV_INTERVAL_START_MINUTE=$((INTERVAL_START_MINUTE - 10))
PREV_INTERVAL_END_MINUTE=$((INTERVAL_START_MINUTE - 1))

# 处理跨小时的情况
if [ $PREV_INTERVAL_START_MINUTE -lt 0 ]; then
  # 跨到上一个小时
  PREV_INTERVAL_START_MINUTE=$((PREV_INTERVAL_START_MINUTE + 60))
  PREV_INTERVAL_END_MINUTE=$((PREV_INTERVAL_END_MINUTE + 60))
  CURRENT_HOUR=$((CURRENT_HOUR - 1))
  # 处理跨天的情况（简化处理，不做复杂计算）
  if [ $CURRENT_HOUR -lt 0 ]; then
    CURRENT_HOUR=23
  fi
fi

# 格式化时间（补零）
START_MINUTE_STR=$(printf "%02d" $PREV_INTERVAL_START_MINUTE)
END_MINUTE_STR=$(printf "%02d" $PREV_INTERVAL_END_MINUTE)
HOUR_STR=$(printf "%02d" $CURRENT_HOUR)

HOUR_START="${CURRENT_DATE}T${HOUR_STR}:${START_MINUTE_STR}:00+08:00"
HOUR_END="${CURRENT_DATE}T${HOUR_STR}:${END_MINUTE_STR}:59+08:00"

# 主函数
main() {
  echo "🤖 CANN 自动审查（10分钟间隔扫描模式）"
  echo "======================================"
  echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "扫描范围: $HOUR_START ~ $HOUR_END"
  echo ""
  
  # 统计仓库数量
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 未找到配置文件 $CONFIG_FILE"
    exit 1
  fi
  
  REPO_COUNT=$(grep -v '^#' "$CONFIG_FILE" | grep -v '^$' | wc -l | tr -d ' ')
  echo "📊 配置信息:"
  echo "  仓库数量: $REPO_COUNT"
  echo ""
  
  # 初始化待审查列表
  python3 << EOF
import json
from datetime import datetime
with open('$PENDING_FILE', 'w', encoding='utf-8') as f:
    json.dump({"pending": [], "scan_time": datetime.now().isoformat(), "hour_range": {"start": "$HOUR_START", "end": "$HOUR_END"}}, f, indent=2, ensure_ascii=False)
EOF
  
  # 遍历仓库，收集整点内提交的所有 PR
  echo "🔍 扫描所有仓库..."
  local total_pending=0
  
  while IFS= read -r repo; do
    # 跳过注释和空行
    [[ "$repo" =~ ^#.*$ ]] && continue
    [[ -z "$repo" ]] && continue
    
    local owner=$(echo "$repo" | cut -d'/' -f1)
    local repo_name=$(echo "$repo" | cut -d'/' -f2)
    
    echo "  检查: $repo"
    
    # 获取开放的 PR（获取前 50 个，覆盖整点内的提交）
    local pr_list=$(curl -s -H "Authorization: Bearer $GITCODE_API_TOKEN" \
      "https://api.gitcode.com/api/v5/repos/$owner/$repo_name/pulls?state=opened&per_page=50&sort=created&direction=desc")
    
    # 将PR列表保存到临时文件，避免编码问题
    local tmp_pr_file=$(mktemp)
    echo "$pr_list" > "$tmp_pr_file"
    
    # 使用 Python 解析并筛选整点内的 PR
    local repo_pending=$(python3 - "$tmp_pr_file" "$HOUR_START" "$HOUR_END" "$PENDING_FILE" "$repo" << 'PYEOF'
import json
import sys
from datetime import datetime

tmp_file = sys.argv[1]
hour_start_str = sys.argv[2]
hour_end_str = sys.argv[3]
pending_file = sys.argv[4]
repo_name = sys.argv[5]

try:
    with open(tmp_file, 'r', encoding='utf-8') as f:
        pr_list = json.load(f)
except:
    print(0)
    sys.exit(0)

count = 0
hour_start = datetime.fromisoformat(hour_start_str)
hour_end = datetime.fromisoformat(hour_end_str)

for pr in pr_list:
    created_at_str = pr.get('created_at', '')
    updated_at_str = pr.get('updated_at', created_at_str)
    
    # 解析时间
    try:
        if 'T' in updated_at_str:
            updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
        else:
            continue
    except:
        continue
    
    # 检查是否在整点范围内
    if hour_start <= updated_at <= hour_end:
        pr_number = pr.get('number')
        title = pr.get('title', '')
        author = pr.get('user', {}).get('login', '')
        html_url = f"https://gitcode.com/{repo_name}/merge_requests/{pr_number}"
        
        # 添加到待审查列表
        try:
            with open(pending_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            from datetime import datetime as dt
            data = {"pending": [], "scan_time": dt.now().isoformat()}
        
        data["pending"].append({
            "repo": repo_name,
            "pr_number": pr_number,
            "title": title,
            "author": author,
            "url": html_url
        })
        
        with open(pending_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        count += 1

print(count)
PYEOF
)
    
    # 清理临时文件
    rm -f "$tmp_pr_file"
    
    if [ "$repo_pending" -gt 0 ]; then
      echo "    ✅ 发现 $repo_pending 个10分钟内提交的 PR"
      ((total_pending += repo_pending))
    else
      echo "    ℹ️  时间段内无新 PR"
    fi
  done < "$CONFIG_FILE"
  
  echo ""
  echo "======================================"
  echo "扫描完成"
  echo "  待审查 PR 总数: $total_pending"
  echo ""
  
  if [ $total_pending -gt 0 ]; then
    echo "📋 待审查 PR 列表:"
    python3 << 'EOF'
import json
try:
    with open('/Users/zj/.openclaw/workspace/skills/cann-review/.pending-reviews.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i, pr in enumerate(data.get("pending", []), 1):
            print(f"  {i}. {pr['repo']}#{pr['pr_number']} - {pr['title']}")
            print(f"     作者: {pr['author']}")
            print(f"     链接: {pr['url']}")
            print()
except Exception as e:
    print(f"  读取列表失败: {e}")
EOF
    
    echo "💡 接下来将逐个审查这些 PR..."
    echo ""
    
    # 输出 JSON 标记，方便 Agent 解析
    echo "PENDING_REVIEWS_JSON_START"
    cat "$PENDING_FILE"
    echo ""
    echo "PENDING_REVIEWS_JSON_END"
  else
    echo "✅ 时间段内无新 PR 需要审查"
  fi
  
  echo ""
  echo "======================================"
  echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 运行主函数
main

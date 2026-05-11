#!/bin/bash
# 一人公司模式：OpenClaw + Codex/Claude Code 实战
# 目标：单日 90+ 次提交，30 分钟合并多个 PR，完全不打开编辑器

set -e

PROJECT_ROOT=$(pwd)
WORKSPACE_BASE=/tmp/one-person-company-$(date +%s)
mkdir -p $WORKSPACE_BASE/{teams,logs,reports}

echo "🚀 启动一人公司模式"
echo "📍 项目: $PROJECT_ROOT"
echo "🗂️  工作区: $WORKSPACE_BASE"
echo ""

# ============================================
# 1. 任务队列管理
# ============================================

# 从 GitHub Issues 自动获取任务
fetch_tasks() {
  echo "📥 获取待处理任务..."
  
  # 获取所有 open issues
  gh issue list --state open --json number,title,labels --limit 50 > $WORKSPACE_BASE/issues.json
  
  # 按优先级和标签分类
  jq -r '.[] | select(.labels[].name | contains("bug")) | "\(.number):bug:\(.title)"' \
    $WORKSPACE_BASE/issues.json > $WORKSPACE_BASE/queue-bugs.txt
  
  jq -r '.[] | select(.labels[].name | contains("feature")) | "\(.number):feature:\(.title)"' \
    $WORKSPACE_BASE/issues.json > $WORKSPACE_BASE/queue-features.txt
  
  jq -r '.[] | select(.labels[].name | contains("refactor")) | "\(.number):refactor:\(.title)"' \
    $WORKSPACE_BASE/issues.json > $WORKSPACE_BASE/queue-refactor.txt
  
  echo "  ✅ 发现 $(wc -l < $WORKSPACE_BASE/queue-bugs.txt) 个 bug"
  echo "  ✅ 发现 $(wc -l < $WORKSPACE_BASE/queue-features.txt) 个 feature"
  echo "  ✅ 发现 $(wc -l < $WORKSPACE_BASE/queue-refactor.txt) 个 refactor"
}

# ============================================
# 2. 智能任务分配
# ============================================

# 根据任务类型选择最佳 agent
select_agent_for_task() {
  local task_type=$1
  
  case $task_type in
    bug)
      echo "codex"  # Codex 擅长快速定位和修复 bug
      ;;
    feature)
      echo "claude"  # Claude Code 擅长复杂功能开发
      ;;
    refactor)
      echo "opencode"  # OpenCode 擅长代码重构
      ;;
    *)
      echo "claude"
      ;;
  esac
}

# ============================================
# 3. 批量启动工作团队
# ============================================

start_all_teams() {
  local max_concurrent=${1:-5}  # 默认最多 5 个并发
  local active_count=0
  
  echo ""
  echo "👥 启动工作团队（最大并发: $max_concurrent）"
  
  # 优先处理 bug（最高优先级）
  while IFS=: read -r issue_num task_type title; do
    # 等待有空位
    while [ $active_count -ge $max_concurrent ]; do
      sleep 2
      active_count=$(ps aux | grep -E "claude|codex|opencode" | grep -v grep | wc -l)
    done
    
    agent=$(select_agent_for_task "$task_type")
    start_team "$issue_num" "$agent" "$task_type" "$title" &
    
    active_count=$((active_count + 1))
    sleep 1  # 避免同时启动太多
  done < $WORKSPACE_BASE/queue-bugs.txt
  
  # 然后处理 feature
  while IFS=: read -r issue_num task_type title; do
    while [ $active_count -ge $max_concurrent ]; do
      sleep 2
      active_count=$(ps aux | grep -E "claude|codex|opencode" | grep -v grep | wc -l)
    done
    
    agent=$(select_agent_for_task "$task_type")
    start_team "$issue_num" "$agent" "$task_type" "$title" &
    
    active_count=$((active_count + 1))
    sleep 1
  done < $WORKSPACE_BASE/queue-features.txt
}

# 启动单个团队
start_team() {
  local issue_num=$1
  local agent=$2
  local task_type=$3
  local title=$4
  
  local branch_name="issue-${issue_num}"
  local work_dir="$WORKSPACE_BASE/teams/issue-${issue_num}"
  
  echo "  🔧 启动 #$issue_num ($agent): $title"
  
  # 创建 worktree
  git worktree add -b $branch_name $work_dir main 2>/dev/null || {
    echo "    ⚠️  分支已存在，使用现有分支"
    git worktree add $work_dir $branch_name
  }
  
  # 获取 issue 详细信息
  local issue_body=$(gh issue view $issue_num --json body -q .body)
  
  # 构建提示词
  local prompt="
【Issue #$issue_num】: $title
【类型】: $task_type
【详情】:
$issue_body

【要求】:
1. 仔细阅读 issue 描述，理解需求
2. 定位相关代码文件
3. 实现修复/功能（遵循项目规范）
4. 编写/更新测试（确保覆盖率）
5. 运行测试确保通过
6. 提交代码（格式: $task_type(#$issue_num): 简短描述）

【完成后执行】:
git add .
git commit -m '$task_type(#$issue_num): $title'
git push -u origin $branch_name
gh pr create --title '$task_type: $title' --body 'Closes #$issue_num' --head $branch_name
openclaw system event --text '✅ #$issue_num 完成并创建 PR' --mode now
"
  
  # 启动 agent
  case $agent in
    claude)
      bash pty:true workdir:$work_dir background:true \
        command:"claude '$prompt'" \
        > $WORKSPACE_BASE/logs/issue-${issue_num}.log 2>&1
      ;;
    codex)
      bash pty:true workdir:$work_dir background:true \
        command:"codex exec --full-auto '$prompt'" \
        > $WORKSPACE_BASE/logs/issue-${issue_num}.log 2>&1
      ;;
    opencode)
      bash pty:true workdir:$work_dir background:true \
        command:"opencode run '$prompt'" \
        > $WORKSPACE_BASE/logs/issue-${issue_num}.log 2>&1
      ;;
  esac
  
  echo $! > $WORKSPACE_BASE/teams/issue-${issue_num}.pid
}

# ============================================
# 4. 实时仪表盘
# ============================================

show_dashboard() {
  while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          一人公司实时仪表盘 - $(date +%H:%M:%S)              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    # 统计信息
    local total_tasks=$(cat $WORKSPACE_BASE/queue-*.txt 2>/dev/null | wc -l)
    local active_teams=$(ps aux | grep -E "claude|codex|opencode" | grep -v grep | wc -l)
    local completed_prs=$(gh pr list --state open --author @me | wc -l)
    local today_commits=$(git log --since="today" --oneline | wc -l)
    
    echo "📊 统计"
    echo "  总任务数: $total_tasks"
    echo "  活跃团队: $active_teams"
    echo "  待合并 PR: $completed_prs"
    echo "  今日提交: $today_commits"
    echo ""
    
    echo "👥 团队状态"
    for pid_file in $WORKSPACE_BASE/teams/*.pid; do
      if [ -f "$pid_file" ]; then
        issue_num=$(basename $pid_file .pid | sed 's/issue-//')
        pid=$(cat $pid_file)
        
        if ps -p $pid > /dev/null 2>&1; then
          # 获取最新日志
          tail -n 1 $WORKSPACE_BASE/logs/issue-${issue_num}.log 2>/dev/null | \
            sed "s/^/  [#$issue_num] 🟢 /"
        else
          echo "  [#$issue_num] ✅ 已完成"
        fi
      fi
    done
    
    echo ""
    echo "按 Ctrl+C 退出监控"
    sleep 5
  done
}

# ============================================
# 5. 自动 PR 审查和合并
# ============================================

auto_review_and_merge() {
  echo ""
  echo "🔍 自动审查和合并 PR..."
  
  # 获取所有待合并的 PR
  gh pr list --state open --author @me --json number,title,headRefName > $WORKSPACE_BASE/prs.json
  
  local pr_count=$(jq length $WORKSPACE_BASE/prs.json)
  echo "  发现 $pr_count 个待处理 PR"
  
  if [ $pr_count -eq 0 ]; then
    echo "  ✅ 没有待处理的 PR"
    return
  fi
  
  # 批量审查
  jq -r '.[] | "\(.number):\(.headRefName)"' $WORKSPACE_BASE/prs.json | while IFS=: read -r pr_num branch; do
    echo ""
    echo "  审查 PR #$pr_num..."
    
    # 检查 CI 状态
    local ci_status=$(gh pr view $pr_num --json statusCheckRollup -q '.statusCheckRollup[0].state')
    
    if [ "$ci_status" = "SUCCESS" ]; then
      echo "    ✅ CI 通过"
      
      # 自动合并
      if gh pr merge $pr_num --squash --delete-branch; then
        echo "    ✅ PR #$pr_num 已合并"
        
        # 清理 worktree
        local work_dir="$WORKSPACE_BASE/teams/$(echo $branch | sed 's/^issue-/issue-/')"
        if [ -d "$work_dir" ]; then
          git worktree remove $work_dir 2>/dev/null || true
        fi
      else
        echo "    ⚠️  PR #$pr_num 合并失败"
      fi
    else
      echo "    ⏳ CI 未通过，等待中..."
    fi
  done
}

# ============================================
# 6. 生成日报
# ============================================

generate_daily_report() {
  local report_file="$WORKSPACE_BASE/reports/daily-$(date +%Y%m%d).md"
  
  echo "📝 生成日报..."
  
  cat > $report_file << EOF
# 一人公司日报 - $(date +%Y-%m-%d)

## 📊 统计数据

- 今日提交: $(git log --since="today" --oneline | wc -l) 次
- 合并 PR: $(gh pr list --state merged --author @me --search "merged:$(date +%Y-%m-%d)" | wc -l) 个
- 关闭 Issue: $(gh issue list --state closed --author @me --search "closed:$(date +%Y-%m-%d)" | wc -l) 个
- 新增代码: $(git diff --stat @{yesterday}..HEAD | tail -n 1)

## 🎯 完成任务

EOF
  
  # 列出今天合并的 PR
  gh pr list --state merged --author @me --search "merged:$(date +%Y-%m-%d)" \
    --json number,title,closedAt --jq '.[] | "- [#\(.number)] \(.title)"' \
    >> $report_file
  
  echo "" >> $report_file
  echo "## 📈 代码变更" >> $report_file
  echo "" >> $report_file
  echo '```' >> $report_file
  git diff --stat @{yesterday}..HEAD >> $report_file
  echo '```' >> $report_file
  
  echo "  ✅ 日报已生成: $report_file"
  cat $report_file
}

# ============================================
# 主流程
# ============================================

main() {
  # 1. 获取任务
  fetch_tasks
  
  # 2. 启动团队（后台）
  start_all_teams 5
  
  # 3. 显示仪表盘（前台）
  show_dashboard &
  DASHBOARD_PID=$!
  
  # 4. 等待所有团队完成
  echo ""
  echo "⏳ 等待所有团队完成..."
  wait
  
  # 5. 停止仪表盘
  kill $DASHBOARD_PID 2>/dev/null || true
  
  # 6. 自动审查和合并
  auto_review_and_merge
  
  # 7. 生成日报
  generate_daily_report
  
  echo ""
  echo "🎉 一人公司模式完成！"
  echo "📊 查看详细报告: $WORKSPACE_BASE/reports/"
}

# 运行
main "$@"

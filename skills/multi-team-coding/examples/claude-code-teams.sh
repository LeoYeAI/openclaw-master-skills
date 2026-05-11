#!/bin/bash
# OpenClaw + Claude Code 多团队工作流
# 专门优化 Claude Code 的调用方式

set -e

PROJECT_ROOT=$(pwd)
WORKSPACE_BASE=/tmp/claude-teams-$(date +%s)
mkdir -p $WORKSPACE_BASE/{teams,logs,state}

echo "🚀 OpenClaw + Claude Code 多团队模式"
echo ""

# ============================================
# Claude Code 配置优化
# ============================================

# Claude Code 最佳实践配置
export CLAUDE_MODEL="claude-opus-4"  # 使用最强模型
export CLAUDE_MAX_TOKENS=8192        # 增加上下文
export CLAUDE_TEMPERATURE=0.2        # 降低随机性，提高代码质量

# ============================================
# 智能提示词生成器
# ============================================

generate_claude_prompt() {
  local task_type=$1
  local issue_num=$2
  local title=$3
  local description=$4
  
  # 基础上下文
  local context="
【项目信息】
- 项目路径: $PROJECT_ROOT
- 代码规范: 参考 .editorconfig 和 .eslintrc
- 测试框架: 自动检测（Jest/Vitest/Pytest）
- Git 分支: issue-${issue_num}

【任务】
Issue #$issue_num: $title
$description
"

  # 根据任务类型定制提示词
  case $task_type in
    bug)
      echo "$context

【Bug 修复流程】
1. 🔍 分析问题
   - 阅读 issue 描述，理解 bug 现象
   - 查看相关代码文件
   - 定位根本原因

2. 🛠️ 实现修复
   - 最小化改动原则
   - 确保不引入新问题
   - 添加防御性代码

3. ✅ 验证修复
   - 添加回归测试
   - 运行现有测试套件
   - 手动验证修复效果

4. 📝 提交代码
   git add .
   git commit -m 'fix(#$issue_num): $title'
   
【时间预算】15-30 分钟
【质量要求】必须通过所有测试
"
      ;;
      
    feature)
      echo "$context

【功能开发流程】
1. 📋 需求分析
   - 理解功能需求和用户场景
   - 设计 API 接口（如果需要）
   - 规划模块结构

2. 🏗️ 实现功能
   - 遵循 SOLID 原则
   - 编写清晰的代码注释
   - 考虑边界情况和错误处理

3. 🧪 编写测试
   - 单元测试（覆盖率 > 80%）
   - 集成测试（关键路径）
   - 边界测试（异常情况）

4. 📚 更新文档
   - API 文档（JSDoc/Docstring）
   - README（如果需要）
   - 使用示例

5. 📝 提交代码
   git add .
   git commit -m 'feat(#$issue_num): $title'

【时间预算】1-2 小时
【质量要求】完整的测试和文档
"
      ;;
      
    refactor)
      echo "$context

【重构流程】
1. 🎯 明确目标
   - 理解重构目的（性能/可读性/可维护性）
   - 识别代码异味
   - 制定重构计划

2. 🔄 逐步重构
   - 小步快跑，每次改动可测试
   - 保持功能不变
   - 提取公共逻辑

3. ✅ 验证重构
   - 确保所有测试通过
   - 性能对比（如果相关）
   - 代码审查自查

4. 📝 提交代码
   git add .
   git commit -m 'refactor(#$issue_num): $title'

【时间预算】30-60 分钟
【质量要求】不改变外部行为
"
      ;;
      
    test)
      echo "$context

【测试编写流程】
1. 📊 分析覆盖率
   - 运行覆盖率报告
   - 识别未覆盖的代码
   - 优先测试关键路径

2. ✍️ 编写测试
   - 单元测试（隔离测试）
   - 集成测试（端到端）
   - 边界测试（异常情况）

3. 🎯 提高质量
   - 测试命名清晰
   - 断言明确
   - 避免脆弱测试

4. 📝 提交代码
   git add .
   git commit -m 'test(#$issue_num): $title'

【时间预算】30-45 分钟
【质量要求】覆盖率提升 > 10%
"
      ;;
  esac
}

# ============================================
# 启动 Claude Code 团队
# ============================================

start_claude_team() {
  local issue_num=$1
  local task_type=$2
  local title=$3
  local description=$4
  
  local branch_name="issue-${issue_num}"
  local work_dir="$WORKSPACE_BASE/teams/issue-${issue_num}"
  
  echo "  🤖 启动 Claude Code 团队 #$issue_num"
  echo "     类型: $task_type"
  echo "     任务: $title"
  
  # 创建 worktree
  git worktree add -b $branch_name $work_dir main 2>/dev/null || {
    git worktree add $work_dir $branch_name
  }
  
  # 生成优化的提示词
  local prompt=$(generate_claude_prompt "$task_type" "$issue_num" "$title" "$description")
  
  # 添加完成后的自动化操作
  prompt="$prompt

【完成后自动执行】
# 推送代码
git push -u origin $branch_name

# 创建 PR
gh pr create \\
  --title '$task_type: $title' \\
  --body 'Closes #$issue_num

## 变更说明
$(git log -1 --pretty=%B)

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动验证通过

## 检查清单
- [ ] 代码符合规范
- [ ] 添加了测试
- [ ] 更新了文档
' \\
  --head $branch_name \\
  --base main

# 通知完成
openclaw system event --text '✅ #$issue_num 完成并创建 PR' --mode now
"

  # 启动 Claude Code（使用 PTY）
  bash pty:true workdir:$work_dir background:true \
    command:"claude '$prompt'" \
    > $WORKSPACE_BASE/logs/issue-${issue_num}.log 2>&1 &
  
  local pid=$!
  echo $pid > $WORKSPACE_BASE/teams/issue-${issue_num}.pid
  
  # 记录状态
  cat > $WORKSPACE_BASE/state/issue-${issue_num}.json << EOF
{
  "issue": $issue_num,
  "type": "$task_type",
  "title": "$title",
  "status": "running",
  "pid": $pid,
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "work_dir": "$work_dir"
}
EOF
  
  echo "     ✅ 已启动 (PID: $pid)"
  echo ""
}

# ============================================
# 智能监控和干预
# ============================================

monitor_claude_teams() {
  echo "📊 监控 Claude Code 团队..."
  echo ""
  
  while true; do
    local all_done=true
    
    for state_file in $WORKSPACE_BASE/state/*.json; do
      if [ ! -f "$state_file" ]; then
        continue
      fi
      
      local issue_num=$(jq -r .issue "$state_file")
      local pid=$(jq -r .pid "$state_file")
      local status=$(jq -r .status "$state_file")
      
      if [ "$status" = "completed" ]; then
        continue
      fi
      
      # 检查进程状态
      if ps -p $pid > /dev/null 2>&1; then
        all_done=false
        
        # 获取最新日志（最后 3 行）
        local latest_log=$(tail -n 3 $WORKSPACE_BASE/logs/issue-${issue_num}.log 2>/dev/null | tr '\n' ' ')
        echo "  [#$issue_num] 🟢 进行中: $latest_log"
        
        # 检查是否卡住（超过 10 分钟无输出）
        local log_age=$(( $(date +%s) - $(stat -f %m $WORKSPACE_BASE/logs/issue-${issue_num}.log 2>/dev/null || echo 0) ))
        if [ $log_age -gt 600 ]; then
          echo "    ⚠️  可能卡住了，尝试发送继续信号..."
          process action:write sessionId:$pid data:"继续\n"
        fi
      else
        # 进程结束，检查结果
        if [ $? -eq 0 ]; then
          echo "  [#$issue_num] ✅ 已完成"
          jq '.status = "completed" | .completed_at = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
            "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"
        else
          echo "  [#$issue_num] ❌ 失败，准备重试..."
          jq '.status = "failed" | .failed_at = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' \
            "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"
        fi
      fi
    done
    
    if $all_done; then
      echo ""
      echo "🎉 所有团队完成！"
      break
    fi
    
    echo ""
    sleep 30
  done
}

# ============================================
# 批量处理 GitHub Issues
# ============================================

process_github_issues() {
  local max_concurrent=${1:-3}
  
  echo "📥 从 GitHub 获取 Issues..."
  
  # 获取 open issues
  gh issue list --state open --json number,title,body,labels --limit 20 > $WORKSPACE_BASE/issues.json
  
  local issue_count=$(jq length $WORKSPACE_BASE/issues.json)
  echo "  发现 $issue_count 个待处理 Issue"
  echo ""
  
  if [ $issue_count -eq 0 ]; then
    echo "  ✅ 没有待处理的 Issue"
    return
  fi
  
  # 按优先级排序并启动团队
  local active_count=0
  
  jq -c '.[]' $WORKSPACE_BASE/issues.json | while read -r issue; do
    # 等待有空位
    while [ $active_count -ge $max_concurrent ]; do
      sleep 5
      active_count=$(ps aux | grep "claude" | grep -v grep | wc -l)
    done
    
    local issue_num=$(echo "$issue" | jq -r .number)
    local title=$(echo "$issue" | jq -r .title)
    local body=$(echo "$issue" | jq -r .body)
    local labels=$(echo "$issue" | jq -r '.labels[].name' | tr '\n' ',')
    
    # 根据标签确定任务类型
    local task_type="feature"
    if echo "$labels" | grep -q "bug"; then
      task_type="bug"
    elif echo "$labels" | grep -q "refactor"; then
      task_type="refactor"
    elif echo "$labels" | grep -q "test"; then
      task_type="test"
    fi
    
    start_claude_team "$issue_num" "$task_type" "$title" "$body" &
    active_count=$((active_count + 1))
    
    sleep 2  # 避免同时启动太多
  done
  
  # 等待所有后台任务完成
  wait
}

# ============================================
# 生成工作报告
# ============================================

generate_report() {
  local report_file="$WORKSPACE_BASE/report-$(date +%Y%m%d-%H%M%S).md"
  
  echo "📝 生成工作报告..."
  
  cat > $report_file << 'EOF'
# Claude Code 多团队工作报告

## 执行摘要

EOF
  
  # 统计信息
  local total=$(ls $WORKSPACE_BASE/state/*.json 2>/dev/null | wc -l)
  local completed=$(jq -s '[.[] | select(.status == "completed")] | length' $WORKSPACE_BASE/state/*.json 2>/dev/null)
  local failed=$(jq -s '[.[] | select(.status == "failed")] | length' $WORKSPACE_BASE/state/*.json 2>/dev/null)
  
  cat >> $report_file << EOF
- 总任务数: $total
- 完成: $completed
- 失败: $failed
- 成功率: $(( completed * 100 / total ))%

## 任务详情

EOF
  
  # 列出所有任务
  for state_file in $WORKSPACE_BASE/state/*.json; do
    if [ -f "$state_file" ]; then
      local issue=$(jq -r .issue "$state_file")
      local title=$(jq -r .title "$state_file")
      local status=$(jq -r .status "$state_file")
      local type=$(jq -r .type "$state_file")
      
      local status_icon="❓"
      case $status in
        completed) status_icon="✅" ;;
        failed) status_icon="❌" ;;
        running) status_icon="🟢" ;;
      esac
      
      echo "- $status_icon [#$issue] ($type) $title" >> $report_file
    fi
  done
  
  echo "" >> $report_file
  echo "## 日志位置" >> $report_file
  echo "" >> $report_file
  echo "- 工作区: \`$WORKSPACE_BASE\`" >> $report_file
  echo "- 日志: \`$WORKSPACE_BASE/logs/\`" >> $report_file
  echo "- 状态: \`$WORKSPACE_BASE/state/\`" >> $report_file
  
  echo "  ✅ 报告已生成: $report_file"
  cat $report_file
}

# ============================================
# 主流程
# ============================================

main() {
  local max_concurrent=${1:-3}
  
  echo "🎯 配置"
  echo "  最大并发: $max_concurrent"
  echo "  Claude 模型: $CLAUDE_MODEL"
  echo ""
  
  # 1. 处理 GitHub Issues
  process_github_issues $max_concurrent
  
  # 2. 监控进度
  monitor_claude_teams
  
  # 3. 生成报告
  generate_report
  
  echo ""
  echo "🎊 完成！"
}

# 运行
main "$@"

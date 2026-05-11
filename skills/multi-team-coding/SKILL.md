---
name: multi-team-coding
description: '完整的 AI 驱动编程工作流。包含：(1) 多团队并行开发（OpenClaw + Claude Code/Codex/OpenCode），(2) 一人公司模式（单日 90+ 提交），(3) Playwright 自动化测试（E2E/API/视觉/性能），(4) 自动 PR 管理和合并。适用于独立开发者、初创团队、开源项目维护。'
metadata:
  {
    "openclaw": { "emoji": "🚀", "requires": { "anyBins": ["claude", "codex", "opencode"] } },
  }
---

# AI 驱动编程工作流

完整的自动化编程解决方案，从任务分配到测试、部署全流程自动化。

## 📚 目录

1. [多团队并行开发](#多团队并行开发)
2. [一人公司模式](#一人公司模式)
3. [Playwright 自动化测试](#playwright-自动化测试)
4. [快速开始](#快速开始)
5. [完整示例](#完整示例)

---

# 多团队并行开发

基于 OpenClaw + OpenCode 的自主工程团队模式，通过主 agent 编排多个 coding agent 并行工作，实现代码自动化。

## 核心理念

**编排器模式（Orchestrator Pattern）**：
- 主 agent（你）作为编排器，负责任务分解、分配和协调
- 多个 coding agent（Claude Code/Codex/OpenCode）作为工作团队
- 每个团队在独立的 git worktree 中工作，互不干扰
- 自动追踪进度、处理依赖、合并结果

**关键优势**：
- 并行执行，速度提升 2-5 倍
- 智能任务分解，自动识别依赖关系
- 实时进度监控，异常自动告警
- 自动冲突检测和解决建议

## 架构设计

```
主 Agent（编排器）
    ├── 任务分析器：分解需求为独立子任务
    ├── 任务调度器：分配任务给可用团队
    ├── 进度监控器：实时追踪各团队状态
    ├── 冲突检测器：识别潜在代码冲突
    └── 结果集成器：合并各团队成果

工作团队（Coding Agents）
    ├── Team A: 独立 worktree + coding agent
    ├── Team B: 独立 worktree + coding agent
    ├── Team C: 独立 worktree + coding agent
    └── Team N: 独立 worktree + coding agent
```

## 工作流程

### 1. 智能任务分解

主 agent 分析用户需求，自动识别：
- 独立模块（可并行）
- 依赖关系（需串行）
- 共享资源（需协调）
- 优先级排序

```bash
# 示例：构建电商系统
任务树：
├── [P0] 数据库设计（基础，其他依赖）
├── [P1] 并行组
│   ├── Team A: 用户认证模块
│   ├── Team B: 商品管理 API
│   └── Team C: 订单系统
└── [P2] 前端集成（依赖 P1 完成）
```

### 2. 动态工作空间创建

为每个团队自动创建隔离的工作环境：

```bash
# 主项目目录
PROJECT_ROOT=$(pwd)
WORKSPACE_BASE=/tmp/multi-team-$(date +%s)

# 创建任务状态追踪文件
cat > $WORKSPACE_BASE/status.json << 'EOF'
{
  "project": "电商系统",
  "started": "2026-03-09T07:00:00Z",
  "teams": {},
  "dependencies": {}
}
EOF

# 为每个团队创建 worktree
create_team_workspace() {
  local team_name=$1
  local task_desc=$2
  local branch_name="team-${team_name}"
  local work_dir="${WORKSPACE_BASE}/${team_name}"
  
  git worktree add -b $branch_name $work_dir main
  
  # 记录团队信息
  echo "{\"status\": \"created\", \"task\": \"$task_desc\", \"dir\": \"$work_dir\"}" \
    > $WORKSPACE_BASE/teams/${team_name}.json
}
```

### 3. 启动工作团队

使用统一的启动模板，支持多种 coding agent：

```bash
# 启动函数（支持 Claude Code/Codex/OpenCode）
start_team() {
  local team_name=$1
  local agent_type=$2  # claude, codex, opencode
  local task_prompt=$3
  local work_dir="${WORKSPACE_BASE}/${team_name}"
  
  # 构建完整提示词
  local full_prompt="
【团队】: $team_name
【任务】: $task_prompt

【要求】:
1. 遵循项目代码规范（参考 .editorconfig）
2. 编写单元测试（覆盖率 > 80%）
3. 更新相关文档
4. 提交前运行 lint 和 format
5. 提交信息格式：feat($team_name): 简短描述

【完成标准】:
- 所有测试通过
- 代码审查通过
- 文档完整

【完成后执行】:
git add . && git commit -m 'feat($team_name): 完成任务'
openclaw system event --text '✅ $team_name 完成：$task_prompt' --mode now
"

  # 根据 agent 类型选择命令
  case $agent_type in
    claude)
      bash pty:true workdir:$work_dir background:true \
        command:"claude '$full_prompt'"
      ;;
    codex)
      bash pty:true workdir:$work_dir background:true \
        command:"codex exec --full-auto '$full_prompt'"
      ;;
    opencode)
      bash pty:true workdir:$work_dir background:true \
        command:"opencode run '$full_prompt'"
      ;;
  esac
  
  # 记录 session ID
  echo $! > $WORKSPACE_BASE/teams/${team_name}.pid
}

# 示例：启动多个团队
start_team "auth" "claude" "实现用户认证模块：注册、登录、JWT、密码加密"
start_team "products" "codex" "实现商品管理 API：CRUD、分类、搜索、库存"
start_team "orders" "opencode" "实现订单系统：创建、支付、状态管理、历史"
```

### 4. 实时进度监控

主 agent 持续监控各团队状态：

```bash
# 监控脚本
monitor_teams() {
  local workspace=$1
  
  while true; do
    echo "=== 团队状态 $(date +%H:%M:%S) ==="
    
    for team_file in $workspace/teams/*.json; do
      team_name=$(basename $team_file .json)
      pid_file="$workspace/teams/${team_name}.pid"
      
      if [ -f "$pid_file" ]; then
        pid=$(cat $pid_file)
        
        # 检查进程状态
        if ps -p $pid > /dev/null; then
          # 获取最新输出
          process action:log sessionId:$pid limit:5
          echo "  [$team_name] 🟢 运行中"
        else
          echo "  [$team_name] ✅ 已完成"
        fi
      fi
    done
    
    echo ""
    sleep 30
  done
}

# 后台启动监控
monitor_teams $WORKSPACE_BASE &
MONITOR_PID=$!
```

### 5. 智能冲突检测

在合并前自动检测潜在冲突：

```bash
# 冲突检测函数
detect_conflicts() {
  local workspace=$1
  local conflicts=()
  
  echo "🔍 检测潜在冲突..."
  
  # 收集所有团队修改的文件
  declare -A file_teams
  
  for team_dir in $workspace/*/; do
    team_name=$(basename $team_dir)
    
    # 获取该团队修改的文件
    cd $team_dir
    modified_files=$(git diff --name-only main)
    
    for file in $modified_files; do
      if [ -n "${file_teams[$file]}" ]; then
        conflicts+=("⚠️  冲突：$file 被 ${file_teams[$file]} 和 $team_name 同时修改")
      else
        file_teams[$file]=$team_name
      fi
    done
  done
  
  # 报告冲突
  if [ ${#conflicts[@]} -gt 0 ]; then
    echo "❌ 发现 ${#conflicts[@]} 个潜在冲突："
    printf '%s\n' "${conflicts[@]}"
    return 1
  else
    echo "✅ 无冲突，可以安全合并"
    return 0
  fi
}
```

### 6. 自动结果集成

智能合并各团队成果：

```bash
# 集成函数
integrate_results() {
  local workspace=$1
  local project_root=$2
  
  cd $project_root
  
  echo "🔄 开始集成各团队成果..."
  
  # 按依赖顺序合并
  local merge_order=("auth" "products" "orders" "frontend")
  
  for team_name in "${merge_order[@]}"; do
    echo "  合并 $team_name..."
    
    # 合并分支
    if git merge --no-ff team-${team_name} -m "feat: 集成 $team_name 模块"; then
      echo "  ✅ $team_name 合并成功"
    else
      echo "  ❌ $team_name 合并失败，需要手动解决"
      git merge --abort
      
      # 调用 AI 辅助解决冲突
      bash pty:true command:"claude '解决以下合并冲突：
$(git diff --name-only --diff-filter=U)

要求：
1. 分析冲突原因
2. 保留正确的代码
3. 确保功能完整
4. 提交解决方案
'"
      return 1
    fi
  done
  
  echo "✅ 所有模块集成完成"
}
```

### 7. 自动化测试验证

集成后自动运行测试套件：

```bash
# 验证函数
validate_integration() {
  local project_root=$1
  
  cd $project_root
  
  echo "🧪 运行集成测试..."
  
  # 安装依赖
  if [ -f "package.json" ]; then
    npm install
  elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  fi
  
  # 运行测试
  if npm test; then
    echo "✅ 所有测试通过"
    return 0
  else
    echo "❌ 测试失败，回滚集成"
    git reset --hard HEAD~1
    return 1
  fi
}
```

---

# 一人公司模式

基于 Elvis Sun 的实战经验：**单日 94 次提交，30 分钟合并 7 个 PR，完全不打开编辑器**。

## 核心理念

**本地优先 + 自动化 + 批量处理**

- AI 跑在本地，不依赖云端网页
- 不需要一直盯着屏幕
- 不需要频繁点击权限弹窗
- 让 AI 团队自主工作，你只需要审查结果

## 快速启动

```bash
cd your-project
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/one-person-company.sh
```

详细文档：[ONE-PERSON-COMPANY.md](./ONE-PERSON-COMPANY.md)

---

# Playwright 自动化测试

基于 Claude Code + Playwright CLI 实现端到端测试自动化。

## 核心优势

- **高效**：26K tokens vs 114K tokens (MCP)
- **可靠**：基于可访问性树，不依赖截图
- **并行**：多浏览器、多测试同时运行
- **持久化**：保存认证状态，避免重复登录

## 快速启动

```bash
cd your-project
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/playwright-test-workflow.sh
```

详细文档：[PLAYWRIGHT-AUTOMATION.md](./PLAYWRIGHT-AUTOMATION.md)

---

# 快速开始

## 场景 1：批量修复 Bug

```bash
# 自动从 GitHub Issues 获取所有 bug
# 并行启动多个 Claude Code 团队修复
cd your-project
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/claude-code-teams.sh 5
```

## 场景 2：开发新功能 + 自动测试

```bash
# 1. 开发功能
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/claude-code-teams.sh

# 2. 生成并运行测试
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/playwright-test-workflow.sh
```

## 场景 3：一人公司全自动模式

```bash
# 早上启动，下午收获
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/one-person-company.sh
```

---

# 完整示例

## 电商系统开发（端到端）

```bash
#!/bin/bash
# 完整的电商系统开发流程

PROJECT_ROOT=~/Projects/ecommerce
cd $PROJECT_ROOT

echo "🚀 启动电商系统开发"

# 1. 并行开发核心功能
echo "📝 Step 1: 并行开发功能模块..."
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/claude-code-teams.sh 5

# 等待开发完成
echo "⏳ 等待开发完成..."
wait

# 2. 生成自动化测试
echo "🧪 Step 2: 生成自动化测试..."
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/playwright-test-workflow.sh << EOF
1
EOF

# 等待测试生成
wait

# 3. 运行测试
echo "🚀 Step 3: 运行测试..."
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/playwright-test-workflow.sh << EOF
2
EOF

# 4. 自动合并 PR
echo "🔄 Step 4: 合并通过的 PR..."
gh pr list --state open --json number,statusCheckRollup | \
  jq -r '.[] | select(.statusCheckRollup[0].state == "SUCCESS") | .number' | \
  while read pr; do
    gh pr merge $pr --squash --delete-branch
  done

echo "🎉 完成！"
echo "📊 查看报告："
echo "  - 开发报告: /tmp/claude-teams-*/report-*.md"
echo "  - 测试报告: playwright-report/index.html"
```

---

# 工作流对比

## 传统方式

```
开发者手动编码
  ↓ (8 小时)
手动编写测试
  ↓ (2 小时)
手动运行测试
  ↓ (30 分钟)
手动创建 PR
  ↓ (10 分钟)
手动审查和合并
  ↓ (30 分钟)
总计: 11 小时 10 分钟
```

## AI 驱动工作流

```
启动脚本
  ↓ (1 分钟)
AI 团队并行开发
  ↓ (30 分钟，自动)
AI 生成测试
  ↓ (15 分钟，自动)
自动运行测试
  ↓ (5 分钟，自动)
自动创建和合并 PR
  ↓ (2 分钟，自动)
总计: 53 分钟（人工参与 < 5 分钟）
```

**效率提升：12 倍**

---

# 配置和定制

## 自定义 Agent 选择

编辑 `examples/claude-code-teams.sh`：

```bash
select_agent_for_task() {
  local task_type=$1
  
  case $task_type in
    bug)
      echo "codex"      # 快速修复
      ;;
    feature)
      echo "claude"     # 复杂功能
      ;;
    refactor)
      echo "opencode"   # 代码优化
      ;;
  esac
}
```

## 自定义并发数

```bash
# 根据机器性能调整
# 8 核 CPU → 3-5 个并发
# 16 核 CPU → 8-10 个并发
bash claude-code-teams.sh 5
```

## 自定义测试类型

编辑 `examples/playwright-test-workflow.sh`：

```bash
# 只生成 E2E 测试
start_test_generation_team "$feature" "$description" "e2e"

# 生成所有类型测试
for type in e2e api visual performance; do
  start_test_generation_team "$feature" "$description" "$type"
done
```

---

# 最佳实践

## 1. 任务拆分

- **独立性**：每个任务应该独立，减少依赖
- **明确性**：清晰的目标和验收标准
- **平衡性**：工作量相当
- **可测试**：可以独立测试

## 2. 代码质量

- 遵循项目规范（.editorconfig, .eslintrc）
- 编写清晰的提交信息（Conventional Commits）
- 保持测试覆盖率 > 80%
- 及时处理 CI 失败

## 3. 资源管理

- 控制并发数量（避免资源耗尽）
- 定期清理 worktree
- 监控系统资源使用
- 使用 SSD 提升性能

## 4. 团队协作

- 使用通知系统（Feishu/Slack）
- 生成详细的日报
- 定期审查 AI 生成的代码
- 建立代码审查流程

---

# 故障排查

## 问题 1：Agent 卡住

```bash
# 查看日志
tail -f /tmp/*/logs/issue-*.log

# 发送继续信号
process action:write sessionId:XXX data:"继续\n"

# 重启
process action:kill sessionId:XXX
```

## 问题 2：测试失败

```bash
# 查看详细报告
npx playwright show-report

# 只运行失败的测试
npx playwright test --last-failed

# 调试模式
npx playwright test --debug
```

## 问题 3：PR 合并冲突

```bash
# 使用 AI 解决冲突
bash pty:true command:"claude '
解决以下合并冲突：
$(git diff --name-only --diff-filter=U)

要求：
1. 分析冲突原因
2. 保留正确的代码
3. 确保功能完整
4. 提交解决方案
'"
```

---

# 性能优化

## 1. 使用本地模型

```bash
# 对于简单任务，使用本地模型更快
export CODEX_MODEL="local/qwen-2.5-coder"
export CLAUDE_MODEL="local/deepseek-coder"
```

## 2. 缓存依赖

```bash
# 共享 node_modules
for team_dir in /tmp/teams/*/; do
  ln -s $PROJECT_ROOT/node_modules $team_dir/node_modules
done
```

## 3. 增量构建

```bash
# 只重建变更的模块
changed_modules=$(git diff --name-only main | cut -d'/' -f1 | sort -u)
for module in $changed_modules; do
  cd $module && npm run build
done
```

---

# 成本分析

## API 成本

```
假设每个任务：
- Claude Code: $0.50
- Codex: $0.30
- OpenCode: $0.20
- Playwright 测试: $0.10

10 个任务 × 平均 $0.35 = $3.50

vs 人工成本：
10 个任务 × 8 小时 × $50/小时 = $4,000

节省：99.9%
```

## 时间成本

```
传统方式：10 个任务 × 8 小时 = 80 小时
AI 工作流：10 个任务 × 0.5 小时 = 5 小时

节省：75 小时（93.75%）
```

---

# 总结

这套 AI 驱动编程工作流提供：

✅ **多团队并行开发**：2-5 倍速度提升
✅ **一人公司模式**：单日 90+ 提交
✅ **自动化测试**：E2E/API/视觉/性能全覆盖
✅ **自动 PR 管理**：从创建到合并全自动
✅ **本地优先**：不依赖云端，数据安全
✅ **成本优化**：节省 99.9% 人工成本

**适用场景**：
- 独立开发者
- 初创公司
- 开源项目维护
- 副业项目

**开始你的 AI 驱动编程之旅！** 🚀

---

## 相关文档

- [多团队编程详细文档](./SKILL.md)
- [一人公司模式指南](./ONE-PERSON-COMPANY.md)
- [Playwright 自动化测试](./PLAYWRIGHT-AUTOMATION.md)
- [示例脚本](./examples/)

## 社区和支持

- OpenClaw 文档: https://docs.openclaw.ai
- GitHub: https://github.com/openclaw/openclaw
- Discord: https://discord.com/invite/clawd
- ClawHub: https://clawhub.com

### 场景
构建一个完整的电商系统，包含用户、商品、订单、支付四个核心模块。

### 执行流程

```bash
#!/bin/bash
# 电商系统多团队开发脚本

PROJECT_ROOT=$(pwd)
WORKSPACE_BASE=/tmp/ecommerce-$(date +%s)
mkdir -p $WORKSPACE_BASE/teams

echo "🚀 启动电商系统多团队开发"

# 1. 任务分解
declare -A TASKS=(
  ["auth"]="用户认证：注册、登录、JWT、权限管理"
  ["products"]="商品管理：CRUD、分类、搜索、库存"
  ["orders"]="订单系统：创建、支付、状态、历史"
  ["payment"]="支付集成：Stripe、支付宝、微信支付"
)

# 2. 创建工作空间并启动团队
for team in "${!TASKS[@]}"; do
  echo "  创建团队: $team"
  
  # 创建 worktree
  git worktree add -b team-$team $WORKSPACE_BASE/$team main
  
  # 启动 coding agent
  bash pty:true workdir:$WORKSPACE_BASE/$team background:true \
    command:"claude '
【团队】: $team
【任务】: ${TASKS[$team]}

【技术栈】:
- 后端: Node.js + Express + TypeScript
- 数据库: PostgreSQL + Prisma
- 测试: Jest + Supertest

【要求】:
1. 遵循 RESTful API 设计
2. 编写单元测试和集成测试
3. 添加 API 文档（JSDoc）
4. 错误处理和日志记录
5. 提交前运行 lint

【完成后】:
git add . && git commit -m \"feat($team): ${TASKS[$team]}\"
openclaw system event --text \"✅ $team 完成\" --mode now
'" &
  
  echo $! > $WORKSPACE_BASE/teams/$team.pid
done

# 3. 监控进度
echo ""
echo "📊 监控团队进度（每30秒更新）"
while true; do
  clear
  echo "=== 电商系统开发进度 $(date +%H:%M:%S) ==="
  echo ""
  
  all_done=true
  for team in "${!TASKS[@]}"; do
    pid=$(cat $WORKSPACE_BASE/teams/$team.pid 2>/dev/null)
    
    if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
      echo "  [$team] 🟢 进行中"
      all_done=false
    else
      echo "  [$team] ✅ 已完成"
    fi
  done
  
  if $all_done; then
    echo ""
    echo "🎉 所有团队完成！开始集成..."
    break
  fi
  
  sleep 30
done

# 4. 冲突检测
echo ""
echo "🔍 检测代码冲突..."
cd $PROJECT_ROOT

conflicts_found=false
for team in "${!TASKS[@]}"; do
  if ! git merge --no-commit --no-ff team-$team 2>/dev/null; then
    echo "  ⚠️  $team 存在冲突"
    conflicts_found=true
    git merge --abort
  else
    git merge --abort
  fi
done

if $conflicts_found; then
  echo "❌ 发现冲突，需要手动解决"
  exit 1
fi

# 5. 按顺序合并
echo ""
echo "🔄 合并各团队成果..."
merge_order=("auth" "products" "orders" "payment")

for team in "${merge_order[@]}"; do
  echo "  合并 $team..."
  git merge --no-ff team-$team -m "feat: 集成 $team 模块"
done

# 6. 运行测试
echo ""
echo "🧪 运行集成测试..."
npm install
npm test

if [ $? -eq 0 ]; then
  echo "✅ 所有测试通过"
else
  echo "❌ 测试失败，回滚"
  git reset --hard HEAD~4
  exit 1
fi

# 7. 清理
echo ""
echo "🧹 清理工作空间..."
for team in "${!TASKS[@]}"; do
  git worktree remove $WORKSPACE_BASE/$team
done

echo ""
echo "🎊 电商系统开发完成！"
```

---

## 高级特性

### 1. 依赖管理

处理模块间的依赖关系：

```bash
# 定义依赖图
declare -A DEPENDENCIES=(
  ["auth"]=""                    # 无依赖，优先执行
  ["products"]="auth"            # 依赖 auth
  ["orders"]="auth,products"     # 依赖 auth 和 products
  ["payment"]="orders"           # 依赖 orders
)

# 拓扑排序执行
execute_with_dependencies() {
  local executed=()
  local pending=("${!DEPENDENCIES[@]}")
  
  while [ ${#pending[@]} -gt 0 ]; do
    for task in "${pending[@]}"; do
      deps="${DEPENDENCIES[$task]}"
      
      # 检查依赖是否都已完成
      can_execute=true
      if [ -n "$deps" ]; then
        IFS=',' read -ra dep_array <<< "$deps"
        for dep in "${dep_array[@]}"; do
          if [[ ! " ${executed[@]} " =~ " ${dep} " ]]; then
            can_execute=false
            break
          fi
        done
      fi
      
      # 执行任务
      if $can_execute; then
        start_team "$task" "claude" "${TASKS[$task]}"
        executed+=("$task")
        pending=("${pending[@]/$task}")
      fi
    done
    
    sleep 5
  done
}
```

### 2. 动态负载均衡

根据任务复杂度分配不同的 agent：

```bash
# 任务复杂度评估
estimate_complexity() {
  local task=$1
  local lines_of_code=0
  local num_files=0
  
  # 分析任务描述，估算复杂度
  # 简单任务: < 500 行代码
  # 中等任务: 500-2000 行
  # 复杂任务: > 2000 行
  
  if [ $lines_of_code -lt 500 ]; then
    echo "simple"
  elif [ $lines_of_code -lt 2000 ]; then
    echo "medium"
  else
    echo "complex"
  fi
}

# 选择合适的 agent
select_agent() {
  local complexity=$1
  
  case $complexity in
    simple)
      echo "opencode"  # 快速，适合简单任务
      ;;
    medium)
      echo "codex"     # 平衡，适合中等任务
      ;;
    complex)
      echo "claude"    # 强大，适合复杂任务
      ;;
  esac
}
```

### 3. 自动重试机制

团队失败时自动重试：

```bash
# 重试函数
retry_team() {
  local team=$1
  local max_retries=3
  local retry_count=0
  
  while [ $retry_count -lt $max_retries ]; do
    echo "  尝试 $team (第 $((retry_count+1)) 次)..."
    
    start_team "$team" "claude" "${TASKS[$team]}"
    
    # 等待完成
    wait_for_team "$team"
    
    # 检查结果
    if validate_team_output "$team"; then
      echo "  ✅ $team 成功"
      return 0
    else
      echo "  ❌ $team 失败，准备重试..."
      retry_count=$((retry_count+1))
      
      # 清理失败的工作
      cd $WORKSPACE_BASE/$team
      git reset --hard HEAD
      git clean -fd
    fi
  done
  
  echo "  ❌ $team 达到最大重试次数"
  return 1
}
```

### 4. 实时协作通知

通过 Feishu/Slack 发送进度通知：

```bash
# 发送通知
notify_progress() {
  local team=$1
  local status=$2
  local message=$3
  
  # 使用 OpenClaw 的 message 工具
  message action:send channel:feishu target:group_chat_id \
    message:"
【多团队开发进度】
团队: $team
状态: $status
详情: $message
时间: $(date '+%Y-%m-%d %H:%M:%S')
"
}

# 在关键节点发送通知
notify_progress "auth" "🟢 进行中" "用户认证模块开发中..."
notify_progress "auth" "✅ 完成" "用户认证模块已完成并通过测试"
```

---

## 最佳实践

### 1. 任务拆分原则

**SMART 原则**：
- **S**pecific（具体）：任务描述清晰明确
- **M**easurable（可衡量）：有明确的完成标准
- **A**chievable（可实现）：单个团队能在合理时间内完成
- **R**elevant（相关）：与项目目标直接相关
- **T**ime-bound（有时限）：设定合理的完成时间

**示例**：
```
❌ 不好：实现用户功能
✅ 好：实现用户注册、登录、JWT认证，包含单元测试，预计2小时
```

### 2. 代码规范统一

在项目根目录创建配置文件：

```bash
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# .eslintrc.json
{
  "extends": ["airbnb-base"],
  "rules": {
    "no-console": "warn"
  }
}

# .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2
}
```

### 3. 提交信息规范

使用 Conventional Commits：

```bash
# 格式
<type>(<scope>): <subject>

# 类型
feat: 新功能
fix: 修复
docs: 文档
style: 格式
refactor: 重构
test: 测试
chore: 构建

# 示例
feat(auth): 实现JWT认证
fix(orders): 修复订单状态更新bug
docs(api): 更新API文档
```

### 4. 测试策略

每个团队必须包含测试：

```javascript
// 单元测试示例
describe('Auth Module', () => {
  test('should register new user', async () => {
    const user = await register({
      email: 'test@example.com',
      password: 'password123'
    });
    expect(user).toHaveProperty('id');
  });
  
  test('should login with valid credentials', async () => {
    const token = await login({
      email: 'test@example.com',
      password: 'password123'
    });
    expect(token).toBeTruthy();
  });
});
```

### 5. 文档要求

每个模块包含 README：

```markdown
# 用户认证模块

## 功能
- 用户注册
- 用户登录
- JWT Token 管理
- 密码加密

## API 端点
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout

## 使用示例
\`\`\`javascript
const { register } = require('./auth');
const user = await register({ email, password });
\`\`\`

## 测试
\`\`\`bash
npm test auth
\`\`\`
```

---

## 故障排查

### 问题 1：团队卡住不动

**症状**：进程运行但无输出

**解决**：
```bash
# 查看详细日志
process action:log sessionId:XXX limit:100

# 发送输入（可能在等待确认）
process action:submit sessionId:XXX data:"y"

# 如果真的卡住，重启
process action:kill sessionId:XXX
retry_team "team_name"
```

### 问题 2：合并冲突

**症状**：多个团队修改了同一文件

**解决**：
```bash
# 查看冲突文件
git diff --name-only --diff-filter=U

# 使用 AI 辅助解决
bash pty:true command:"claude '
分析并解决以下合并冲突：

冲突文件：
$(git diff --name-only --diff-filter=U)

冲突内容：
$(git diff)

要求：
1. 理解两个版本的意图
2. 合并功能，保留所有特性
3. 确保代码可运行
4. 解决后提交
'"
```

### 问题 3：测试失败

**症状**：集成后测试不通过

**解决**：
```bash
# 查看失败的测试
npm test -- --verbose

# 逐个模块测试
for team in auth products orders; do
  echo "测试 $team..."
  npm test -- $team
done

# 回滚到最后一个可工作的版本
git log --oneline -10
git reset --hard <commit_hash>
```

### 问题 4：性能问题

**症状**：同时运行太多团队导致系统卡顿

**解决**：
```bash
# 限制并发数
MAX_CONCURRENT=3
active_count=0

for team in "${!TASKS[@]}"; do
  # 等待有空位
  while [ $active_count -ge $MAX_CONCURRENT ]; do
    sleep 5
    # 更新活跃计数
    active_count=$(ps aux | grep "claude\|codex\|opencode" | wc -l)
  done
  
  start_team "$team"
  active_count=$((active_count+1))
done
```

---

## 性能优化

### 1. 增量构建

只重新构建修改的模块：

```bash
# 检测变更
changed_modules=$(git diff --name-only main | cut -d'/' -f1 | sort -u)

# 只重建变更的模块
for module in $changed_modules; do
  cd $module && npm run build
done
```

### 2. 缓存依赖

共享 node_modules：

```bash
# 在主项目安装依赖
npm install

# 各团队链接到主项目
for team_dir in $WORKSPACE_BASE/*/; do
  ln -s $PROJECT_ROOT/node_modules $team_dir/node_modules
done
```

### 3. 并行测试

使用 Jest 的并行功能：

```bash
# 并行运行所有测试
npm test -- --maxWorkers=4

# 只运行变更相关的测试
npm test -- --onlyChanged
```

---

## 总结

多团队编程工作流通过智能编排和并行执行，将开发效率提升 2-5 倍。

**关键要素**：
- 主 agent 作为编排器，负责任务分解和协调
- 多个 coding agent 并行工作，互不干扰
- 实时监控进度，自动处理异常
- 智能冲突检测和解决
- 自动化测试和集成

**适用场景**：
- 大型功能的模块化开发
- 批量 issue 并行修复
- 多仓库同步更新
- 复杂重构任务

**注意事项**：
- 合理拆分任务，确保独立性
- 控制并发数量，避免资源耗尽
- 定期检查进度，及时处理异常
- 重视测试，确保集成质量



# 一人公司模式实战指南

基于 Elvis Sun 的实战经验：**单日 94 次提交，30 分钟合并 7 个 PR，完全不打开编辑器**。

## 核心理念

**本地优先 + 自动化 + 批量处理**

- AI 跑在本地，不依赖云端网页
- 不需要一直盯着屏幕
- 不需要频繁点击权限弹窗
- 让 AI 团队自主工作，你只需要审查结果

## 快速开始

### 1. 一键启动

```bash
cd your-project
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/one-person-company.sh
```

这个脚本会：
1. 从 GitHub Issues 自动获取所有待处理任务
2. 根据任务类型智能分配给最合适的 agent
3. 批量启动多个工作团队并行处理
4. 实时显示进度仪表盘
5. 自动创建 PR 并等待 CI
6. 自动审查和合并通过的 PR
7. 生成详细的日报

### 2. 工作流程

```
早上 9:00
  ↓
运行脚本，启动 AI 团队
  ↓
去喝咖啡 ☕️
  ↓
30 分钟后回来
  ↓
查看仪表盘：7 个 PR 已创建
  ↓
一键合并所有通过 CI 的 PR
  ↓
查看日报：今日 94 次提交 ✅
```

## 关键特性

### 1. 智能任务分配

根据任务类型自动选择最佳 agent：

- **Bug 修复** → Codex（快速定位和修复）
- **新功能** → Claude Code（复杂功能开发）
- **重构** → OpenCode（代码优化）

### 2. 批量并行处理

```bash
# 同时处理 5 个任务
start_all_teams 5

# 或者更激进：10 个并发
start_all_teams 10
```

### 3. 实时仪表盘

```
╔════════════════════════════════════════════════════════════╗
║          一人公司实时仪表盘 - 09:30:15                      ║
╚════════════════════════════════════════════════════════════╝

📊 统计
  总任务数: 15
  活跃团队: 5
  待合并 PR: 3
  今日提交: 47

👥 团队状态
  [#123] 🟢 正在修复登录 bug...
  [#124] 🟢 实现支付功能...
  [#125] ✅ 已完成
  [#126] 🟢 重构数据库查询...
  [#127] ✅ 已完成
```

### 4. 自动 PR 管理

```bash
# 自动创建 PR
gh pr create --title "fix: 修复登录 bug" --body "Closes #123"

# 等待 CI 通过
# 自动合并
gh pr merge --squash --delete-branch

# 清理 worktree
git worktree remove /tmp/issue-123
```

### 5. 日报生成

```markdown
# 一人公司日报 - 2026-03-09

## 📊 统计数据

- 今日提交: 94 次
- 合并 PR: 7 个
- 关闭 Issue: 7 个
- 新增代码: 47 files changed, 2847 insertions(+), 1203 deletions(-)

## 🎯 完成任务

- [#123] 修复用户登录 bug
- [#124] 实现支付功能
- [#125] 优化数据库查询性能
- [#126] 添加单元测试
- [#127] 更新 API 文档
- [#128] 重构认证模块
- [#129] 修复订单状态更新问题
```

## 高级配置

### 自定义并发数

```bash
# 根据机器性能调整
# 8 核 CPU → 5-8 个并发
# 16 核 CPU → 10-15 个并发
start_all_teams 8
```

### 自定义 Agent 选择

```bash
# 修改 select_agent_for_task 函数
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
    docs)
      echo "claude"     # 文档编写
      ;;
    test)
      echo "codex"      # 测试编写
      ;;
  esac
}
```

### 自定义提示词模板

```bash
# 为不同任务类型定制提示词
case $task_type in
  bug)
    prompt="
【紧急 Bug 修复】
Issue: #$issue_num
描述: $title

步骤：
1. 快速定位问题代码
2. 实现最小化修复
3. 添加回归测试
4. 验证修复效果
5. 立即提交

时间限制: 15 分钟
"
    ;;
  feature)
    prompt="
【新功能开发】
Issue: #$issue_num
需求: $title

要求：
1. 理解完整需求
2. 设计模块结构
3. 实现核心功能
4. 编写完整测试
5. 更新文档

质量优先，时间预算: 2 小时
"
    ;;
esac
```

## 最佳实践

### 1. 早上启动，下午收获

```bash
# 早上 9:00
./one-person-company.sh

# 去做其他事情：
# - 开会
# - 喝咖啡
# - 思考产品方向
# - 回复邮件

# 下午 2:00 回来
# 查看结果，合并 PR
```

### 2. 分批处理

```bash
# 第一批：紧急 bug（优先级最高）
start_all_teams 3  # 只处理 bug

# 等待完成后
# 第二批：新功能
start_all_teams 5  # 处理 feature

# 第三批：优化和重构
start_all_teams 3  # 处理 refactor
```

### 3. 设置通知

```bash
# 在脚本中添加通知
notify_completion() {
  local pr_count=$1
  
  # 使用 OpenClaw 发送通知
  message action:send channel:feishu target:your_chat_id \
    message:"
🎉 一人公司日报

今日完成：
- 提交: 94 次
- PR: $pr_count 个
- Issue: 7 个

查看详情: $WORKSPACE_BASE/reports/
"
}
```

### 4. 定期清理

```bash
# 每天结束时清理
cleanup_daily() {
  # 删除已合并分支的 worktree
  git worktree prune
  
  # 归档日志
  tar -czf logs-$(date +%Y%m%d).tar.gz $WORKSPACE_BASE/logs/
  
  # 清理临时文件
  rm -rf $WORKSPACE_BASE/teams/*
}
```

## 性能优化

### 1. 使用 SSD

AI agent 会频繁读写文件，SSD 能显著提升速度。

### 2. 增加内存

```bash
# 每个 agent 约占用 500MB-1GB 内存
# 10 个并发 ≈ 10GB 内存
# 建议至少 16GB RAM
```

### 3. 使用本地模型

```bash
# 对于简单任务，使用本地模型更快
export CODEX_MODEL="local/qwen-2.5-coder"
export CLAUDE_MODEL="local/deepseek-coder"
```

## 故障排查

### 问题：某个团队卡住

```bash
# 查看日志
tail -f $WORKSPACE_BASE/logs/issue-123.log

# 手动介入
cd $WORKSPACE_BASE/teams/issue-123
# 检查状态，手动完成
```

### 问题：PR 创建失败

```bash
# 检查 GitHub CLI 认证
gh auth status

# 重新认证
gh auth login
```

### 问题：CI 一直不通过

```bash
# 查看 CI 日志
gh pr view 123 --json statusCheckRollup

# 手动修复
cd $WORKSPACE_BASE/teams/issue-123
# 修复问题
git commit --amend
git push --force
```

## 成本分析

### 传统方式（手动开发）

```
1 个开发者 × 8 小时 × 7 个任务 = 56 小时
```

### 一人公司模式

```
1 个开发者 × 0.5 小时（启动和审查）× 7 个任务 = 3.5 小时
AI 团队自动处理 = 52.5 小时节省

效率提升：16 倍
```

### API 成本

```
假设每个任务：
- Claude Code: $0.50
- Codex: $0.30
- OpenCode: $0.20

7 个任务 × 平均 $0.35 = $2.45

vs 人工成本：
7 个任务 × 8 小时 × $50/小时 = $2,800

节省：99.9%
```

## 总结

一人公司模式让你从"写代码的人"变成"管理 AI 团队的人"。

**关键要素**：
- 本地优先，不依赖云端
- 批量并行，最大化效率
- 自动化流程，减少人工干预
- 实时监控，掌握全局
- 质量保证，自动测试和审查

**适用场景**：
- 独立开发者
- 初创公司
- 开源项目维护
- 副业项目

**不适用场景**：
- 需要深度思考的架构设计
- 需要人工判断的复杂决策
- 涉及敏感数据的操作

开始你的一人公司之旅吧！🚀

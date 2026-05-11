# AI 驱动编程工作流 - 快速参考

## 🚀 三大核心功能

### 1. 多团队并行开发
```bash
cd your-project
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/claude-code-teams.sh 5
```
- 自动从 GitHub Issues 获取任务
- 智能分配给最合适的 agent
- 并行处理，自动创建 PR

### 2. 一人公司模式
```bash
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/one-person-company.sh
```
- 单日 90+ 次提交
- 30 分钟合并多个 PR
- 完全不打开编辑器

### 3. Playwright 自动化测试
```bash
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/playwright-test-workflow.sh
```
- E2E/API/视觉/性能测试
- 26K tokens (vs 114K MCP)
- 并行运行，自动报告

## 📊 效率对比

| 指标 | 传统方式 | AI 工作流 | 提升 |
|------|---------|----------|------|
| 开发时间 | 8 小时 | 30 分钟 | 16x |
| 测试时间 | 2 小时 | 15 分钟 | 8x |
| 人工参与 | 100% | < 5% | 20x |
| 成本 | $4,000 | $3.50 | 99.9% |

## 🎯 快速场景

### 场景 1：修复 10 个 Bug
```bash
cd your-project
bash examples/claude-code-teams.sh 5
# 30 分钟后：10 个 PR 已创建
```

### 场景 2：开发新功能 + 测试
```bash
# 开发
bash examples/claude-code-teams.sh
# 测试
bash examples/playwright-test-workflow.sh
```

### 场景 3：完整项目开发
```bash
# 一键启动
bash examples/one-person-company.sh
# 去喝咖啡，回来查看结果
```

## 🛠️ 配置

### 调整并发数
```bash
# 根据 CPU 核心数
# 8 核 → 3-5 并发
# 16 核 → 8-10 并发
bash claude-code-teams.sh 5
```

### 选择 Agent
- **Bug 修复** → Codex（快速）
- **新功能** → Claude Code（强大）
- **重构** → OpenCode（优化）

### 测试类型
- **E2E** → 用户流程
- **API** → 接口验证
- **Visual** → UI 回归
- **Performance** → 性能基准

## 📚 详细文档

- [完整文档](./SKILL.md)
- [一人公司模式](./ONE-PERSON-COMPANY.md)
- [Playwright 测试](./PLAYWRIGHT-AUTOMATION.md)

## 🎊 开始使用

```bash
# 1. 进入项目
cd your-project

# 2. 选择模式
bash ~/.openclaw/workspace/skills/multi-team-coding/examples/claude-code-teams.sh

# 3. 查看结果
# - 代码: git log
# - PR: gh pr list
# - 测试: npx playwright show-report
```

**让 AI 成为你的工程团队！** 🚀

# Self-Improving Agent Skill

> "An AI agent that learns from every interaction, accumulating patterns and insights to continuously improve its own capabilities." — Based on 2025 lifelong learning research

## 🧠 技能简介

这是一个**通用自学习系统**，让 AI Agent 能够从每次任务中学习，持续优化自身能力。基于 2025 年终身学习研究设计，实现完整的「经验→模式→改进」反馈循环。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🧠 **三记忆架构** | 语义记忆（模式/规则）+ 情景记忆（经验）+ 工作记忆（会话上下文） |
| 🔄 **自我纠错** | 检测并修复错误的技能指导 |
| ✅ **自我验证** | 定期检查技能准确性和外部引用有效性 |
| 📊 **置信度追踪** | 动态衡量模式可靠性，随应用次数调整 |
| 🛡️ **用户确认门** | 所有技能修改需用户明确批准，安全可控 |
| 👤 **人在回路** | 每次改进后收集用户反馈，持续优化 |

## 🎯 触发条件

### 自动触发
- ✅ 重要任务完成后 → 提取模式，提议技能更新
- ✅ 错误或失败发生时 → 捕获上下文，触发自我纠错
- ✅ 会话结束时 → 合并工作记忆到长期记忆

### 手动触发
用户输入以下指令时激活：
- "自我进化" / "self-improve"
- "总结经验" / "从经验中学习"
- "分析今天的经验" / "总结教训"

## 📦 安装

```bash
clawhub install self-improving-agent-skill
```

## 🚀 使用示例

### 任务完成后自动学习
```
用户：帮我修复这个 bug...
Agent: [修复完成]
→ 自动触发：提取经验 → 抽象模式 → 提议更新
```

### 手动触发学习
```
用户：自我进化
Agent: 正在分析本次会话经验...
       - 提取 3 个新模式
       - 提议更新 2 个技能
       - 请确认是否应用更改
```

### 错误后自我纠错
```
[检测到错误]
→ 捕获错误上下文
→ 识别根本原因
→ 提议修正方案（需用户确认）
→ 应用修正并添加标记
```

## 📁 记忆存储结构

```
{workspace}/memory/self-improving/
├── semantic/
│   └── patterns.json          # 抽象模式和规则
├── episodic/
│   └── YYYY/
│       └── YYYY-MM-DD-{task}.json  # 具体经验
├── working/
│   ├── current_session.json   # 当前会话
│   ├── last_error.json        # 最近错误
│   └── session_end.json       # 会话结束标记
└── index.json                 # 全局索引和指标
```

## 🔄 自我改进流程

```
任务完成 → 提取经验 → 抽象模式 → 提议更改 → ★用户确认★ → 更新技能 → 存入记忆 → 收集反馈
```

### 关键安全机制
1. **用户确认门**：所有修改必须经用户明确批准
2. **可追溯标记**：每次更新带 Evolution/Correction 标记
3. **置信度动态调整**：
   - 成功应用 → +0.05
   - 用户正面反馈 → +0.05
   - 用户负面反馈 → -0.10
   - 导致错误 → -0.15

## 📊 持续学习指标

在 `memory/self-improving/index.json` 中追踪：

| 指标 | 描述 | 目标 |
|------|------|------|
| `patterns_learned` | 学习的模式总数 | 持续增长 |
| `patterns_applied` | 模式应用次数 | 持续增长 |
| `avg_confidence` | 平均置信度 | > 0.8 |
| `self_corrections` | 自我修正次数 | 越低越好 |
| `error_rate_reduction` | 错误减少率 | 负值（改善） |

## 🎓 研究基础

基于以下 2025 年终身学习研究设计：

- [SimpleMem: Efficient Lifelong Memory for LLM Agents](https://arxiv.org/html/2601.02553v1)
- [A Survey on the Memory Mechanism of Large Language Model Agents](https://dl.acm.org/doi/10.1145/3748302)
- [Lifelong Learning of LLM based Agents](https://arxiv.org/html/2501.07278v1)
- [Evo-Memory: DeepMind's Benchmark](https://shothota.medium.com/evo-memory-deepminds-new-benchmark)

## 📝 版本历史

### v0.2.0 (当前版本)
- ✅ 多记忆架构实现（语义 + 情景 + 工作）
- ✅ 用户确认门机制
- ✅ 置信度追踪系统
- ✅ 自我纠错流程
- ✅ 自我验证模板
- ✅ 人在回路反馈收集

### v0.1.0
- 初始版本，基础模式提取功能

## ⚠️ 使用注意

- **不要** 在未确认的情况下自动修改技能文件
- **不要** 覆盖现有记忆内容（始终追加）
- **不要** 从单一经验过度概括（等待 2-3 次出现）
- **要** 为所有模式追踪置信度
- **要** 重视负面反馈（最有价值的信号）
- **要** 使用 Evolution/Correction 标记保证可追溯性

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 改进此技能！

## 📄 许可证

MIT License

---

**作者**: 子然  
**分类**: 元技能 / 自我改进  
**标签**: self-improvement, lifelong-learning, memory, agent-architecture

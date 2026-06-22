# 快速导航索引 (Quick Navigation Index)

> 最后更新: 2026-01-23
> 用途: 快速定位所需文档和工具

---

## 目录

1. [按任务类型导航](#1-按任务类型导航)
2. [按学习路径导航](#2-按学习路径导航)
3. [核心文档速查](#3-核心文档速查)
4. [工具命令速查](#4-工具命令速查)
5. [常见问题快速定位](#5-常见问题快速定位)

---

## 1. 按任务类型导航

### 1.1 创建新 Skill

```
开始 → SKILL.md (主入口)
    ↓
Step 0: 需求澄清/范围收敛 → requirement-elicitation-protocol.md
    ↓
Step 0: 先查现成 Skill（复用优先）→ skill-discovery-protocol.md
    ↓
Step 0: 收敛困难时用五层框架 → task-narrowing-framework.md
    ↓
Step 0: Skill 类型定性 → skill-type-taxonomy.md
    ↓
Step 0: 非技术方法论研究（判断密集领域）→ non-technical-methodology-research.md
    ↓
Step 0: 从 GitHub 学习（技术型任务）→ learn-from-github-protocol.md
    ↓
Step 0: 专家化准备 → latest-knowledge-acquisition.md
    ↓
Step 0: 深度研究 → deep-research-methodology.md
    ↓
Step 0: 领域专家化 → domain-expertise-protocol.md
    ↓
选择模板 → skill-templates.md
    ↓
初始化项目 → scripts/init_skill.py
    ↓
编写内容 → writing-style-guide.md
    ↓
验证 → quick_validate.py + universal_validate.py
```

### 1.2 优化现有 Skill

```
开始 → SKILL.md (主入口)
    ↓
Step 0: 需求澄清/范围收敛（目标不明确时）→ requirement-elicitation-protocol.md
    ↓
Step 0: 先查现成 Skill（准备大改/新增能力时）→ skill-discovery-protocol.md
    ↓
Step 0: Skill 类型定性（影响输出契约与测试）→ skill-type-taxonomy.md
    ↓
Step 0: 获取最新知识 → latest-knowledge-acquisition.md
    ↓
MCP 回退方案 → mcp-fallback-strategies.md
    ↓
Step 0: 领域专家化 → domain-expertise-protocol.md
    ↓
优化内容 → skills-knowledge-base.md
    ↓
验证 → quick_validate.py + universal_validate.py
    ↓
对比官方 → scripts/diff_with_official.py
```

### 1.3 打包分发

```
完成 → SKILL.md (主入口)
    ↓
打包 → scripts/package_skill.py
    ↓
验证 → skills-knowledge-base.md
```

---

## 2. 按学习路径导航

### 2.1 快速上手 (30 分钟)

```
1. 阅读官方最佳实践 (10 分钟)
   → official-best-practices.md

2. 查看示例 (10 分钟)
   → examples.md

3. 选择模板开始实践 (10 分钟)
   → skill-templates.md
```

### 2.2 深入学习 (2 小时)

```
1. 理解核心原则 (30 分钟)
   → skills-knowledge-base.md (第 1-3 节)

2. 学习领域专家化 (30 分钟)
   → domain-expertise-protocol.md

3. 掌握研究方法 (30 分钟)
   → latest-knowledge-acquisition.md
   → deep-research-methodology.md

4. 实践创建 Skill (30 分钟)
   → examples.md → 自己动手
```

### 2.3 成为专家 (1 周)

```
Day 1: 核心概念与原则
  → official-best-practices.md
  → skills-knowledge-base.md (全部)

Day 2: 领域专家化流程
  → domain-expertise-protocol.md
  → deep-research-methodology.md

Day 3: 知识获取与验证
  → latest-knowledge-acquisition.md
  → knowledge-validation-checklist.md

Day 4: 写作与样式规范
  → writing-style-guide.md
  → universality-guide.md

Day 5: 工具与脚本
  → tools-guide.md
  → 阅读 scripts/ 源码

Day 6: 模式与最佳实践
  → patterns.md
  → examples.md (深入研究)

Day 7: 领域知识库
  → domain-knowledge/_index.md
  → 选择相关领域深入学习
```

---

## 3. 核心文档速查

### 3.1 必读文档 (按优先级)

| 优先级 | 文档 | 用途 | 何时阅读 |
|--------|------|------|----------|
| 🔴🔴🔴 | official-best-practices.md | Anthropic 官方指南 | 第一优先 |
| 🔴🔴 | requirement-elicitation-protocol.md | 需求澄清与边界定义 | 写/改 Skill 前 |
| 🔴🔴 | skill-discovery-protocol.md | 先查现成 Skill（复用优先） | 创建新 Skill 前 |
| 🔴🔴🔴 | latest-knowledge-acquisition.md | 知识获取协议 | 创建/优化 Skill 前 |
| 🔴🔴 | domain-expertise-protocol.md | 领域专家化流程 | 深度研究前 |
| 🔴 | deep-research-methodology.md | 深度研究方法 | 成为专家 |
| 🔴 | examples.md | 3 个完整示例 | 不确定时 |
| 🟡 | skill-templates.md | 5 个模板 | 开始创建 |
| 🟡 | skill-type-taxonomy.md | Skill 类型定性（认知操作） | 选模板/写输出契约前 |
| 🟡 | task-narrowing-framework.md | 五层收敛框架 | 需求太宽时 |
| 🟡 | non-technical-methodology-research.md | 非技术方法论研究门禁 | 写作/沟通/决策等 |
| 🟡 | methodology-seed-database.md | 非技术领域方法论种子库 | 不知道从哪找专家/框架时 |
| 🟡 | learn-from-github-protocol.md | 从 GitHub 项目学习并编码为 Skill | 技术型任务/缺少最佳实践时 |

### 3.2 按需阅读文档

| 任务类型 | 首选文档 | 备选文档 |
|----------|----------|----------|
| 需求澄清/范围收敛 | requirement-elicitation-protocol.md | task-narrowing-framework.md |
| 查现成 Skill | skill-discovery-protocol.md | requirement-elicitation-protocol.md |
| Skill 类型定性 | skill-type-taxonomy.md | skill-templates.md |
| 非技术方法论研究 | non-technical-methodology-research.md | knowledge-validation-checklist.md |
| 从 GitHub 学习 | learn-from-github-protocol.md | latest-knowledge-acquisition.md |
| 写 description | writing-style-guide.md (第 1 节) | official-best-practices.md |
| 写正文 | writing-style-guide.md (第 2 节) | skills-knowledge-base.md |
| 写 references | skills-knowledge-base.md (第 4 节) | universality-guide.md |
| 测试模式 | patterns.md (第 3 节) | examples.md |
| 工作流设计 | patterns.md (第 1 节) | examples.md |

---

## 4. 工具命令速查

> 说明：本节命令默认在**项目根目录**运行。如果你已 `cd .claude/skills/skill-expert-skills`，请改用 `python scripts/...`，并把目标路径 `.claude/skills/<skill>` 替换为 `../<skill>`。

### 4.1 初始化与验证

```bash
# 初始化新 Skill
python .claude/skills/skill-expert-skills/scripts/init_skill.py my-new-skill --path .claude/skills

# 快速验证
python .claude/skills/skill-expert-skills/scripts/quick_validate.py .claude/skills/my-skill

# 通用性验证
python .claude/skills/skill-expert-skills/scripts/universal_validate.py .claude/skills/my-skill

# 两者都运行
python .claude/skills/skill-expert-skills/scripts/quick_validate.py .claude/skills/my-skill && \
python .claude/skills/skill-expert-skills/scripts/universal_validate.py .claude/skills/my-skill
```

### 4.2 分析与打包

```bash
# 触发词分析
python .claude/skills/skill-expert-skills/scripts/analyze_trigger.py .claude/skills/my-skill

# 本地检索已安装 Skills（复用优先）
python .claude/skills/skill-expert-skills/scripts/search_skills.py "code review" --root .claude/skills

# 打包 Skill
python .claude/skills/skill-expert-skills/scripts/package_skill.py .claude/skills/my-skill ./dist

# 对比官方版本
python .claude/skills/skill-expert-skills/scripts/diff_with_official.py .claude/skills/my-skill

# 升级旧版 Skill
python .claude/skills/skill-expert-skills/scripts/upgrade_skill.py .claude/skills/my-skill
```

### 4.3 安装依赖

```bash
# 进入项目目录
cd .claude/skills/skill-expert-skills

# 安装依赖
pip install -r scripts/requirements.txt

# 或使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r scripts/requirements.txt
```

---

## 5. 常见问题快速定位

### 5.1 创建 Skill 问题

| 问题 | 定位文档 | 关键章节 |
|------|----------|----------|
| 不知道从哪里开始 | examples.md, skill-templates.md | 快速选择 |
| description 怎么写 | writing-style-guide.md | 第 1 节 |
| SKILL.md 写什么 | official-best-practices.md | Progressive Disclosure |
| 需要什么知识 | domain-expertise-protocol.md | 步骤 1-2 |

### 5.2 优化 Skill 问题

| 问题 | 定位文档 | 关键章节 |
|------|----------|----------|
| 如何获取最新知识 | latest-knowledge-acquisition.md | 全部 |
| MCP 工具不可用 | mcp-fallback-strategies.md | 全部 |
| 如何深度研究 | deep-research-methodology.md | 全部 |
| 领域知识在哪里 | domain-knowledge/_index.md | 列表 |

### 5.3 验证问题

| 问题 | 定位文档 | 关键章节 |
|------|----------|----------|
| quick_validate 报错 | troubleshooting.md | 第 4 节 |
| universal_validate 报错 | troubleshooting.md | 第 4 节 |
| SKILL.md 太长 | official-best-practices.md | Conciseness |
| 通用性问题 | universality-guide.md | Red Flags |

### 5.4 跨项目问题

| 问题 | 定位文档 | 关键章节 |
|------|----------|----------|
| 项目路径问题 | universality-guide.md | Red Flags |
| 项目特定内容 | universality-guide.md | 抽象化步骤 |
| 依赖问题 | troubleshooting.md | 第 4 节 |

---

## 6. 快速决策树

### 6.1 创建 Skill 决策树

```
┌─────────────────────────────────────────┐
│ 创建 Skill 决策树                    │
├─────────────────────────────────────────┤
│                                        │
│  第一次创建？                         │
│    ├─ 是 → examples.md + skill-templates.md (选模板)
│    └─ 否 → 查看现有 Skill，参考结构
│                                        │
│  需要专业知识？                       │
│    ├─ 是 → domain-knowledge/_index.md (查是否已有)
│    └─ 否 → 从 skill-templates.md 开始
│                                        │
│  MCP 工具可用？                      │
│    ├─ 是 → latest-knowledge-acquisition.md
│    └─ 否 → mcp-fallback-strategies.md
└─────────────────────────────────────────┘
```

### 6.2 优化 Skill 决策树

```
┌─────────────────────────────────────────┐
│ 优化 Skill 决策树                    │
├─────────────────────────────────────────┤
│                                        │
│  需要最新知识？                       │
│    ├─ 是 → latest-knowledge-acquisition.md
│    └─ 否 → 跳过，直接优化
│                                        │
│  需要深度研究？                       │
│    ├─ 是 → deep-research-methodology.md
│    └─ 否 → 跳过，使用现有知识
│                                        │
│  有领域知识库？                       │
│    ├─ 是 → domain-knowledge/xxx-expertise.md
│    └─ 否 → 跳过，使用通用知识
│                                        │
│  优化后验证？                         │
│    ├─ 是 → quick_validate.py + universal_validate.py
│    └─ 否 → 跳过验证（不推荐）
└─────────────────────────────────────────┘
```

---

## 7. 领域知识库快速定位

### 7.1 领域知识库映射

| 开发任务 | 推荐知识库 | 文件 |
|----------|------------|------|
| Bug 修复 | Bug Fixing | domain-knowledge/bug-fixing-expertise.md |
| 代码审查 | Code Review | domain-knowledge/code-review-expertise.md |
| 前端开发 | Frontend | domain-knowledge/frontend-expertise.md |
| 后端开发 | Backend | domain-knowledge/backend-expertise.md |
| API 设计 | API Design | domain-knowledge/api-design-expertise.md |
| 安全实现 | Security | domain-knowledge/security-expertise.md |
| 数据库操作 | Database | domain-knowledge/database-expertise.md |
| DevOps 部署 | DevOps | domain-knowledge/devops-expertise.md |

### 7.2 领域知识库现状

| 状态 | 领域 | 数量 |
|------|------|------|
| ✅ 已创建 | Bug 修复, 代码审查, 前端, 后端 | 4 |
| ⚠️ 待创建 (P1) | 安全, 数据库 | 2 |
| 📝 待创建 (P2) | DevOps, API 设计 | 2 |
| 📝 待创建 (P3) | UI/UX 设计 | 1 |

---

## 8. 学习检查清单

### 8.1 快速上手检查

- [ ] 已阅读 official-best-practices.md
- [ ] 已查看 examples.md
- [ ] 已选择 skill-templates.md 中的模板
- [ ] 已运行 init_skill.py 初始化项目
- [ ] 已编写 frontmatter (name, description)
- [ ] 已编写正文内容 (保持简炼)
- [ ] 已运行 quick_validate.py 验证

### 8.2 深入学习检查

- [ ] 已完成一周学习路径 (见 2.3 节)
- [ ] 已理解渐进式披露模式
- [ ] 已掌握领域专家化流程
- [ ] 已理解知识获取协议
- [ ] 已掌握写作规范
- [ ] 已创建至少一个完整 Skill
- [ ] 已通过所有验证检查
- [ ] 已参与代码审查或 peer review

---

## 9. 版本信息

- 本索引版本: v1.0
- 最后更新: 2025-01-17
- 维护者: Claude Agent
- 相关文档: 16 个 references 文件

---

## 10. 获取帮助

如果本索引无法解决问题：

1. **查看完整文档列表**：references/ 目录
2. **查看知识验证**：knowledge-validation-checklist.md
3. **查看故障排除**：troubleshooting.md
4. **查看官方资源**：official-best-practices.md 末尾

**快速反馈路径**：
- GitHub Issues: https://github.com/anthropics/skills/issues
- Discord: https://discord.gg/anthropic
- 文档: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/

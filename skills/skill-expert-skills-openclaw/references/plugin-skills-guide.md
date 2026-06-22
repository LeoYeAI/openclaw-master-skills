# Claude Code 插件 Skill 开发指南

本文档提供为 Claude Code 插件创建 Skill 的专门指导。

---

## 插件 Skill vs 普通 Skill

| 维度 | 普通 Skill | 插件 Skill |
|------|------------|------------|
| **位置** | `$HOME/.claude/skills/` 或 `.claude/skills/` | `plugin-name/skills/` |
| **分发** | 手动复制或 .skill 包 | 随插件一起安装 |
| **打包** | 需要 package_skill.py | 不需要单独打包 |
| **发现** | Claude 全局扫描 | 插件加载时扫描 |
| **依赖** | 独立 | 可依赖插件其他组件 |

---

## 插件目录结构

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── commands/                 # 斜杠命令
├── agents/                   # 自定义 Agent
└── skills/                   # 插件 Skills
    ├── skill-a/
    │   ├── SKILL.md
    │   ├── references/
    │   ├── examples/
    │   └── scripts/
    └── skill-b/
        └── SKILL.md
```

---

## 创建插件 Skill 流程

### Step 1: 初始化目录

```bash
# 在插件根目录下创建
mkdir -p skills/my-skill/{references,examples,scripts}
touch skills/my-skill/SKILL.md
```

### Step 2: 编写 SKILL.md

```yaml
---
name: my-skill
description: |
  This skill should be used when the user asks to "specific action 1",
  "specific action 2", or mentions relevant keywords.

  Provides [capability] within the [plugin-name] plugin context.
---
```

### Step 3: 添加支持文件

根据需要添加:
- `references/` - 详细文档
- `examples/` - 工作示例
- `scripts/` - 工具脚本

### Step 4: 测试

```bash
# 使用插件目录测试
claude --plugin-dir /path/to/my-plugin

# 询问触发问题
> "help me with [trigger phrase]"
```

---

## 插件 Skill 自动发现机制

Claude Code 按以下顺序加载 Skill:

```
1. 扫描 skills/ 目录
2. 查找包含 SKILL.md 的子目录
3. 解析 frontmatter (name + description)
4. 将 metadata 加载到上下文 (~100 words)
5. 当 Skill 触发时，加载 SKILL.md body (<5k words)
6. 按需加载 references/examples/scripts
```

### 发现要求

- [ ] 目录在 `skills/` 下
- [ ] 包含 `SKILL.md` 文件
- [ ] SKILL.md 有有效的 YAML frontmatter
- [ ] frontmatter 包含 `name` 和 `description`

---

## 渐进式披露设计

### 三层加载系统

```
┌─────────────────────────────────────────────────────────────────────┐
│ 层级                         │ 加载时机        │ 大小限制           │
├──────────────────────────────┼────────────────┼───────────────────┤
│ Layer 1: Metadata            │ 始终加载        │ ~100 words        │
│ (name + description)         │                │                    │
├──────────────────────────────┼────────────────┼───────────────────┤
│ Layer 2: SKILL.md body       │ Skill 触发时   │ 1,500-2,000 words │
│ (核心指令和流程)              │                │ (max 5,000)       │
├──────────────────────────────┼────────────────┼───────────────────┤
│ Layer 3: Bundled Resources   │ 按需加载        │ 无限制*           │
│ (references/examples/scripts)│                │                    │
└─────────────────────────────────────────────────────────────────────┘

* scripts 可执行而不加载到上下文
```

### 内容分配指南

**放入 SKILL.md (始终加载)**:
- 核心概念和流程概览
- 快速参考表
- 指向 references 的导航
- 最常见用例

**放入 references/ (按需加载)**:
- 详细模式和高级技术
- 完整 API 文档
- 迁移指南
- 边缘案例处理
- 扩展示例

**放入 examples/ (按需加载)**:
- 完整可运行脚本
- 配置文件示例
- 模板文件

**放入 scripts/ (可执行)**:
- 验证工具
- 自动化脚本
- 解析工具

---

## 插件 Skill 最佳实践

### 1. 保持 SKILL.md 精炼

```markdown
# 目标: 1,500-2,000 words

# ✅ 好的结构
## Overview (200 words)
## Quick Reference Table (300 words)
## Core Workflow (500 words)
## Output Contract (200 words)
## References Navigation (100 words)

# ❌ 避免
## 8,000 words of detailed documentation all in SKILL.md
```

### 2. 强触发 Description

```yaml
# ✅ 好的 description
description: |
  This skill should be used when the user asks to "create a hook",
  "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks",
  or mentions hook events (PreToolUse, PostToolUse, Stop).

  Provides comprehensive hooks API guidance for the plugin-dev plugin.

# ❌ 差的 description
description: |
  Provides hook guidance.
```

### 3. 引用支持文件

```markdown
# 在 SKILL.md 中明确引用

## Additional Resources

### Reference Files
- **`references/patterns.md`** - Detailed hook patterns
- **`references/advanced.md`** - Advanced techniques

### Examples
- **`examples/pre-tool-hook.sh`** - PreToolUse example
- **`examples/validation-hook.py`** - Validation example

### Scripts
- **`scripts/validate-hook.sh`** - Hook validation utility
```

### 4. 写作风格一致性

```markdown
# ✅ 正确: 祈使句
Configure the hook by editing hooks.json.
Validate the configuration with scripts/validate.sh.

# ❌ 错误: 第二人称
You should configure the hook by editing hooks.json.
You can validate the configuration with scripts/validate.sh.
```

---

## 插件 Skill 模板

### 完整模板

```markdown
---
name: my-plugin-skill
description: |
  This skill should be used when the user asks to "action 1",
  "action 2", "action 3", or mentions relevant keywords.

  Provides [capability] within the [plugin-name] plugin context.
---

# My Plugin Skill

## Overview

Brief description of what this skill provides within the plugin.

## Quick Reference

| Task | Command/Action |
|------|----------------|
| Task 1 | `command` |
| Task 2 | `command` |

## Core Workflow

### Step 1: Preparation

Describe preparation steps using imperative form.

### Step 2: Implementation

Describe implementation steps.

### Step 3: Validation

Describe validation steps.

```bash
# Validation command
scripts/validate.sh
```

## Output Contract

### Expected Deliverables
- Deliverable 1
- Deliverable 2

### Quality Criteria
- Criterion 1
- Criterion 2

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Issue 1 | Solution 1 |
| Issue 2 | Solution 2 |

## Additional Resources

### Reference Files
- **`references/patterns.md`** - Detailed patterns
- **`references/advanced.md`** - Advanced techniques

### Examples
- **`examples/example.sh`** - Working example
```

---

## 测试插件 Skill

### 本地测试

```bash
# 方式 1: 使用 --plugin-dir
claude --plugin-dir /path/to/my-plugin

# 方式 2: 符号链接到插件目录
ln -s /path/to/.../my-plugin $HOME/.claude/plugins/my-plugin
```

### 测试清单

- [ ] Skill 在 `/skills` 命令中显示
- [ ] 触发短语正确激活 Skill
- [ ] 指令被正确遵循
- [ ] references 按需加载
- [ ] scripts 可执行
- [ ] examples 完整可用

### 调试

```bash
# 启用调试模式
claude --debug --plugin-dir /path/to/my-plugin

# 检查加载日志
# 查看 Skill 发现和激活信息
```

---

## 与插件其他组件集成

### 与 Commands 集成

```markdown
# 在 SKILL.md 中引用命令

## Quick Start

Run the `/my-command` slash command to get started.

Or use the skill directly by asking about [topic].
```

### 与 Agents 集成

```markdown
# 在 SKILL.md 中引用 Agent

## Advanced Usage

For complex tasks, use the `my-agent` agent:

```
Ask: "Use my-agent to handle this"
```
```

### 共享资源

```
my-plugin/
├── shared/                   # 共享资源
│   └── schemas/
├── skills/
│   └── my-skill/
│       └── SKILL.md          # 可引用 ../../shared/
└── agents/
```

---

## 常见问题

### Q: 插件 Skill 需要打包吗?

不需要。插件 Skill 随插件一起分发，用户安装插件时自动获得所有 Skill。

### Q: 如何处理依赖?

在 SKILL.md 中文档化依赖，或在 `scripts/requirements.txt` 中列出:

```markdown
## Prerequisites

```bash
pip install -r skills/my-skill/scripts/requirements.txt
```
```

### Q: Skill 可以调用插件的其他功能吗?

可以。在 SKILL.md 中引用:
- 其他 Skill: "See the `other-skill` skill for..."
- 命令: "Run `/command` to..."
- Agent: "Use the `agent-name` agent for..."

### Q: 如何处理版本兼容性?

在 description 或 SKILL.md 中注明:

```yaml
description: |
  ...
  Requires: plugin-dev v2.0+
```

---

## 检查清单

### 结构检查

- [ ] Skill 在 `skills/` 目录下
- [ ] 包含 `SKILL.md`
- [ ] 目录名与 frontmatter `name` 匹配

### Frontmatter 检查

- [ ] 有 `name` 字段
- [ ] 有 `description` 字段
- [ ] description 使用第三人称
- [ ] description 包含触发短语

### 内容检查

- [ ] SKILL.md < 3,000 words (推荐 < 2,000)
- [ ] 使用祈使句写作
- [ ] 详细内容在 references/
- [ ] 明确引用支持文件

### 测试检查

- [ ] Skill 正确触发
- [ ] 指令被遵循
- [ ] scripts 可执行
- [ ] examples 完整

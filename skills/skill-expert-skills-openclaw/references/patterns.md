# Skill 模式库 (Patterns)

本文档整合了工作流模式和输出模式，帮助设计高质量的 Skill。

## 目录

- [1. 工作流模式](#1-工作流模式-workflow-patterns)
  - [1.1 顺序工作流](#11-顺序工作流-sequential-workflows)
  - [1.2 条件工作流](#12-条件工作流-conditional-workflows)
  - [1.3 反馈循环工作流](#13-反馈循环工作流-feedback-loop)
- [2. 输出模式](#2-输出模式-output-patterns)
  - [2.1 模板模式](#21-模板模式-template-pattern)
  - [2.2 示例模式](#22-示例模式-examples-pattern)
- [3. 测试与评估模式](#3-测试与评估模式-testing-patterns)
  - [3.1 多模型测试](#31-多模型测试-multi-model-testing)
  - [3.2 评估驱动开发](#32-评估驱动开发-evaluation-driven-development)

---

## 1. 工作流模式 (Workflow Patterns)

### 1.1 顺序工作流 (Sequential Workflows)

对于复杂的任务，将操作分解为清晰的顺序步骤。在 SKILL.md 的开头向 Claude 提供流程概览通常很有帮助：

```markdown
填充 PDF 表单涉及以下步骤：

1. 分析表单 (运行 analyze_form.py)
2. 创建字段映射 (编辑 fields.json)
3. 校验映射 (运行 validate_fields.py)
4. 填充表单 (运行 fill_form.py)
5. 验证输出 (运行 verify_output.py)
```

### 1.2 条件工作流 (Conditional Workflows)

对于具有分支逻辑的任务，引导 Claude 经过决策点：

```markdown
1. 确定修改类型：
   **创建新内容？** → 遵循下方的"创建工作流"
   **编辑现有内容？** → 遵循下方的"编辑工作流"

2. 创建工作流：[步骤]
3. 编辑工作流：[步骤]
```

### 1.3 反馈循环工作流 (Feedback Loop)

**官方强调**：`运行验证器 → 修复错误 → 重复` 是提高输出质量的关键模式。

```markdown
## 验证循环（强制）

1. 运行验证脚本
2. 如有错误 → 修复 → 返回步骤 1
3. 全部通过 → 完成

示例：
┌─────────────────────────────────────────┐
│  运行 quick_validate.py                  │
│       ↓                                  │
│  通过? ─── 是 ──→ 运行 universal_validate │
│       │                    ↓             │
│       否                通过? ─── 是 ──→ ✅ 完成
│       ↓                    │             │
│  修复问题                  否             │
│       ↓                    ↓             │
│  返回步骤 1            修复问题           │
│                            ↓             │
│                       返回步骤 2          │
└─────────────────────────────────────────┘
```

---

## 2. 输出模式 (Output Patterns)

当 Skill 需要产生一致且高质量的输出时，请使用这些模式。

### 2.1 模板模式 (Template Pattern)

为输出格式提供模板。根据需求匹配严格程度。

**对于严格要求（如 API 响应或数据格式）：**

```markdown
## 报告结构

务必使用此精确的模板结构：

# [分析标题]

## 执行摘要
[对关键发现的一段概述]

## 关键发现
- 发现 1 以及支持数据
- 发现 2 以及支持数据
- 发现 3 以及支持数据

## 建议
1. 具体且可操作的建议
2. 具体且可操作的建议
```

**对于灵活指导（当需要适配时）：**

```markdown
## 报告结构

这是一个合理的默认格式，但请根据你的判断进行调整：

# [分析标题]

## 执行摘要
[概述]

## 关键发现
[根据你的发现适配各个章节]

## 建议
[根据具体语境量身定制]

根据具体的分析类型，按需调整章节。
```

### 2.2 示例模式 (Examples Pattern)

对于输出质量依赖于参考示例的 Skill，请提供输入/输出对：

```markdown
## Commit 消息格式

参考这些示例生成 commit 消息：

**示例 1:**
输入: Added user authentication with JWT tokens
输出:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**示例 2:**
输入: Fixed bug where dates displayed incorrectly in reports
输出:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

遵循此风格：类型(范围): 简短描述，然后是详细说明。
```

相比于单纯的文字描述，示例能更清晰地帮助 Claude 理解所需的风格和详细程度。

---

## 3. 测试与评估模式 (Testing Patterns)

### 3.1 多模型测试 (Multi-Model Testing)

**官方建议**：在不同模型上测试 Skill，确保指令足够清晰。

**测试矩阵**：

| 模型 | 用途 | 测试重点 |
|------|------|----------|
| Haiku | 快速/低成本任务 | 指令是否足够明确？ |
| Sonnet | 平衡性能/成本 | 主要功能是否正常？ |
| Opus | 复杂推理任务 | 边缘情况处理如何？ |

**测试流程**：
```
1. 准备 3-5 个代表性测试用例
2. 在 Haiku 上运行 → 如果失败，说明指令不够清晰
3. 在 Sonnet 上运行 → 验证主要功能
4. 在 Opus 上运行 → 验证复杂场景
5. 记录各模型表现差异，优化指令
```

**关键原则**：
- 如果 Haiku 无法正确执行，说明 Skill 指令需要更明确
- 不要依赖模型的"聪明"来弥补指令的模糊

### 3.2 评估驱动开发 (Evaluation-Driven Development)

**核心理念**：像测试驱动开发一样，先定义成功标准，再编写 Skill。

**评估清单模板**：
```markdown
## 评估标准

### 功能性 (必须通过)
- [ ] 触发词正确激活 Skill
- [ ] 核心流程可执行
- [ ] 输出格式符合预期

### 鲁棒性 (应该通过)
- [ ] 边缘输入处理得当
- [ ] 错误情况有明确提示
- [ ] 不同模型表现一致

### 效率 (可选优化)
- [ ] Token 使用合理
- [ ] 无冗余步骤
- [ ] 渐进式披露有效
```

**迭代改进循环**：
```
定义评估标准 → 编写 Skill → 运行测试 → 分析失败 → 改进 Skill → 重复
```


# Skill 模式模板库

本文档提供可直接复制使用的 Skill 模板，覆盖常见开发场景。

---

## 0. 先定“Skill 类型”，再选“模板形态”

本文件的模板更偏“结构形态/复杂度”（最小/只读/脚本驱动/知识密集/插件）。

在选模板之前，建议先判定用户真正需要的 **Skill 类型（认知操作）**：总结/洞察/生成/决策/评估/诊断…

→ `skill-type-taxonomy.md`

类型会直接影响：Output Contract、质量标准、测试用例与 allowed-tools（只读 vs 可写）。

## 模板索引

| 模板 | 适用场景 | 复杂度 | 文件数 |
|------|----------|--------|--------|
| [最小 Skill](#1-最小-skill-模板) | 快速原型/简单任务 | 低 | 1 |
| [只读 Skill](#2-只读-skill-模板) | 代码审查/分析 | 低 | 1 |
| [脚本驱动 Skill](#3-脚本驱动-skill-模板) | 自动化任务 | 中 | 3+ |
| [知识密集 Skill](#4-知识密集-skill-模板) | 专业领域 | 高 | 5+ |
| [插件 Skill](#5-插件-skill-模板) | Claude Code 插件 | 中 | 4+ |

---

## 1. 最小 Skill 模板

**适用场景**: 快速原型、简单提示、个人偏好

### 目录结构

```
my-skill/
└── SKILL.md
```

### SKILL.md 模板

```markdown
---
name: my-skill
description: |
  Brief description of what this skill does.

  Use when:
  - Scenario 1
  - Scenario 2
---

# My Skill

## Quick Start

[最简单的使用方式]

## Instructions

1. Step one
2. Step two
3. Step three

## Output Format

[预期输出格式示例]
```

### 初始化命令

```bash
mkdir -p .claude/skills/my-skill
cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: |
  [描述]

  Use when:
  - [场景1]
  - [场景2]
---

# My Skill

## Instructions

1. [步骤1]
2. [步骤2]
EOF
```

---

## 2. 只读 Skill 模板

**适用场景**: 代码审查、文档分析、安全审计（不需要修改文件）

### 目录结构

```
code-analyzer/
├── SKILL.md
└── references/
    └── checklist.md
```

### SKILL.md 模板

```markdown
---
name: code-analyzer
description: |
  Analyze code for quality, security, and best practices without making changes.

  Use when:
  - Reviewing pull requests or code changes
  - Auditing codebase for security issues
  - Assessing code quality metrics

  Outputs: Analysis report with findings and recommendations.
allowed-tools: [Read, Grep, Glob]
---

# Code Analyzer

## Scope

This skill performs **read-only** analysis. No files will be modified.

## Decision Tree

```
┌─────────────────────────────────────────────────────────┐
│ 分析类型决策                                              │
├─────────────────────────────────────────────────────────┤
│  安全审计?   → 执行 [安全检查流程](#安全检查流程)          │
│  质量评估?   → 执行 [质量评估流程](#质量评估流程)          │
│  性能分析?   → 执行 [性能分析流程](#性能分析流程)          │
└─────────────────────────────────────────────────────────┘
```

## Analysis Workflow

### Step 1: Scope Identification

```bash
# 识别分析范围
find . -name "*.py" -o -name "*.ts" | head -20
```

### Step 2: Pattern Search

```bash
# 搜索潜在问题模式
grep -rn "TODO\|FIXME\|XXX" --include="*.py"
grep -rn "password\|secret\|api_key" --include="*.py"
```

### Step 3: Generate Report

Output format:

```markdown
# Analysis Report

## Summary
- Files analyzed: [N]
- Issues found: [N]
- Risk level: [Low/Medium/High]

## Findings

### Critical
1. [Description] - Location: file.py:123

### Warnings
1. [Description] - Location: file.py:456

## Recommendations
1. [Recommendation]
```

## References

For detailed checklists, see `references/checklist.md`.
```

### 关键特点

- `allowed-tools: [Read, Grep, Glob]` 限制为只读工具
- 明确声明 "No files will be modified"
- 输出为分析报告，不是代码修改

---

## 3. 脚本驱动 Skill 模板

**适用场景**: 重复性任务、确定性操作、需要可靠执行

### 目录结构

```
data-processor/
├── SKILL.md
├── scripts/
│   ├── process.py
│   ├── validate.py
│   └── requirements.txt
└── references/
    └── format-guide.md
```

### SKILL.md 模板

```markdown
---
name: data-processor
description: |
  Process and transform data files with Python scripts.

  Use when:
  - Converting CSV to JSON or vice versa
  - Cleaning and validating data files
  - Batch processing multiple data files

  Requires: Python 3.8+, pandas
  Outputs: Processed files in output/ directory.
allowed-tools: [Read, Write, Execute]
---

# Data Processor

## Prerequisites

```bash
# Install dependencies
pip install -r scripts/requirements.txt
```

## Quick Start

```bash
# Single file processing
python scripts/process.py input.csv --output output.json

# Batch processing
python scripts/process.py data/ --batch --output results/

# Validate output
python scripts/validate.py output.json
```

## Workflow

### Step 1: Prepare Input

- Ensure files are UTF-8 encoded
- Supported formats: CSV, JSON, Excel (.xlsx)

### Step 2: Run Processing

| Task | Command |
|------|---------|
| CSV to JSON | `python scripts/process.py input.csv -f json` |
| JSON to CSV | `python scripts/process.py input.json -f csv` |
| Clean data | `python scripts/process.py input.csv --clean` |
| Validate | `python scripts/validate.py output.json` |

### Step 3: Verify Output

```bash
# Check output structure
python scripts/validate.py output/ --verbose
```

## Output Contract

- **Location**: `output/` directory
- **Naming**: `{original_name}.{new_format}`
- **Encoding**: UTF-8
- **Validation**: All outputs pass schema validation

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Input file missing | Check input path |
| `UnicodeDecodeError` | Wrong encoding | Convert to UTF-8 |
| `ValidationError` | Invalid data format | Check format-guide.md |

## References

- Format specifications: `references/format-guide.md`
```

### scripts/requirements.txt 模板

```
pandas>=1.5.0
openpyxl>=3.0.0
jsonschema>=4.0.0
```

### 关键特点

- 核心逻辑封装在 `scripts/` 中
- 命令表格便于快速查找
- 错误处理表格覆盖常见问题
- 依赖明确列出

---

## 4. 知识密集 Skill 模板

**适用场景**: 需要专业知识、遵循行业标准、多步骤专家判断

### 目录结构

```
api-reviewer/
├── SKILL.md
├── scripts/
│   ├── analyze.py
│   └── requirements.txt
├── references/
│   ├── knowledge-base.md
│   ├── security-checklist.md
│   ├── performance-guide.md
│   └── best-practices.md
└── assets/
    └── templates/
        └── report-template.md
```

### SKILL.md 模板

```markdown
---
name: api-reviewer
description: |
  Expert-level API design review based on industry best practices.

  Use when:
  - Designing new REST/GraphQL APIs
  - Reviewing API specifications (OpenAPI/Swagger)
  - Auditing API security and performance
  - Evaluating versioning strategies

  Requires: OpenAPI spec or API documentation.
  Outputs: Comprehensive design review with scored recommendations.
allowed-tools: [Read, Execute]
---

# API Reviewer

## Prerequisites

Before starting, ensure you have:
- [ ] OpenAPI/Swagger specification (YAML/JSON)
- [ ] OR documented API endpoints with examples
- [ ] Authentication requirements
- [ ] Expected traffic/scaling targets

## Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│ API 审查决策树                                               │
├─────────────────────────────────────────────────────────────┤
│  有 OpenAPI spec? → 自动化分析 + 专家审查                    │
│  仅有文档?        → 人工审查 + 标准对照                      │
│  新设计?          → 领域专家化研究 + 最佳实践应用            │
└─────────────────────────────────────────────────────────────┘
```

## Domain Expertise Gate

Before reviewing new API designs, complete domain research:

1. **Required Domains** (see `references/knowledge-base.md`)
   - RESTful design principles
   - HTTP method semantics
   - Security best practices (OWASP)
   - Versioning strategies

2. **Research Protocol**
   - Consult 2+ authoritative sources per domain
   - Document findings in knowledge base

## Review Workflow

### Phase 1: Automated Analysis

```bash
python scripts/analyze.py api-spec.yaml --output report.json
```

### Phase 2: Expert Review

Use checklists from references/:
- Security: `references/security-checklist.md`
- Performance: `references/performance-guide.md`
- Best practices: `references/best-practices.md`

### Phase 3: Generate Report

Report structure (see `assets/templates/report-template.md`):

```markdown
# API Review Report

## Executive Summary
- Overall Score: [0-100]
- Critical Issues: [N]
- Warnings: [N]

## Detailed Findings

### Security (Score: X/25)
[Findings...]

### Performance (Score: X/25)
[Findings...]

## Recommendations
1. **[P0]** Must fix before release
2. **[P1]** Should fix soon
3. **[P2]** Nice to have
```

## Output Contract

### Required Deliverables
- Scored review report (Markdown)
- Prioritized action items (P0/P1/P2)
- Reference to standards for each finding

### Quality Criteria
- Each finding cites specific standard
- Recommendations are actionable
- Score is justified

## References Navigation

| File | Purpose | When to Read |
|------|---------|--------------|
| `references/knowledge-base.md` | Core domain knowledge | Before first review |
| `references/security-checklist.md` | Security audit points | During security phase |
| `references/performance-guide.md` | Performance patterns | During performance phase |
| `references/best-practices.md` | Industry standards | Throughout review |
```

### 关键特点

- 领域专家化门控（必须先研究）
- 分层知识库（多个 references 文件）
- 结构化评分系统
- 明确的交付标准

---

## 5. 插件 Skill 模板

**适用场景**: Claude Code 插件开发

### 目录结构

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── my-skill/
        ├── SKILL.md
        ├── references/
        │   └── patterns.md
        └── examples/
            └── example.sh
```

### SKILL.md 模板

```markdown
---
name: my-skill
description: |
  This skill should be used when the user asks to "do X", "create Y",
  "configure Z", or mentions specific keywords.

  Provides guidance for [domain] within the plugin context.
---

# My Skill

## Overview

Brief description of what this skill provides within the plugin.

## Core Concepts

### Concept 1

Explain key concept using imperative form.

### Concept 2

More concepts as needed.

## Workflow

### Step 1: Preparation

Describe preparation steps.

### Step 2: Implementation

Describe implementation steps.

### Step 3: Validation

Describe validation steps.

## Quick Reference

| Task | Command |
|------|---------|
| Task 1 | `command` |
| Task 2 | `command` |

## Additional Resources

### Reference Files
- `references/patterns.md` - Detailed patterns

### Examples
- `examples/example.sh` - Working example
```

### 关键特点

- description 使用第三人称 ("This skill should be used when...")
- 正文使用祈使句 (不用 "you should")
- 保持精炼 (1500-2000 words)
- 详细内容移至 references/

---

## 快速选择指南

```
┌─────────────────────────────────────────────────────────────────────┐
│ 模板选择决策树                                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  任务是否需要修改文件?                                                │
│  ├── 否 → 只读 Skill 模板                                            │
│  └── 是 → 继续判断                                                   │
│                                                                      │
│  是否有重复性脚本逻辑?                                                │
│  ├── 是 → 脚本驱动 Skill 模板                                        │
│  └── 否 → 继续判断                                                   │
│                                                                      │
│  是否需要专业领域知识?                                                │
│  ├── 是 → 知识密集 Skill 模板                                        │
│  └── 否 → 继续判断                                                   │
│                                                                      │
│  是否为插件开发?                                                      │
│  ├── 是 → 插件 Skill 模板                                            │
│  └── 否 → 最小 Skill 模板                                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 模板使用最佳实践

### DO

- 从最简单的模板开始，按需增加复杂度
- 保持 SKILL.md 精炼 (< 500 行)
- 将详细内容移至 references/
- 定义清晰的输出契约
- 包含错误处理表格

### DON'T

- 不要一开始就选择最复杂的模板
- 不要在 SKILL.md 中放所有内容
- 不要省略 "Use when:" 和 "Outputs:"
- 不要忘记 allowed-tools 限制

---
name: comprehensive-tech-documentation
description: "Creates layered, comprehensive technical documentation for projects, skills, or systems. Use when user requests 'write technical documentation', 'explain how this works', or 'document the architecture'. Produces 3-4 documents with different depths and purposes."
---

# Comprehensive Technical Documentation

Creates a complete documentation suite that serves different audiences and use cases, from quick reference to deep technical analysis.

## Quick Reference

| User Request | Documentation Output |
|--------------|---------------------|
| "写技术文档" or "Write docs" | Full 4-document suite |
| "解释原理" or "Explain how it works" | Technical Principles doc + Architecture |
| "快速参考" or "Quick reference" | Quick Reference Guide only |
| "画架构图" or "Draw architecture" | Architecture Visualization doc |
| "写导航索引" or "Create index" | Navigation Index doc |

## Background

When documenting complex systems, a single monolithic document fails to serve different audiences:
- New users need quick start guides
- Architects need visual diagrams
- Developers need deep technical details
- Everyone needs navigation

This skill solves that by creating a **layered documentation system** with 3-4 complementary documents.

## Solution

### The Documentation Suite

Create these documents (adapt based on project scope):

1. **📖 Technical Principles** (技术原理文档.md)
   - Deep dive into how the system works
   - Design philosophy and decisions
   - Implementation details
   - Best practices
   - **Target**: Developers, contributors
   - **Reading time**: 30-60 minutes

2. **📊 Architecture Visualization** (架构与流程可视化.md)
   - Mermaid diagrams for architecture
   - Flow charts and sequence diagrams
   - State machines
   - Data flow diagrams
   - **Target**: Architects, visual learners
   - **Reading time**: 15-30 minutes

3. **🔖 Quick Reference Guide** (快速参考指南.md)
   - Templates and examples
   - Command cheat sheets
   - Field definitions
   - Troubleshooting
   - **Target**: All users (most frequently used)
   - **Reading time**: 5-15 minutes

4. **🗺️ Navigation Index** (README-文档索引.md or 文档索引.md)
   - Document comparison table
   - Learning paths by role
   - Scenario-based navigation
   - FAQ with document links
   - **Target**: First-time users, navigators
   - **Reading time**: 5 minutes

### Step-by-Step Workflow

#### Phase 1: Deep Understanding (15-30 minutes)

Read core files to understand the system:

```markdown
MUST READ:
- Main entry point (SKILL.md, README.md, main config)
- Core implementation files
- Configuration files
- Integration documentation

PARALLEL READ:
- Use parallel file reads for independent files
- Group related files (e.g., all configs together)
```

**Decision point**: If system is small (<5 files), might only need 1-2 docs.

#### Phase 2: Analysis & Extraction (10-15 minutes)

Extract key information:

1. **Core Concepts** - What problem does it solve?
2. **Architecture** - What are the major components?
3. **Data Flow** - How does information move?
4. **Integration Points** - How does it connect to other systems?
5. **User Workflows** - What are the main use cases?
6. **Pain Points** - What commonly goes wrong?

#### Phase 3: Document Creation (30-60 minutes)

Create documents in this order:

**1. Technical Principles (技术原理文档.md)**

Structure:
```markdown
# Title - 技术原理详解

## 目录
[Table of contents with clear sections]

## 核心概念
1.1 设计理念
1.2 核心机制

## 系统架构
2.1 组件结构 (with tree diagram)
2.2 数据分层

## 工作原理
3.1 触发条件
3.2 处理流程
3.3 输出机制

## 技术实现
4.1 关键代码实现
4.2 配置系统
4.3 扩展机制

## 数据流转
5.1 完整生命周期
5.2 跨系统通信

## 核心循环/机制
6.1 主要循环
6.2 反馈机制

## 集成方式
7.1 Platform A
7.2 Platform B
7.3 Generic setup

## 最佳实践
8.1 应该做
8.2 不应该做
8.3 维护建议

## 技术洞察
9.1 设计哲学
9.2 局限性
9.3 与其他系统对比

## 实际应用示例
10.1 场景A
10.2 场景B

## 总结
```

**Word count**: 5000-8000 words for complex systems

**2. Architecture Visualization (架构与流程可视化.md)**

Include these diagram types:

```markdown
# Title - 架构与流程可视化

## 1. 核心架构图
### 1.1 系统层次架构
[Mermaid: graph TB with subgraphs]

### 1.2 数据流架构
[Mermaid: flowchart LR showing data movement]

## 2. 核心流程
### 2.1 主要流程完整序列
[Mermaid: sequenceDiagram]

### 2.2 子流程
[Mermaid: flowchart TD with decision nodes]

## 3. 触发条件映射
[Mermaid: flowchart TD - decision tree]

## 4. 跨系统通信
[Mermaid: graph showing system interactions]

## 5. 模式识别机制
[Mermaid: flowchart showing pattern matching]

## 6. 文件系统拓扑
[Mermaid: graph TD showing directory structure]

## 7. 状态转换图
[Mermaid: stateDiagram-v2]

## 8. 集成模式对比
[Mermaid: comparison graphs]

## 9. 性能与扩展性
[Mermaid: growth curves]

## 10. 监控与度量
[Mermaid: metrics dashboard]
```

**Diagram count**: 10-15 Mermaid diagrams

**3. Quick Reference Guide (快速参考指南.md)**

Structure:
```markdown
# Title - 快速参考指南

## 📚 一分钟了解
[Core concept in 3-5 bullet points]

## 🎯 何时使用
[Trigger conditions table]

## 📝 模板
[Copy-paste templates with all fields]

## 🎨 优先级/分类指南
[Reference tables]

## 🚀 提升/决策指南
[Decision flowchart in text]

## 🔧 快速安装
[Copy-paste commands for each platform]

## 📊 字段说明
[All field definitions in tables]

## 🛠️ 常用命令
[Bash/PowerShell command examples]

## 📦 文件结构
[ASCII tree diagrams]

## 🔄 工作流程示例
[3-5 numbered scenarios with outcomes]

## 💡 最佳实践
[✅ DO and ❌ DON'T lists]

## 🆘 故障排查
[Problem-solution pairs]

## 🔖 速查卡
[Super compact cheat sheet at the end]
```

**Word count**: 2500-3500 words

**4. Navigation Index (README-文档索引.md)**

Structure:
```markdown
# Title - 文档索引

## 📚 文档导航
[3-column table: Quick Start | Architecture | Deep Dive]

## 📖 文档列表
[Table with: Doc name, Type, Word count, Summary, Audience]

## 🗺️ 学习路径
### 路径A: 快速上手（30分钟）
[Numbered steps with specific sections to read]

### 路径B: 深入理解（1小时）
[Longer path]

### 路径C: 精通全貌（2小时）
[Complete path]

## 💡 按场景查找
[5-10 common scenarios with recommended docs]

## 📊 文档内容对比
[Matrix showing topic coverage across all docs]

## 🎯 快速问题解答
[10 FAQ with links to specific doc sections]

## 🔗 相关资源
[External links]

## 📝 文档更新记录

## 💬 反馈与贡献

## 🎓 下一步
[Role-based next actions in 2x2 table]
```

**Word count**: 2000-3000 words

#### Phase 4: Visualization (20-30 minutes)

Create Mermaid diagrams for Architecture doc:

**Essential diagrams:**
1. System architecture (graph TB with subgraphs)
2. Data flow (flowchart LR)
3. Main sequence flow (sequenceDiagram)
4. Decision tree (flowchart TD)
5. State machine (stateDiagram-v2)
6. File system topology (graph TD)

**Mermaid best practices:**
- Use `subgraph` for logical grouping
- Apply `style` for visual hierarchy (colors)
- Keep each diagram focused on one aspect
- Add `Note` annotations for clarity

#### Phase 5: Quality Check (10 minutes)

Verify completeness:

- [ ] All documents use consistent terminology
- [ ] Cross-references between docs work
- [ ] Code examples are syntactically correct
- [ ] Mermaid diagrams render properly
- [ ] File paths are accurate
- [ ] Tables are properly formatted
- [ ] Each doc has clear target audience
- [ ] Reading time estimates are realistic
- [ ] Documents are in logical reading order

### Output Decision Tree

```
How complex is the system?
│
├─ Simple (1-2 files, single purpose)
│  └─ Create: Quick Reference only
│
├─ Medium (3-10 files, clear structure)
│  └─ Create: Quick Reference + Technical Principles
│
├─ Complex (10+ files, multiple subsystems)
│  └─ Create: All 4 documents
│
└─ Massive (50+ files, enterprise scale)
   └─ Create: All 4 + additional domain-specific docs
```

## Document Templates

### Technical Principles Template

```markdown
# [System Name] - 技术原理详解

## 目录
[auto-generated or manual]

---

## 核心概念

### 1.1 设计理念

> [One-sentence design philosophy quote]

[System Name] 的核心理念是：

> **[Core idea in bold quote]**

这个框架解决了以下核心问题：

1. **[Problem 1]**：[Description]
2. **[Problem 2]**：[Description]

### 1.2 核心机制

[ASCII or text diagram showing the main loop]

---

## 系统架构

### 2.1 组件结构

```
[Directory tree with comments]
project/
├── component-a/    # Purpose
├── component-b/    # Purpose
└── config/         # Purpose
```

### 2.2 数据分层

```
[Layer diagram in ASCII]
┌──────────────────┐
│   Layer 3        │ ← Description
└──────────────────┘
        ▲
        │ relationship
        │
┌──────────────────┐
│   Layer 2        │ ← Description
└──────────────────┘
```

[Continue with all sections...]

---

## 总结

**[System Name]** 是一个[description]，它通过系统化地：

1. **[Action 1]**：[Description]
2. **[Action 2]**：[Description]

[Closing statement about value]

---

**文档版本**: 1.0
**最后更新**: [Date]
**作者**: GitHub Copilot (Claude Sonnet 4.5)
```

### Quick Reference Template

```markdown
# [System Name] - 快速参考指南

## 📚 一分钟了解

**[System Name]** [one-line description]

### 核心概念
```
[Simple flow diagram]
Step1 → Step2 → Step3
```

- **[Concept 1]**：[Description]
- **[Concept 2]**：[Description]

---

## 🎯 何时使用

| 场景 | 记录位置 | 类别 |
|------|---------|------|
| [Trigger] | [Location] | [Type] |

---

## 📝 记录模板

### [Template Type 1]

```markdown
[Actual template content to copy-paste]
```

[Continue...]

---

**版本**: 1.0  
**更新**: [Date]  
**适用**: [System] v[version]+  

**提示**: 保持此指南在手边，快速查阅关键信息！ 📖
```

## Common Variations

### Variation A: Codebase Documentation

For documenting a code repository:

**Focus on:**
- Architecture patterns
- API design
- Code organization
- Development workflow
- Testing strategy

**Additional diagrams:**
- Class diagrams
- API flow
- Database schema

### Variation B: Skill Documentation

For documenting an AI agent skill:

**Focus on:**
- When to trigger
- Decision logic
- Output format
- Integration with other skills

**Additional sections:**
- Trigger conditions
- Examples of good/bad prompts

### Variation C: Tool/Library Documentation

For documenting a tool or library:

**Focus on:**
- Installation steps
- Configuration options
- API reference
- Usage examples
- Troubleshooting

**Additional sections:**
- Compatibility matrix
- Performance benchmarks

### Variation D: Process Documentation

For documenting a workflow or methodology:

**Focus on:**
- Step-by-step procedures
- Decision points
- Quality gates
- Roles and responsibilities

**Additional diagrams:**
- Swimlane diagrams
- Gantt charts

## Gotchas

⚠️ **Don't create all 4 docs for simple systems** - Use judgment. A 50-line script doesn't need 4 documents.

⚠️ **Don't duplicate content** - Each document should have a distinct purpose. Cross-reference instead of copy-paste.

⚠️ **Don't skip the index** - Without navigation, users get lost. The index document is crucial for multi-doc suites.

⚠️ **Don't use broken Mermaid syntax** - Test diagrams before finalizing. Common errors:
- Missing closing quotes
- Invalid node IDs
- Unsupported diagram features

⚠️ **Don't ignore reading time estimates** - Help users plan their time. Be realistic about document length.

⚠️ **Don't mix languages inconsistently** - If user requests Chinese, use Chinese for all headings and body text. Keep code/commands in original language.

⚠️ **Don't assume prior knowledge** - Define acronyms and technical terms, especially in Quick Reference.

⚠️ **Don't forget visual hierarchy** - Use emojis (📖 🎯 💡) and formatting to make docs scannable.

## Writing Style Guidelines

### For Technical Principles Doc

- **Tone**: Academic but accessible
- **Depth**: Assume reader wants to understand "why" not just "how"
- **Code examples**: Include actual implementations with explanations
- **Length**: Don't shy away from detail; this is the deep-dive doc

### For Architecture Visualization Doc

- **Diagram-first**: Let diagrams tell the story
- **Minimal text**: Just enough to explain what you're looking at
- **Consistent notation**: Use same colors/shapes for same concepts
- **Progressive complexity**: Start simple, add detail gradually

### For Quick Reference Doc

- **Tone**: Practical and direct
- **Format**: Heavy use of tables, lists, and code blocks
- **No fluff**: Every sentence should provide actionable information
- **Scannable**: Use visual markers (✅ ❌ 🔴 🟢) liberally

### For Navigation Index Doc

- **Tone**: Welcoming and guiding
- **Purpose**: Help users find what they need fast
- **Structure**: Clear hierarchy with visual tables
- **Empathy**: Anticipate what different users need

## Localization

When creating Chinese documentation:

**Do:**
- ✅ Use Chinese for all headings and body text
- ✅ Keep technical terms in English within backticks: `SKILL.md`
- ✅ Use Chinese punctuation (，。；：)
- ✅ Provide clear Chinese translations for concepts
- ✅ Use emojis universally (work in all languages)

**Don't:**
- ❌ Mix English and Chinese in the same sentence without backticks
- ❌ Translate file names or commands
- ❌ Use English-style comma in Chinese text
- ❌ Translate acronyms (keep API as API, not 应用程序接口)

## Integration with Other Skills

**Pairs well with:**

- **self-improvement** - After creating docs, log if you learned better documentation patterns
- **proactive-agent** - Proactively offer to update docs when code changes
- **agent-customization** - Document your custom skills using this approach

## Quality Checklist

Before delivering documentation:

- [ ] All 4 documents created (or justified why fewer)
- [ ] Reading time estimates in index
- [ ] At least 8 Mermaid diagrams in Architecture doc
- [ ] Quick Reference has copy-paste templates
- [ ] Technical Principles explains "why" not just "what"
- [ ] Index provides learning paths for 3 personas
- [ ] Cross-references between docs work
- [ ] No broken Mermaid syntax
- [ ] Consistent terminology across all docs
- [ ] Each doc has version and last-updated date
- [ ] Troubleshooting section in Quick Reference
- [ ] File tree diagrams use consistent formatting
- [ ] Tables are aligned and complete
- [ ] Code blocks have language specified
- [ ] Chinese localization follows guidelines (if applicable)

## Example Prompt Patterns

**To trigger this skill:**

✅ Good prompts:
- "当前skill的原理是什么，写一份详尽文档"
- "Write comprehensive documentation for this codebase"
- "Document the architecture with diagrams"
- "Create a quick reference guide and full technical docs"

✅ Clarifying questions (if needed):
- "Who is the primary audience?" (if unclear)
- "Is this for internal use or public consumption?"
- "Do you need Chinese or English documentation?"

❌ Avoid confusion with:
- "Write a README" (too vague - might just need one doc)
- "Add comments to the code" (different skill)
- "Create API documentation" (use API-specific skill if available)

## Related

- **agent-customization** - For creating SKILL.md files specifically
- **self-improvement** - For logging documentation patterns you discover
- **proactive-agent** - For maintaining docs over time

## Source

- **Created**: 2026-03-05
- **Origin**: Extracted from conversation where comprehensive docs were created for self-improving-agent skill
- **Pattern**: Successfully applied to document a complex AI agent skill with multiple subsystems
- **Validation**: Created 4 documents totaling ~13,000 words with 10+ diagrams

---

**Note:** This skill produces 5,000-15,000 words of documentation. Budget 1-2 hours for complete execution on complex systems.

**Tip:** Start by reading core files in parallel to save time. The understanding phase is critical - don't rush it.

**Remember:** Different users need different depths. The layered approach ensures everyone finds what they need. 📚

# Knowledge Classification Guide

## Three-Type Classification with Tag System

### Overview

提取的知识分为三种类型，每个条目可以同时标记多个类型：

| 类型 | 定义 | 写入文件 |
|------|------|---------|
| **Thinking Pattern** (思维框架) | 可复用决策框架 | `thinking-patterns.md` |
| **Principle** (原则) | 高度抽象指导原则 | `thinking-patterns.md` |
| **Concept** (概念) | 领域特定知识 | `concepts.md` |

---

### Thinking Patterns (思维框架)

**Definition**: Reusable mental models, decision frameworks, or strategic principles that can be applied across different contexts.

**Characteristics**:
- Provides a lens for future decisions
- Can be triggered by specific situations
- Has broad applicability beyond the original domain
- Includes decision rules or heuristics

**Examples**:
- **Disruptive Innovation Framework**: "When evaluating competition, check if you're serving top customers (vulnerable) or edge markets (opportunity)"
- **Escape Mechanism**: "When seeing inequality, ask 'who is escaping?' before judging"
- **First Principles Thinking**: "Break down problems to fundamental truths, rebuild from there"

**Write format**:
```markdown
## [Framework Name] - [Book Title]

**标签**: thinking-pattern
**思维框架 (Framework)**: [核心逻辑]
**决策原则 (Decision Rule)**: 在XX场景下，应该XX而非XX
**盲区警告 (Blind Spots)**: 小心XX情况
**反射弧 (Trigger Pattern)**: 看到XX信号 → 联想到这个模型 → 判断/行动
**来源**: [Book Title] - [Author]
**日期**: YYYY-MM-DD
```

---

### Principles (原则)

**Definition**: Highly abstract, universal guiding principles that shape thinking but may not directly function as decision tools.

**Characteristics**:
- Extremely broad applicability
- Often expressed as a single sentence or rule
- More abstract than Thinking Patterns (less specific trigger/action)
- Guides meta-level thinking rather than specific decisions

**Examples**:
- **Pareto Principle (二八法则)**: "80% of results come from 20% of effort"
- **Occam's Razor (奥卡姆剃刀)**: "Among competing hypotheses, prefer the simplest"
- **Lindy Effect (林迪效应)**: "The longer something has survived, the longer it will continue"

**Write format**:
```markdown
## [Principle Name] - [Book Title]

**标签**: principle
**核心原则 (Core Principle)**: [一句话表述]
**适用范围 (Scope)**: 在什么层面/领域适用？
**局限性 (Limitations)**: 什么情况下不适用？
**来源**: [Book Title] - [Author]
**日期**: YYYY-MM-DD
```

---

### Concepts (具体概念)

**Definition**: Specific domain knowledge, terminology, facts, or theories that provide understanding but aren't directly reusable as decision tools.

**Characteristics**:
- Domain-specific knowledge
- Explains "what" or "how" something works
- May not have broad applicability
- Factual or descriptive

**Examples**:
- **Variolation**: "18th-century inoculation technique using live smallpox virus"
- **Energy Density Ceiling**: "Physical limit to battery energy storage per unit volume"
- **Edge AI Models**: "AI models running on local devices (watches, phones) vs cloud"

**Write format**:
```markdown
## [Concept Name] - [Book Title]

**标签**: concept
**定义 (Definition)**: [简洁定义]
**上下文 (Context)**: 在什么领域/场景重要？
**关联理论 (Related Theories)**: 与哪些思维框架相关？
**来源**: [Book Title] - [Author]
**日期**: YYYY-MM-DD
```

---

## Decision Tree

```
提取的知识
    │
    ├─ 能否在不同领域复用为决策工具？
    │  └─ YES → Thinking Pattern
    │  └─ NO ↓
    │
    ├─ 是否是高度抽象的通用指导原则？
    │  └─ YES → Principle
    │  └─ NO ↓
    │
    └─ 是否是领域特定的知识/术语？
       └─ YES → Concept
       └─ NO → Re-evaluate (might be too vague)
```

---

## Tag System

每个条目可标记一个或多个 tags：

```
tags: ["thinking-pattern"]
tags: ["principle"]
tags: ["concept"]
tags: ["thinking-pattern", "principle"]   ← 边界模糊时
tags: ["thinking-pattern", "concept"]     ← 拆分时
```

**在写入文件时**，tags 体现在 `**标签**` 行：
```markdown
**标签**: thinking-pattern, principle
```

---

## Edge Cases

### When Both Pattern and Principle Apply
- 如果一个知识既是可复用框架又是抽象原则 → 标记两个 tag
- Example: "Antifragility" — 既是一个决策框架（Thinking Pattern），也是一个通用原则（Principle）
- 写入 `thinking-patterns.md`，标签为 `thinking-pattern, principle`

### When Both Pattern and Concept Apply
- 核心理论 → Concept
- 从理论派生的决策应用 → Thinking Pattern
- 可以拆分为两个条目，分别写入不同文件

**Example**:
- Concept: "Disruptive Innovation Theory — Christensen's research on how incumbents fail"
- Thinking Pattern: "When evaluating markets, prioritize 'edge' over 'top' customers"

### When Nothing Clearly Applies
- 如果提取的知识太模糊或太泛（如 "创新很重要"）→ 丢弃，要求重新提取更具体的模型
- 底线：每个条目必须能回答 "这个知识能帮我在什么场景做什么决定？"

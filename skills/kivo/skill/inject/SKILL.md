---
name: context-inject
description: "系统级 Skill：系统自动触发，非用户直接调用。为当前任务自动注入相关知识上下文。根据请求语义检索知识库，按注入策略格式化后注入 Agent 上下文窗口。"
trigger-mode: system
---

# ContextInjectSkill — 上下文注入

为 Agent 当前任务自动注入相关知识上下文，提升回答质量。

## 触发词

system:context-inject

## 使用方式

```bash
# 为查询注入相关上下文
tsx scripts/inject.ts --query "当前用户请求" [--budget <tokens>]

# 指定注入格式
tsx scripts/inject.ts --query "设计决策" --format markdown --budget 3000
```

## 核心路径

`src/injection/context-injector.ts` → `src/injection/injection-policy.ts`

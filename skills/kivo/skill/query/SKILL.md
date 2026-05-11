---
name: knowledge-query
description: "检索知识库并返回相关知识条目。支持语义搜索，按相关性排序，可指定 token 预算控制返回量。"
---

# KnowledgeQuerySkill — 知识查询

基于语义搜索检索知识库，返回与查询最相关的知识条目。

## 触发词

查知识、搜索记忆、搜索知识库、你知道关于、查一下之前的决策、有没有相关经验、你还记得、recall、query knowledge、search knowledge、what do you know about

## 使用方式

```bash
# 查询相关知识（默认 budget 2000 tokens）
tsx scripts/query.ts --query "用户的交付偏好"

# 指定 token 预算
tsx scripts/query.ts --query "架构决策" --budget 4000
```

## 核心路径

`src/search/semantic-search.ts` → `src/repository/knowledge-repository.ts`

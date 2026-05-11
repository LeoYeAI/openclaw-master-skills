---
name: conflict-resolve
description: "处理知识冲突的人工裁决请求。展示冲突详情，支持用户选择保留策略（新覆旧、保留旧、合并、标记待定）。"
---

# ConflictResolveSkill — 冲突裁决

处理知识库中的冲突条目，支持人工裁决和自动解决策略。

## 触发词

知识冲突、矛盾了、哪个是对的、这两条知识矛盾了、用新的、保留旧的、帮我决定哪个对、resolve conflict、conflict、which one is correct

## 使用方式

```bash
# 列出待裁决冲突
tsx scripts/resolve.ts --list

# 裁决指定冲突（保留新条目）
tsx scripts/resolve.ts --id <conflict-id> --verdict keep-incoming

# 裁决指定冲突（保留旧条目）
tsx scripts/resolve.ts --id <conflict-id> --verdict keep-existing

# 合并两条
tsx scripts/resolve.ts --id <conflict-id> --verdict merge
```

## 核心路径

`src/conflict/conflict-resolver.ts` → `src/conflict/conflict-record.ts`

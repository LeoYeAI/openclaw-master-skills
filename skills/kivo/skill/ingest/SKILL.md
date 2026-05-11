---
name: knowledge-ingest
description: "从对话或文档中提取并存储结构化知识。支持文件和文本输入，自动执行知识提取、冲突检测和入库。"
---

# KnowledgeIngestSkill — 知识摄入

从对话、文档、代码中自动提取结构化知识，经冲突检测后存入知识库。

## 触发词

学习这个、记住、摄入知识、记住这个、把这段话存下来、从这篇文档提取知识、学习这个文件、保存到知识库、ingest、learn this、save knowledge、remember this、extract knowledge

## 使用方式

```bash
# 从文件摄入
tsx scripts/ingest.ts --file ./docs/design.md --source "design-doc"

# 从文本摄入
tsx scripts/ingest.ts --text "用户偏好短答，先结论后证据" --source "conversation"
```

## 核心路径

`src/extraction/` → `src/pipeline/engine.ts` → `src/conflict/` → `src/repository/`

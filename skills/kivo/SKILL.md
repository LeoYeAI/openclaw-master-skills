---
name: kivo
description: "KIVO — Agent Knowledge Iteration Engine. A knowledge management system for AI agents that provides knowledge extraction, storage, search, conflict resolution, and iterative learning capabilities. Use when building agent systems that need persistent, evolving knowledge bases."
license: MIT
---

# KIVO — Agent Knowledge Iteration Engine

Agent 知识平台。覆盖知识提取、存储、检索、迭代、调研、图谱、工作台全生命周期。

## Features

- Knowledge extraction and storage (SQLite-backed)
- Semantic and keyword search
- Conflict detection and resolution
- Knowledge distribution and subscription
- Multi-agent authentication and permissions
- Bootstrap initialization and health checks
- Document gate for doc-code consistency

## Quick Start

```bash
npm install @self-evolving-harness/kivo
```

```typescript
import { KnowledgeStore, ExtractionPipeline } from '@self-evolving-harness/kivo';

const store = new KnowledgeStore({ dbPath: './knowledge.db' });
const pipeline = new ExtractionPipeline({ store });
await pipeline.extract(document);
```

## CLI

```bash
npx kivo init        # Initialize knowledge base
npx kivo health      # Health check
npx kivo capabilities # Show capabilities
```

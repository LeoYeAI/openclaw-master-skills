# API 类名速查表

本文档列出所有导出的类名及其职责，避免测试时产生误解。

---

## 一、核心管理器类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `PerceptionMemoryStore` | `scripts.perception` | 感知记忆存储 | `create_session()`, `store_conversation()` |
| `ShortTermMemoryManager` | `scripts.short_term` | 短期记忆管理 | `store()`, `get_stats()`, `get_topic_summary()` |
| `LongTermMemoryManager` | `scripts.long_term` | 长期记忆管理 | `update_user_profile()`, `update_procedural_memory()` |
| `AsynchronousExtractor` | `scripts.short_term` | 短期→长期记忆提炼 | `extract()`, `get_stats()`, `get_last_insight()` |

---

## 二、洞察分析类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `ShortTermInsightAnalyzer` | `scripts.short_term_insight` | 短期记忆洞察分析 | `analyze()`, `get_stats()` |
| `InsightModule` | `scripts.insight_module` | 洞察生成模块 | `observe()`, `get_insights()` |
| `InsightPool` | `scripts.insight_module` | 洞察池管理 | `add()`, `get_active()`, `get_stats()` |

---

## 三、状态管理类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `GlobalStateCapture` | `scripts.state_capture` | 全局状态捕捉 | `capture()`, `create_checkpoint()`, `restore()` |
| `StateConsistencyValidator` | `scripts.state_consistency_validator` | 状态一致性校验 | `validate()`, `auto_fix()` |
| `StateInferenceEngine` | `scripts.state_inference_engine` | 状态推理引擎 | `infer()`, `predict_next()` |

---

## 四、检索相关类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `RetrievalDecisionEngine` | `scripts.retrieval_decision_engine` | 检索决策引擎 | `decide()`, `should_retrieve()` |
| `RetrievalQualityEvaluator` | `scripts.retrieval_quality_evaluator` | 检索质量评估 | `evaluate()`, `get_scores()` |

---

## 五、记忆处理类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `CognitiveModelBuilder` | `scripts.cognitive_model_builder` | 认知模型构建 | `build()`, `get_model()` |
| `CausalChainExtractor` | `scripts.causal_chain_extractor` | 因果链提取 | `extract()`, `get_chains()` |
| `KnowledgeGapIdentifier` | `scripts.knowledge_gap_identifier` | 知识缺口识别 | `identify()`, `get_gaps()` |
| `CrossSessionMemoryLinker` | `scripts.cross_session_memory_linker` | 跨会话关联 | `link()`, `get_linked_memories()` |
| `MemoryForgettingMechanism` | `scripts.memory_forgetting_mechanism` | 遗忘机制 | `decay()`, `cleanup()` |

---

## 六、异步写入类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `AsyncWriter` | `scripts.async_writer` | 异步写入器 | `write()`, `get_stats()`, `flush()` |
| `BatchedWriter` | `scripts.batched_writer` | 批量写入器 | `write()`, `get_stats()`, `flush_all()` |

---

## 七、上下文编排类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `ContextOrchestrator` | `scripts.context_orchestrator` | 上下文编排器 | `prepare()`, `get_context()` |
| `ContextReconstructor` | `scripts.context_reconstructor` | 上下文重构器 | `reconstruct()`, `get_package()` |
| `MultiSourceCoordinator` | `scripts.multi_source_coordinator` | 多源协调器 | `coordinate()`, `register_source()` |

---

## 八、工具类

| 类名 | 导入路径 | 职责 | 主要方法 |
|------|----------|------|----------|
| `HeatManager` | `scripts.heat_manager` | 热度管理 | `calculate()`, `apply_policy()` |
| `ConflictResolver` | `scripts.conflict_resolver` | 冲突解决 | `resolve()`, `detect_conflicts()` |
| `TokenBudgetManager` | `scripts.token_budget` | Token预算管理 | `allocate()`, `get_stats()` |
| `MemoryIndexer` | `scripts.memory_index` | 记忆索引 | `index()`, `search()`, `get_stats()` |

---

## 九、常见误解澄清

### 1. 类名混淆

| ❌ 错误理解 | ✅ 正确类名 | 说明 |
|------------|------------|------|
| `ShortTermInsightExtractor` | `ShortTermInsightAnalyzer` | 不存在 Extractor 后缀的类 |
| `ShortTermManager` | `ShortTermMemoryManager` | 完整名称 |
| `LongTermManager` | `LongTermMemoryManager` | 完整名称 |

### 2. 方法位置混淆

| 方法 | 正确所属类 | 错误理解 |
|------|------------|----------|
| `get_stats()` | `ShortTermMemoryManager` | ❌ `ShortTermInsightAnalyzer` 也支持 |
| `get_stats()` | `AsynchronousExtractor` | ✅ 正确 |
| `get_stats()` | `ShortTermInsightAnalyzer` | ✅ 已添加支持 |
| `analyze()` | `ShortTermInsightAnalyzer` | ❌ 不是 `AsynchronousExtractor` 的方法 |
| `extract()` | `AsynchronousExtractor` | ❌ 不是 `ShortTermInsightAnalyzer` 的方法 |

### 3. 职责划分

```
┌─────────────────────────────────────────────────────────────┐
│                    记忆处理流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  对话输入                                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                    │
│  │PerceptionMemoryStore│  → 实时对话存储                    │
│  └─────────────────────┘                                    │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                    │
│  │ShortTermMemoryManager│ → 语义分类存储                    │
│  └─────────────────────┘                                    │
│      │                                                      │
│      ├────────────────────────────────┐                     │
│      │                                │                     │
│      ▼                                ▼                     │
│  ┌───────────────────────┐   ┌───────────────────────┐     │
│  │ShortTermInsightAnalyzer│   │AsynchronousExtractor │     │
│  │  (分析短期记忆)        │   │  (提炼到长期记忆)    │     │
│  │  analyze()            │   │  extract()           │     │
│  │  get_stats()          │   │  get_stats()         │     │
│  └───────────────────────┘   └───────────────────────┘     │
│                                      │                      │
│                                      ▼                      │
│                              ┌─────────────────────┐        │
│                              │LongTermMemoryManager│        │
│                              └─────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十、get_stats 方法汇总

所有支持 `get_stats()` 方法的类：

| 类名 | 返回类型 | 返回内容 |
|------|----------|----------|
| `ShortTermMemoryManager` | `dict[str, Any]` | total_items, items_by_bucket, active_topics |
| `ShortTermInsightAnalyzer` | `dict[str, Any]` | similarity_threshold, domain_keywords_count |
| `AsynchronousExtractor` | `dict[str, Any]` | extraction_count, last_insight_available |
| `LongTermMemoryManager` | 无此方法 | - |
| `AsyncWriter` | `WriterStats` | total_requests, successful_writes, queue_size |
| `BatchedWriter` | `BatchedWriterStats` | total_requests, merged_requests, actual_writes |
| `InsightPool` | `dict[str, Any]` | active_count, pending_count, archived_count |
| `InsightModule` | `dict[str, Any]` | 继承自 InsightPool + total_history |
| `TokenBudgetManager` | `dict[str, Any]` | total_budget, used, remaining, usage_ratio |
| `MemoryIndexer` | `IndexStats` | total_documents, total_searches, avg_latency |
| `IncrementalSync` | `SyncStats` | total_memories, pending_count, extracted_count |
| `ContextLazyLoader` | `dict[str, Any]` | size, max_size, bytes, utilization |
| `ObservabilityManager` | `ObservabilityStats` | token_usage, latency, quality_metrics |

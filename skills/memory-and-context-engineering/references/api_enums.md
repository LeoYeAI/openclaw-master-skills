# API 枚举类型参考

本文档汇总所有模块的枚举类型，供开发者查阅。

## 目录

1. [认知模型枚举](#一认知模型枚举)
2. [因果链枚举](#二因果链枚举)
3. [知识缺口枚举](#三知识缺口枚举)
4. [检索决策枚举](#四检索决策枚举)
5. [状态一致性枚举](#五状态一致性枚举)
6. [状态推理枚举](#六状态推理枚举)
7. [跨会话关联枚举](#七跨会话关联枚举)
8. [遗忘机制枚举](#八遗忘机制枚举)
9. [权限控制枚举](#九权限控制枚举)
10. [可观测性枚举](#十可观测性枚举)

---

## 一、认知模型枚举

### StepResult（步骤结果）

```python
from scripts.cognitive_model_builder import StepResult
```

| 值 | 说明 |
|------|------|
| SUCCESS | 成功 |
| FAILURE | 失败 |
| IN_PROGRESS | 进行中 |
| SKIPPED | 跳过 |
| BLOCKED | 阻塞 |

### FactSource（事实来源）

```python
from scripts.cognitive_model_builder import FactSource
```

| 值 | 说明 |
|------|------|
| MEMORY | 来自记忆 |
| RETRIEVAL | 来自检索 |
| TOOL | 来自工具返回 |
| USER | 来自用户输入 |
| INFERENCE | 来自推理 |

### ConstraintType（约束类型）

```python
from scripts.cognitive_model_builder import ConstraintType
```

| 值 | 说明 |
|------|------|
| MUST_USE | 必须使用 |
| MUST_AVOID | 禁止使用 |
| PREFERENCE | 用户偏好 |
| RESOURCE | 资源限制 |
| PERMISSION | 权限约束 |

### GapImportance（知识缺口重要程度）

```python
from scripts.cognitive_model_builder import GapImportance
```

| 值 | 说明 |
|------|------|
| CRITICAL | 关键：必须补充 |
| HIGH | 高：强烈建议补充 |
| MEDIUM | 中：建议补充 |
| LOW | 低：可选补充 |

### DecisionStatus（决策状态）

```python
from scripts.cognitive_model_builder import DecisionStatus
```

| 值 | 说明 |
|------|------|
| PENDING | 待决策 |
| MADE | 已决策 |
| REVISED | 已修订 |
| DEFERRED | 已推迟 |

---

## 二、因果链枚举

### CausalRelationType（因果关系类型）

```python
from scripts.causal_chain_extractor import CausalRelationType
```

| 值 | 说明 |
|------|------|
| DIRECT_CAUSE | 直接原因 |
| CONTRIBUTING_FACTOR | 促成因素 |
| ROOT_CAUSE | 根本原因 |
| ENABLING_CONDITION | 使能条件 |
| TRIGGER | 触发因素 |

### ProblemType（问题类型）

```python
from scripts.causal_chain_extractor import ProblemType
```

| 值 | 说明 |
|------|------|
| ERROR | 错误 |
| FAILURE | 失败 |
| ANOMALY | 异常 |
| BOTTLENECK | 瓶颈 |
| CONFLICT | 冲突 |
| GAP | 缺口 |

### SolutionStatus（解决方案状态）

```python
from scripts.causal_chain_extractor import SolutionStatus
```

| 值 | 说明 |
|------|------|
| PROPOSED | 已提出 |
| VALIDATED | 已验证 |
| IMPLEMENTED | 已实施 |
| FAILED | 失败 |

---

## 三、知识缺口枚举

### KnowledgeType（知识类型）

```python
from scripts.knowledge_gap_identifier import KnowledgeType
```

| 值 | 说明 | 建议填充策略 |
|------|------|--------------|
| FACTUAL | 事实性知识 | RETRIEVAL（检索补充） |
| PROCEDURAL | 过程性知识 | TOOL_QUERY（工具查询） |
| CONCEPTUAL | 概念性知识 | RETRIEVAL（检索补充） |
| CONTEXTUAL | 上下文知识 | INFERENCE（推理推断） |
| PREFERENTIAL | 偏好性知识 | USER_CLARIFICATION（用户澄清） |
| TEMPORAL | 时间性知识 | RETRIEVAL（检索补充） |

### GapCategory（缺口类别）

```python
from scripts.knowledge_gap_identifier import GapCategory
```

| 值 | 说明 |
|------|------|
| MISSING_INFO | 缺失信息 |
| UNCERTAINTY | 不确定性 |
| AMBIGUITY | 歧义 |
| CONFLICT | 冲突 |
| OUTDATED | 过时 |
| UNVERIFIED | 未验证 |

### FillStrategy（填充策略）

```python
from scripts.knowledge_gap_identifier import FillStrategy
```

| 值 | 说明 |
|------|------|
| RETRIEVAL | 检索补充 |
| USER_CLARIFICATION | 用户澄清 |
| TOOL_QUERY | 工具查询 |
| INFERENCE | 推理推断 |
| ASSUMPTION | 假设暂时 |

### BlockingLevel（阻塞级别）

```python
from scripts.knowledge_gap_identifier import BlockingLevel
```

| 值 | 说明 |
|------|------|
| CRITICAL | 必须立即解决 |
| HIGH | 强烈建议解决 |
| MEDIUM | 建议解决 |
| LOW | 可选解决 |
| NON_BLOCKING | 不阻塞 |

---

## 四、检索决策枚举

### RetrievalNeed（检索需求级别）

```python
from scripts.retrieval_decision_engine import RetrievalNeed
```

| 值 | 触发条件 |
|------|----------|
| REQUIRED | 知识覆盖率低、不确定性高、故障排查 |
| RECOMMENDED | 复杂查询、知识边界外 |
| OPTIONAL | 探索性查询、已有知识可能足够 |
| UNNECESSARY | 简单查询、已有知识足够 |
| CACHED | 缓存命中 |

### QueryType（查询类型）

```python
from scripts.retrieval_decision_engine import QueryType
```

| 值 | 说明 | 推荐策略 |
|------|------|----------|
| FACTUAL | 事实查询 | HYBRID |
| PROCEDURAL | 过程查询 | KEYWORD_ONLY |
| CONCEPTUAL | 概念查询 | VECTOR_ONLY |
| TROUBLESHOOTING | 故障排查 | HYBRID |
| EXPLORATORY | 探索性查询 | MULTI_PATH |

### RetrievalStrategy（检索策略）

```python
from scripts.retrieval_decision_engine import RetrievalStrategy
```

| 值 | 说明 |
|------|------|
| VECTOR_ONLY | 仅向量检索 |
| KEYWORD_ONLY | 仅关键词检索 |
| HYBRID | 混合检索 |
| SEMANTIC_BUCKET | 语义桶检索 |
| MULTI_PATH | 多路召回 |

### CacheDecision（缓存决策）

```python
from scripts.retrieval_decision_engine import CacheDecision
```

| 值 | 说明 |
|------|------|
| USE_CACHE | 使用缓存 |
| PARTIAL_CACHE | 部分使用缓存 |
| FRESH_RETRIEVAL | 全新检索 |

---

## 五、检索质量枚举

### QualityDimension（质量维度）

```python
from scripts.retrieval_quality_evaluator import QualityDimension
```

| 值 | 权重 | 说明 |
|------|------|------|
| RELEVANCE | 30% | 相关性 |
| COMPLETENESS | 20% | 完整性 |
| FRESHNESS | 15% | 新鲜度 |
| DIVERSITY | 15% | 多样性 |
| COHERENCE | 10% | 连贯性 |
| CREDIBILITY | 10% | 可信度 |

### QualityLevel（质量级别）

```python
from scripts.retrieval_quality_evaluator import QualityLevel
```

| 值 | 评分范围 |
|------|----------|
| EXCELLENT | >= 0.85 |
| GOOD | >= 0.70 |
| ACCEPTABLE | >= 0.50 |
| POOR | >= 0.30 |
| UNACCEPTABLE | < 0.30 |

### ReretrievalNeed（二次检索需求）

```python
from scripts.retrieval_quality_evaluator import ReretrievalNeed
```

| 值 | 说明 |
|------|------|
| NOT_NEEDED | 不需要 |
| RECOMMENDED | 建议 |
| REQUIRED | 需要 |
| URGENT | 紧急 |

---

## 六、状态一致性枚举

### ConsistencyLevel（一致性级别）

```python
from scripts.state_consistency_validator import ConsistencyLevel
```

| 值 | 说明 |
|------|------|
| FULLY_CONSISTENT | 完全一致 |
| MOSTLY_CONSISTENT | 基本一致 |
| PARTIALLY_CONSISTENT | 部分一致 |
| INCONSISTENT | 不一致 |
| SEVERELY_INCONSISTENT | 严重不一致 |

### ConflictSeverity（冲突严重程度）

```python
from scripts.types import ConflictSeverity
```

| 值 | 说明 |
|------|------|
| CRITICAL | 严重：需要立即解决 |
| HIGH | 高：需要尽快解决 |
| MEDIUM | 中：建议解决 |
| LOW | 低：可忽略 |

### ResolutionStrategy（解决策略）

```python
from scripts.state_consistency_validator import ResolutionStrategy
```

| 值 | 说明 |
|------|------|
| AUTO_FIX | 自动修复 |
| LATEST_WINS | 最新优先 |
| PRIORITY_WINS | 优先级优先 |
| USER_DECISION | 用户决策 |
| MANUAL_FIX | 手动修复 |

### StateModule（状态模块）

```python
from scripts.state_consistency_validator import StateModule
```

| 值 | 说明 |
|------|------|
| TASK_PROGRESS | 任务进度状态 |
| SHORT_TERM_MEMORY | 短期记忆状态 |
| LONG_TERM_MEMORY | 长期记忆状态 |
| CONTEXT_ORCHESTRATOR | 上下文编排器状态 |
| GLOBAL_STATE | 全局状态 |

---

## 七、状态推理枚举

### InferenceType（推理类型）

```python
from scripts.state_inference_engine import InferenceType
```

| 值 | 说明 |
|------|------|
| DEDUCTIVE | 演绎推理（从一般到特殊） |
| INDUCTIVE | 归纳推理（从特殊到一般） |
| ABDUCTIVE | 溯因推理（最佳解释） |
| ANALOGICAL | 类比推理（相似情况） |

### InferenceConfidence（推理置信度）

```python
from scripts.state_inference_engine import InferenceConfidence
```

| 值 | 置信度范围 |
|------|------------|
| CERTAIN | >= 0.9 |
| HIGH | >= 0.7 |
| MEDIUM | >= 0.5 |
| LOW | >= 0.3 |
| UNCERTAIN | < 0.3 |

### InferenceSource（推理来源）

```python
from scripts.state_inference_engine import InferenceSource
```

| 值 | 说明 |
|------|------|
| PATTERN | 模式匹配 |
| RULE | 规则推导 |
| HEURISTIC | 启发式 |
| TEMPORAL | 时序推断 |
| CONTEXTUAL | 上下文推断 |

---

## 八、跨会话关联枚举

### LinkStrength（关联强度）

```python
from scripts.cross_session_memory_linker import LinkStrength
```

| 值 | 说明 |
|------|------|
| STRONG | 强关联：同一任务、直接引用 |
| MEDIUM | 中关联：相同主题、相似上下文 |
| WEAK | 弱关联：共享实体、间接关联 |

### LinkType（关联类型）

```python
from scripts.cross_session_memory_linker import LinkType
```

| 值 | 说明 |
|------|------|
| SAME_TASK | 同一任务 |
| SAME_TOPIC | 同一主题 |
| SAME_ENTITY | 同一实体 |
| CONTINUATION | 延续关系 |
| REFERENCE | 引用关系 |
| CONTRADICTION | 矛盾关系 |
| COMPLEMENT | 互补关系 |

### SessionStatus（会话状态）

```python
from scripts.cross_session_memory_linker import SessionStatus
```

| 值 | 说明 |
|------|------|
| ACTIVE | 活跃 |
| PAUSED | 暂停 |
| COMPLETED | 完成 |
| ARCHIVED | 归档 |

---

## 九、遗忘机制枚举

### MemoryImportance（记忆重要性）

```python
from scripts.memory_forgetting_mechanism import MemoryImportance
```

| 值 | 说明 | 遗忘策略 |
|------|------|----------|
| CRITICAL | 关键：永不遗忘 | 保护 |
| HIGH | 高：长期保留 | 延迟遗忘 |
| MEDIUM | 中：中期保留 | 正常遗忘 |
| LOW | 低：短期保留 | 快速遗忘 |
| TRIVIAL | 琐碎：快速遗忘 | 优先遗忘 |

### ForgettingTrigger（遗忘触发因素）

```python
from scripts.memory_forgetting_mechanism import ForgettingTrigger
```

| 值 | 说明 |
|------|------|
| TIME_DECAY | 时间衰减 |
| LOW_ACCESS | 低访问频率 |
| REDUNDANCY | 冗余 |
| IRRELEVANCE | 不相关 |
| CONFLICT | 冲突 |
| EXPLICIT | 显式标记 |

### ForgettingAction（遗忘动作）

```python
from scripts.memory_forgetting_mechanism import ForgettingAction
```

| 值 | 说明 |
|------|------|
| ARCHIVE | 归档：移至冷存储 |
| DEPRIORITIZE | 降权：降低访问优先级 |
| MERGE | 合并：与相似记忆合并 |
| DELETE | 删除：完全移除 |
| KEEP | 保留：不做处理 |

### MemoryState（记忆状态）

```python
from scripts.memory_forgetting_mechanism import MemoryState
```

| 值 | 说明 |
|------|------|
| ACTIVE | 活跃 |
| DORMANT | 休眠 |
| ARCHIVED | 已归档 |
| DELETED | 已删除 |

---

## 十、权限控制枚举

### AccessAction（访问动作）

```python
from scripts.permission_boundary_controller import AccessAction
```

| 值 | 说明 |
|------|------|
| READ | 读取 |
| WRITE | 写入 |
| DELETE | 删除 |
| SHARE | 分享 |
| EXPORT | 导出 |

### DataCategory（数据类别）

```python
from scripts.permission_boundary_controller import DataCategory
```

| 值 | 说明 |
|------|------|
| USER_PROFILE | 用户资料 |
| MEMORY_DATA | 记忆数据 |
| PREFERENCE_DATA | 偏好数据 |
| BEHAVIOR_DATA | 行为数据 |
| SENSITIVE_DATA | 敏感数据 |

### PermissionLevel（权限级别）

```python
from scripts.permission_boundary_controller import PermissionLevel
```

| 值 | 说明 |
|------|------|
| PUBLIC | 公开 |
| INTERNAL | 内部 |
| CONFIDENTIAL | 机密 |
| RESTRICTED | 限制 |

---

## 十一、可观测性枚举

### AlertLevel（告警级别）

```python
from scripts.observability_manager import AlertLevel
```

| 值 | 说明 |
|------|------|
| INFO | 信息 |
| WARNING | 警告 |
| ERROR | 错误 |
| CRITICAL | 严重 |

### MetricType（指标类型）

```python
from scripts.observability_manager import MetricType
```

| 值 | 说明 |
|------|------|
| COUNTER | 计数器 |
| GAUGE | 仪表 |
| HISTOGRAM | 直方图 |
| SUMMARY | 摘要 |

---

## 相关文档

- [architecture_overview.md](architecture_overview.md) - 全局架构总览
- [memory_types.md](memory_types.md) - 记忆类型详解

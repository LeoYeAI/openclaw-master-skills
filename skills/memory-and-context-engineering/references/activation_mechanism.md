# 六维激活器机制

## 目录

1. [概述](#概述)
2. [激活器详解](#激活器详解)
3. [激活算法](#激活算法)
4. [区间管理](#区间管理)
5. [上下文重构](#上下文重构)
6. [最佳实践](#最佳实践)

---

## 概述

非线性记忆激活是 Agent Memory System 的核心创新，通过六个维度的触发器并行激活相关记忆，实现从"信息检索"到"智能关联"的跃迁。

### 六维激活器

| 维度 | 英文 | 作用 | 权重 |
|------|------|------|------|
| 时间 | Temporal | 激活近期相关记忆 | 0.20 |
| 语义 | Semantic | 激活概念相关记忆 | 0.25 |
| 情境 | Contextual | 激活相似场景记忆 | 0.20 |
| 情感 | Emotional | 激活情感共鸣记忆 | 0.10 |
| 因果 | Causal | 激活因果链相关经验 | 0.15 |
| 身份 | Identity | 激活身份关联成长记忆 | 0.10 |

---

## 激活器详解

### 1. 时间激活器（Temporal Activator）

#### 原理
基于时间窗口激活近期相关记忆，遵循"近因效应"。

#### 时间窗口定义

| 窗口 | 时间范围 | 权重 |
|------|----------|------|
| 立即 | 0-1 小时 | 1.00 |
| 近期 | 1-24 小时 | 0.85 |
| 本周 | 1-7 天 | 0.70 |
| 本月 | 7-30 天 | 0.55 |
| 归档 | > 30 天 | 0.35 |

#### 激活公式

```python
def temporal_activation_score(
    hours_since_access: float,
    base_importance: float = 1.0
) -> float:
    """
    计算时间激活分数
    
    Args:
        hours_since_access: 距上次访问的小时数
        base_importance: 基础重要性
    
    Returns:
        激活分数 (0.0-1.0)
    """
    # 指数衰减
    decay_factor = 0.95
    recency_score = 100 * (decay_factor ** hours_since_access)
    
    # 窗口权重
    window_weights = {
        (0, 1): 1.0,
        (1, 24): 0.85,
        (24, 168): 0.70,
        (168, 720): 0.55,
    }
    
    for (low, high), weight in window_weights.items():
        if low <= hours_since_access < high:
            return min(1.0, recency_score / 100 * weight * base_importance)
    
    return 0.35 * base_importance
```

---

### 2. 语义激活器（Semantic Activator）

#### 原理
基于概念关联激活语义相关记忆，使用关键词匹配和同义词扩展。

#### 匹配类型与权重

| 匹配类型 | 说明 | 权重 |
|----------|------|------|
| 直接匹配 | 完全相同的概念 | 1.00 |
| 同义词匹配 | 语义相近的词 | 0.85 |
| 下位词匹配 | 更具体的概念 | 0.75 |
| 上位词匹配 | 更抽象的概念 | 0.70 |
| 因果关联 | 有因果关系的概念 | 0.65 |

#### 激活算法

```python
def semantic_activation_score(
    query_concepts: list[str],
    memory_concepts: list[str],
    concept_relations: dict[str, list[str]]
) -> float:
    """
    计算语义激活分数
    
    Args:
        query_concepts: 查询中的概念
        memory_concepts: 记忆中的概念
        concept_relations: 概念关系图
    
    Returns:
        激活分数 (0.0-1.0)
    """
    total_score = 0.0
    matched_count = 0
    
    for q_concept in query_concepts:
        for m_concept in memory_concepts:
            # 直接匹配
            if q_concept.lower() == m_concept.lower():
                total_score += 1.0
                matched_count += 1
                continue
            
            # 同义词匹配
            if m_concept in concept_relations.get(q_concept, []):
                total_score += 0.85
                matched_count += 1
                continue
            
            # 部分匹配
            if q_concept.lower() in m_concept.lower() or m_concept.lower() in q_concept.lower():
                total_score += 0.60
                matched_count += 1
    
    return min(1.0, total_score / max(len(query_concepts), 1))
```

---

### 3. 情境激活器（Contextual Activator）

#### 原理
基于任务情境激活相似场景记忆，匹配问题类型和解决策略。

#### 情境匹配维度

- 任务类型（TaskType）
- 任务复杂度
- 任务阶段
- 隐式需求

#### 激活流程

```python
def contextual_activation_score(
    current_situation: SituationAwareness,
    memory_strategies: list[StrategyRecord]
) -> float:
    """
    计算情境激活分数
    
    Args:
        current_situation: 当前情境
        memory_strategies: 记忆中的策略
    
    Returns:
        激活分数 (0.0-1.0)
    """
    task_type = current_situation.current_task.task_type.value
    
    for strategy in memory_strategies:
        if strategy.problem_type.lower() in task_type.lower():
            # 匹配成功，返回成功率作为激活分数
            return strategy.success_rate
    
    return 0.0
```

---

### 4. 情感激活器（Emotional Activator）

#### 原理
基于情感共鸣激活相似情感记忆，用于情感化响应。

#### 情感类型映射

```python
EMOTION_TYPE_MAP = {
    "positive": ["积极", "满意", "开心", "兴奋"],
    "negative": ["焦虑", "沮丧", "不满", "愤怒"],
    "neutral": ["中性", "平静", "专注"],
    "mixed": ["矛盾", "纠结", "复杂"],
}
```

#### 激活算法

```python
def emotional_activation_score(
    current_emotion: str,
    emotional_memories: list[EmotionState]
) -> float:
    """
    计算情感激活分数
    
    Args:
        current_emotion: 当前情感
        emotional_memories: 情感记忆列表
    
    Returns:
        激活分数 (0.0-1.0)
    """
    if not emotional_memories:
        return 0.0
    
    # 取最近5条情感记忆
    recent_emotions = emotional_memories[-5:]
    
    for state in recent_emotions:
        if state.emotion_type in current_emotion or current_emotion in state.emotion_type:
            # 情感匹配，返回强度作为激活分数
            return state.intensity * 0.7
    
    return 0.0
```

---

### 5. 因果激活器（Causal Activator）

#### 原理
基于因果链激活相关经验，识别"因为...所以..."模式。

#### 因果模式识别

```python
CAUSAL_PATTERNS = [
    "因为...所以...",
    "由于...导致...",
    "...的原因是...",
    "...结果是...",
]
```

#### 激活逻辑

```python
def causal_activation_score(
    current_context: str,
    procedural_memory: ProceduralMemoryData
) -> float:
    """
    计算因果激活分数
    
    Args:
        current_context: 当前上下文
        procedural_memory: 程序性记忆
    
    Returns:
        激活分数 (0.0-1.0)
    """
    # 检查决策模式的成功/失败率
    if procedural_memory.decision_patterns:
        avg_success = sum(
            p.success_rate for p in procedural_memory.decision_patterns
        ) / len(procedural_memory.decision_patterns)
        return avg_success
    
    return 0.0
```

---

### 6. 身份激活器（Identity Activator）

#### 原理
基于身份关联激活相关成长记忆，追踪身份演化。

#### 身份匹配逻辑

```python
def identity_activation_score(
    current_task: str,
    user_profile: UserProfileData,
    narrative_memory: NarrativeMemoryData
) -> float:
    """
    计算身份激活分数
    
    Args:
        current_task: 当前任务
        user_profile: 用户画像
        narrative_memory: 叙事记忆
    
    Returns:
        激活分数 (0.0-1.0)
    """
    # 检查身份标签与当前任务的关联
    for identity in user_profile.identity:
        if identity.lower() in current_task.lower():
            return 0.8
    
    # 检查成长节点相关性
    for milestone in narrative_memory.growth_milestones[-3:]:
        if any(
            skill.lower() in current_task.lower()
            for skill in milestone.related_skills
        ):
            return 0.6
    
    return 0.0
```

---

## 激活算法

### 并行激活流程

```
当前情境
    ↓
┌─────────────────────────────────────────────┐
│         六维激活器并行执行                    │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │
│  │时间 │ │语义 │ │情境 │ │情感 │ │因果 │ │身份 │ │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ │
│     │       │       │       │       │       │    │
│     └───────┴───────┴───────┴───────┴───────┘    │
│                     ↓                          │
│              激活来源聚合                       │
└─────────────────────────────────────────────┘
    ↓
记忆激活记录（ActivatedMemory）
```

### 综合激活分数计算

```python
def calculate_comprehensive_score(
    activation_sources: list[ActivationSource],
    weights: dict[TriggerDimension, float]
) -> float:
    """
    计算综合激活分数
    
    Args:
        activation_sources: 激活来源列表
        weights: 维度权重
    
    Returns:
        综合激活分数 (0.0-1.0)
    """
    total_score = 0.0
    total_weight = 0.0
    
    for source in activation_sources:
        dim_weight = weights.get(source.dimension, 0.1)
        total_score += source.score * dim_weight
        total_weight += dim_weight
    
    return total_score / max(total_weight, 0.01)
```

---

## 区间管理

### 激活区间定义

| 区间 | 分数范围 | 描述 |
|------|----------|------|
| 高激活区 | 0.8 - 1.0 | 强相关，优先使用 |
| 中激活区 | 0.5 - 0.8 | 中等相关，候选使用 |
| 低激活区 | 0.2 - 0.5 | 弱相关，按需使用 |
| 抑制区 | 0.0 - 0.2 | 不相关，抑制激活 |

### 区间策略

```python
def apply_interval_policy(
    activated_memories: list[ActivatedMemory],
    max_high: int = 5,
    max_medium: int = 10
) -> list[ActivatedMemory]:
    """
    应用区间策略
    
    Args:
        activated_memories: 激活的记忆列表
        max_high: 高激活区最大数量
        max_medium: 中激活区最大数量
    
    Returns:
        筛选后的记忆列表
    """
    high = [m for m in activated_memories if m.relevance_score >= 0.8]
    medium = [m for m in activated_memories if 0.5 <= m.relevance_score < 0.8]
    low = [m for m in activated_memories if m.relevance_score < 0.5]
    
    # 限制数量
    high = sorted(high, key=lambda x: x.relevance_score, reverse=True)[:max_high]
    medium = sorted(medium, key=lambda x: x.relevance_score, reverse=True)[:max_medium]
    low = sorted(low, key=lambda x: x.relevance_score, reverse=True)[:5]
    
    return high + medium + low
```

---

## 上下文重构

### 重构目标

将激活的记忆重构为结构化的上下文，供模型决策使用。

### 重构层次

```
ReconstructedContext
├── task_context          # 任务上下文层
├── user_state            # 用户状态层
├── activated_experiences # 激活经验层
├── knowledge_context     # 知识上下文层
├── emotional_context     # 情感上下文层
└── narrative_anchor      # 叙事锚点层
```

### 重构流程

```python
def reconstruct_context(
    activated_memories: list[ActivatedMemory]
) -> ReconstructedContext:
    """
    重构上下文
    
    Args:
        activated_memories: 激活的记忆列表
    
    Returns:
        重构后的上下文
    """
    # 1. 构建任务上下文层
    task_context = build_task_context(activated_memories)
    
    # 2. 构建用户状态层
    user_state = build_user_state(activated_memories)
    
    # 3. 构建激活经验层
    experiences = build_experiences(activated_memories)
    
    # 4. 构建知识上下文层
    knowledge = build_knowledge(activated_memories)
    
    # 5. 构建情感上下文层
    emotional = build_emotional(activated_memories)
    
    # 6. 构建叙事锚点层
    narrative = build_narrative(activated_memories)
    
    return ReconstructedContext(
        task_context=task_context,
        user_state=user_state,
        activated_experiences=experiences,
        knowledge_context=knowledge,
        emotional_context=emotional,
        narrative_anchor=narrative,
    )
```

---

## 最佳实践

### 1. 激活阈值调整

根据任务类型调整激活阈值：

| 任务类型 | 推荐阈值 | 原因 |
|----------|----------|------|
| 技术实现 | 0.6 | 需要精确匹配 |
| 创意设计 | 0.4 | 需要广泛联想 |
| 问题诊断 | 0.7 | 需要高相关性 |
| 头脑风暴 | 0.3 | 需要最大发散 |

### 2. 维度权重调优

根据用户偏好调整维度权重：

```python
# 逻辑型用户
LOGICAL_WEIGHTS = {
    TriggerDimension.TEMPORAL: 0.15,
    TriggerDimension.SEMANTIC: 0.30,
    TriggerDimension.CONTEXTUAL: 0.25,
    TriggerDimension.EMOTIONAL: 0.05,
    TriggerDimension.CAUSAL: 0.20,
    TriggerDimension.IDENTITY: 0.05,
}

# 创意型用户
CREATIVE_WEIGHTS = {
    TriggerDimension.TEMPORAL: 0.10,
    TriggerDimension.SEMANTIC: 0.20,
    TriggerDimension.CONTEXTUAL: 0.15,
    TriggerDimension.EMOTIONAL: 0.20,
    TriggerDimension.CAUSAL: 0.15,
    TriggerDimension.IDENTITY: 0.20,
}
```

### 3. 性能优化

- **并行激活**：六个维度并行计算
- **缓存热记忆**：热记忆常驻内存
- **惰性加载**：冷记忆按需加载
- **批量处理**：批量计算激活分数

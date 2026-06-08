# 记忆类型详解

## 目录

1. [记忆分类体系](#记忆分类体系)
2. [短期记忆到长期记忆映射](#短期记忆到长期记忆映射)
3. [用户画像](#用户画像)
4. [程序性记忆](#程序性记忆)
5. [叙事记忆](#叙事记忆)
6. [语义记忆](#语义记忆)
7. [情感记忆](#情感记忆)

---

## 记忆分类体系

### 7种长期记忆分类

```
┌─────────────────────────────────────────────────────────────┐
│                    长期记忆7分类体系                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【核心层】持久化，跨会话稳定                                │
│  ├── CORE_IDENTITY     核心身份 → UserProfile.identity      │
│  ├── CORE_PREFERENCE   核心偏好 → UserProfile.preferences   │
│  └── CORE_SKILL        核心技能 → ProceduralMemory          │
│                                                             │
│  【扩展层】动态更新，跨会话积累                              │
│  ├── EXTENDED_BEHAVIOR 扩展行为 → ProceduralMemory          │
│  ├── EXTENDED_EMOTION  扩展情感 → EmotionalMemory           │
│  ├── EXTENDED_KNOWLEDGE 扩展知识 → SemanticMemory           │
│  └── EXTENDED_NARRATIVE 扩展叙事 → NarrativeMemory          │
│                                                             │
│  注意：上下文（Context）是动态的、会话级别的，              │
│        由短期记忆和上下文重构器管理，不属于长期记忆。        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5种短期记忆语义桶

```
┌─────────────────────────────────────────────────────────────┐
│                    短期记忆5种语义桶                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TASK_CONTEXT      任务上下文桶（优先级 0.90）              │
│  USER_INTENT       用户意图桶（优先级 0.85）                │
│  DECISION_CONTEXT  决策上下文桶（优先级 0.80）              │
│  KNOWLEDGE_GAP     知识缺口桶（优先级 0.70）                │
│  EMOTIONAL_TRACE   情感痕迹桶（优先级 0.60）                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 短期记忆到长期记忆映射

### 核心设计理念

```
┌─────────────────────────────────────────────────────────────┐
│              短期记忆提炼的核心区分                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【持久化内容】→ 长期记忆                                    │
│  ├── 用户意图 → 核心偏好/身份                               │
│  ├── 知识缺口 → 扩展知识                                    │
│  └── 情感痕迹 → 扩展情感                                    │
│                                                             │
│  【动态上下文】→ 上下文重构器（非线性激活）                  │
│  ├── 决策上下文 → 六维激活                                  │
│  └── 任务上下文 → 扩展叙事 + 六维激活                       │
│                                                             │
│  关键区别：                                                  │
│  - 决策上下文是"当前会话的决策情境"                         │
│  - 它是动态的、情境化的                                     │
│  - 不应固化到长期记忆，而是用于激活相关记忆                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 完整映射表

```
┌─────────────────────────────────────────────────────────────┐
│          短期记忆语义桶 → 目标 映射                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  USER_INTENT (用户意图)                                      │
│  ├── 首选 → CORE_PREFERENCE (核心偏好)                      │
│  └── 备选 → CORE_IDENTITY (核心身份)                        │
│      → 存储到长期记忆                                       │
│                                                             │
│  DECISION_CONTEXT (决策上下文)                               │
│  └── 唯选 → CONTEXT_ACTIVATION (上下文激活)                 │
│      → 传递给上下文重构器，进行六维激活                     │
│      → 不存储到长期记忆                                     │
│                                                             │
│  TASK_CONTEXT (任务上下文)                                   │
│  ├── 主选 → EXTENDED_NARRATIVE (扩展叙事)                   │
│  └── 同时 → CONTEXT_ACTIVATION                              │
│      → 存储到长期叙事 + 传递给上下文重构器                  │
│                                                             │
│  KNOWLEDGE_GAP (知识缺口)                                    │
│  └── 唯选 → EXTENDED_KNOWLEDGE (扩展知识)                   │
│      → 存储到长期记忆                                       │
│                                                             │
│  EMOTIONAL_TRACE (情感痕迹)                                  │
│  └── 唯选 → EXTENDED_EMOTION (扩展情感)                     │
│      → 存储到长期记忆                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 映射规则说明

| 短期桶 | 目标 | 处理方式 | 说明 |
|--------|------|----------|------|
| USER_INTENT | CORE_PREFERENCE | 长期存储 | 用户偏好应持久化 |
| USER_INTENT | CORE_IDENTITY | 长期存储 | 涉及身份认同时 |
| DECISION_CONTEXT | CONTEXT_ACTIVATION | **不存储** | 传递给上下文重构器 |
| TASK_CONTEXT | EXTENDED_NARRATIVE | 长期存储 + 激活 | 双重用途 |
| KNOWLEDGE_GAP | EXTENDED_KNOWLEDGE | 长期存储 | 知识应持久化 |
| EMOTIONAL_TRACE | EXTENDED_EMOTION | 长期存储 | 情感应持久化 |

### 为什么决策上下文不存长期记忆？

```
场景示例：
用户说："我选择用 PostgreSQL"

【错误做法】直接存储
→ 长期记忆中出现大量"选择X"的碎片
→ 没有上下文，无法理解为什么选择

【正确做法】传递给上下文重构器
→ 激活相关记忆：电商系统项目、数据库需求
→ 结合当前情境理解决策
→ 形成有意义的上下文包
→ 决策结果体现在叙事记忆中（任务完成时）
```

### 使用映射工具

```python
from scripts.types import ExtractionMapping, SemanticBucketType, MemoryCategory

# 获取目标分类
category = ExtractionMapping.get_target_category(
    bucket_type=SemanticBucketType.DECISION_CONTEXT,
    confidence=0.8,  # 高置信度
)
# 返回: MemoryCategory.CORE_SKILL

# 判断分类层级
if ExtractionMapping.is_core_category(category):
    print("核心层记忆，跨会话稳定")
else:
    print("扩展层记忆，动态更新")
```

---

## 用户画像

### 定义
用户画像是关于用户身份、背景、偏好和决策模式的长期记忆，用于个性化交互。

### 数据结构

```python
class UserProfileData:
    identity: list[str]           # 身份标签 ["开发者", "架构师"]
    technical_background: TechnicalBackground  # 技术背景
    communication_style: CommunicationStyle    # 沟通风格
    decision_pattern: DecisionPattern          # 决策模式
    version: int                  # 版本号（用于增量更新）
```

### 核心字段说明

#### TechnicalBackground（技术背景）
```python
class TechnicalBackground:
    domains: list[str]            # 领域 ["后端开发", "分布式系统"]
    expertise_level: str          # 水平 "beginner" | "intermediate" | "advanced"
    stack: list[str]              # 技术栈 ["Python", "Kubernetes"]
    learning_goals: list[str]     # 学习目标
```

#### CommunicationStyle（沟通风格）
```python
class CommunicationStyle:
    style: str                    # "直接" | "详细" | "引导式"
    preference: str               # 偏好 "逻辑清晰" | "简洁易懂"
    dislike: list[str]            # 不喜欢 ["长篇大论", "抽象概念"]
    response_length: str          # "简短" | "适中" | "详细"
```

#### DecisionPattern（决策模式）
```python
class DecisionPattern:
    type: str                     # "审慎型" | "果断型" | "平衡型"
    requires: str                 # 需求 "充分证据" | "快速反馈"
    focus: str                    # 关注点 "架构优先" | "效率优先" | "质量优先"
    risk_tolerance: str           # "低" | "中" | "高"
```

### 使用场景
- 首次识别用户身份
- 调整沟通策略
- 决策风格适配
- 知识推送个性化

### 更新策略
- 初始构建：从首次对话中提取
- 增量更新：从每次交互中学习
- 定期校准：每 N 次交互后评估一致性

---

## 程序性记忆

### 定义
程序性记忆存储用户的问题解决策略、决策模式、工具使用习惯等"如何做"的知识。

### 数据结构

```python
class ProceduralMemoryData:
    decision_patterns: list[DecisionPatternRecord]     # 决策模式记录
    problem_solving_strategies: list[StrategyRecord]   # 问题解决策略
    tool_effectiveness_records: list[ToolUsageRecord]  # 工具使用记录
    tool_combination_patterns: list[ToolCombination]   # 工具组合模式
    operation_preferences: dict[str, Any]              # 操作偏好
    neuroticism_tendency: NeuroticismTendency          # 神经质倾向
```

### 核心组件

#### DecisionPatternRecord（决策模式记录）
```python
class DecisionPatternRecord:
    pattern_id: str               # 模式ID
    trigger_condition: str        # 触发条件 "技术讨论"
    workflow: list[str]           # 工作流 ["概念讨论", "设计", "实现"]
    confidence: float             # 置信度 0.0-1.0
    usage_count: int              # 使用次数
    success_rate: float           # 成功率 0.0-1.0
```

#### StrategyRecord（问题解决策略）
```python
class StrategyRecord:
    strategy_id: str              # 策略ID
    problem_type: str             # 问题类型 "代码调试"
    approach: list[str]           # 方法 ["复现", "定位", "修复"]
    success_rate: float           # 成功率
    applicability: list[str]      # 适用场景
```

#### ToolUsageRecord（工具使用记录）
```python
class ToolUsageRecord:
    record_id: str                # 记录ID
    timestamp: datetime           # 时间戳
    task_type: str                # 任务类型
    tool_name: str                # 工具名称
    effectiveness_score: float    # 有效度分数 0.0-1.0
    outcome: str                  # 结果 "success" | "failure"
    user_feedback: float | None   # 用户反馈 1.0-5.0
```

#### NeuroticismTendency（神经质倾向）
```python
class NeuroticismTendency:
    score: float                  # 分数 -1.0 到 1.0
    triggers: list[str]           # 触发因素
    adjustments: list[float]      # 历史调整记录
    derived_from: list[str]       # 数据来源
```

### 神经质倾向计算

神经质倾向用于在冲突解决时调整权重分配：

```python
def calculate_neuroticism_adjustment(
    base_logical_weight: float,
    neuroticism_score: float
) -> float:
    """
    根据神经质分数调整逻辑权重
    
    Args:
        base_logical_weight: 基础逻辑权重 (0.0-1.0)
        neuroticism_score: 神经质分数 (-1.0 到 1.0)
    
    Returns:
        调整后的逻辑权重
    """
    # 正值表示更神经质，降低逻辑权重
    # 负值表示更理性，提高逻辑权重
    adjustment = -neuroticism_score * 0.1
    return max(0.1, min(0.9, base_logical_weight + adjustment))
```

### 使用场景
- 推荐问题解决策略
- 工具选择建议
- 决策风格匹配
- 冲突解决权重调整

---

## 叙事记忆

### 定义
叙事记忆存储用户的成长历程、身份演化和持续关注点，形成连贯的自我叙事。

### 数据结构

```python
class NarrativeMemoryData:
    growth_milestones: list[GrowthMilestone]  # 成长节点
    current_identity: list[str]               # 当前身份
    identity_evolution: list[IdentityShift]   # 身份演化轨迹
    continuous_concerns: list[str]            # 持续关注点
    recurring_questions: list[str]            # 反复提出的问题
```

### 核心组件

#### GrowthMilestone（成长节点）
```python
class GrowthMilestone:
    timestamp: datetime           # 时间戳
    event: str                    # 事件 "完成架构设计"
    significance: str             # 意义 "掌握了分布式系统设计"
    importance_score: float       # 重要性分数 0.0-1.0
    related_skills: list[str]     # 相关技能
```

#### IdentityShift（身份演化）
```python
class IdentityShift:
    from_identity: str            # 原身份 "初级开发者"
    to_identity: str              # 新身份 "技术负责人"
    trigger: str                  # 触发事件
    confidence: float             # 置信度
```

### 使用场景
- 身份识别与演化追踪
- 成长路径规划
- 长期目标对齐
- 里程碑提醒

---

## 语义记忆

### 定义
语义记忆存储核心概念、知识实体和原则，是用户的"知识库"。

### 数据结构

```python
class SemanticMemoryData:
    core_concepts: list[ConceptDefinition]    # 核心概念
    knowledge_entities: list[KnowledgeEntity] # 知识实体
    principles: list[Principle]               # 原则
    concept_relations: list[ConceptRelation] # 概念关系
```

### 核心组件

#### ConceptDefinition（概念定义）
```python
class ConceptDefinition:
    concept: str                  # 概念 "微服务"
    definition: str               # 定义
    attributes: dict[str, Any]    # 属性 {"优点": "...", "缺点": "..."}
    related_concepts: list[str]   # 相关概念 ["单体架构", "服务网格"]
    usage_count: int              # 使用次数
    confidence: float             # 置信度
```

#### KnowledgeEntity（知识实体）
```python
class KnowledgeEntity:
    entity_id: str                # 实体ID
    entity_type: str              # 类型 "技术" | "概念" | "工具"
    name: str                     # 名称
    properties: dict[str, Any]    # 属性
    source: str                   # 来源
    last_accessed: datetime       # 最后访问时间
```

### 使用场景
- 概念解释
- 知识检索
- 概念关联分析
- 知识缺口检测

---

## 情感记忆

### 定义
情感记忆存储用户的情绪状态、态度倾向和满意度记录，用于情感化交互。

### 数据结构

```python
class EmotionalMemoryData:
    emotion_states: list[EmotionState]        # 情绪状态历史
    attitude_tendencies: list[AttitudeRecord] # 态度倾向
    satisfaction_records: list[SatisfactionRecord] # 满意度记录
    emotional_triggers: list[str]             # 情感触发因素
```

### 核心组件

#### EmotionState（情绪状态）
```python
class EmotionState:
    timestamp: datetime           # 时间戳
    emotion_type: str             # 情绪类型 "positive" | "negative" | "neutral"
    intensity: float              # 强度 0.0-1.0
    trigger_context: str          # 触发上下文
    topic: str                    # 相关主题
    decay_factor: float           # 衰减因子
```

### 情感衰减模型

情绪强度随时间衰减：

```python
def calculate_emotion_intensity(
    initial_intensity: float,
    days_elapsed: float,
    decay_factor: float = 0.98
) -> float:
    """
    计算衰减后的情绪强度
    
    Args:
        initial_intensity: 初始强度
        days_elapsed: 经过天数
        decay_factor: 衰减因子
    
    Returns:
        衰减后的强度
    """
    return initial_intensity * (decay_factor ** days_elapsed)
```

### 使用场景
- 情感化响应
- 用户满意度追踪
- 情绪周期分析
- 个性化语气调整

---

## 记忆协同机制

### 感知 → 长期提炼流程

```
感知记忆（临时）
    ↓
短期记忆提炼
    ├── 用户画像更新
    ├── 程序性记忆更新
    ├── 叙事记忆更新
    ├── 语义记忆更新
    └── 情感记忆更新
    ↓
长期记忆（持久化）
```

### 记忆权重计算

不同记忆类型在决策中的权重：

| 记忆类型 | 默认权重 | 调整因素 |
|----------|----------|----------|
| 用户画像 | 0.25 | 身份匹配度 |
| 程序性记忆 | 0.30 | 策略成功率 |
| 叙事记忆 | 0.15 | 节点相关性 |
| 语义记忆 | 0.20 | 概念关联度 |
| 情感记忆 | 0.10 | 情绪强度 |

---

## 最佳实践

### 1. 记忆更新时机
- **即时更新**：用户明确表达偏好时
- **延迟更新**：模式需要多次验证时
- **异步更新**：复杂计算（如神经质分数）时

### 2. 记忆查询优化
- 热记忆优先：从内存 LRU 中查找
- 相关性排序：按激活分数排序
- 去重合并：合并相同来源的记忆

### 3. 隐私保护
- 敏感数据加密存储
- 提供用户控制接口
- 支持记忆删除请求

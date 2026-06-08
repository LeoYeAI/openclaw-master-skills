# 洞察模块设计原理

## 目录

1. [概述](#概述)
2. [洞察类型](#洞察类型)
3. [信号生成机制](#信号生成机制)
4. [契合度计算](#契合度计算)
5. [信号注入](#信号注入)
6. [最佳实践](#最佳实践)

---

## 概述

洞察模块是 Agent Memory System 的"智能大脑"，负责从记忆中提取有价值的模式和预测，生成洞察信号注入上下文，辅助模型做出更智能的决策。

### 核心价值

- **预测性**：从历史模式预测未来行为
- **个性化**：基于用户画像定制洞察
- **可操作性**：提供具体的行动建议
- **无感化**：作为上下文增强，不干扰主流程

---

## 洞察类型

### InsightType 枚举

```python
class InsightType(str, Enum):
    USER_PREFERENCE = "user_preference"           # 用户偏好
    BEHAVIORAL_PATTERN = "behavioral_pattern"     # 行为模式
    BEST_PRACTICE = "best_practice"               # 最佳实践
    EFFICIENCY_OPPORTUNITY = "efficiency_opportunity"  # 效率机会
    KNOWLEDGE_GAP = "knowledge_gap"               # 知识缺口
    PROCESS_IMPROVEMENT = "process_improvement"   # 流程改进
    ERROR_PREVENTION = "error_prevention"         # 错误预防
    EMOTIONAL_PATTERN = "emotional_pattern"       # 情感模式
    IDENTITY_EVOLUTION = "identity_evolution"     # 身份演化
```

### 类型详解

#### 1. 用户偏好洞察

**触发条件**：检测到明确的用户偏好模式

**数据结构**：
```python
{
    "insight_type": "user_preference",
    "title": "用户偏好发现",
    "content": "用户偏好直接的沟通方式",
    "confidence": 0.85,
    "actions": ["采用直接沟通风格"]
}
```

**生成逻辑**：
```python
def detect_user_preference(profile: UserProfileData) -> list[InsightSignal]:
    """检测用户偏好"""
    signals = []
    
    if profile.communication_style.style:
        signals.append(InsightSignal(
            signal_type=InsightType.USER_PREFERENCE,
            confidence=0.85,
            data={"communication_style": profile.communication_style.style},
            raw_observation=f"用户偏好 {profile.communication_style.style} 的沟通方式"
        ))
    
    return signals
```

---

#### 2. 行为模式洞察

**触发条件**：识别到重复的决策模式

**数据结构**：
```python
{
    "insight_type": "behavioral_pattern",
    "title": "行为模式识别",
    "content": "发现重复决策模式: 概念讨论 → 设计 → 实现",
    "confidence": 0.78,
    "actions": ["应用已验证的工作流"]
}
```

**生成逻辑**：
```python
def detect_behavioral_pattern(procedural: ProceduralMemoryData) -> list[InsightSignal]:
    """检测行为模式"""
    signals = []
    
    for pattern in procedural.decision_patterns:
        if pattern.usage_count >= 3:
            signals.append(InsightSignal(
                signal_type=InsightType.BEHAVIORAL_PATTERN,
                confidence=pattern.confidence,
                data={
                    "pattern": pattern.workflow,
                    "trigger": pattern.trigger_condition,
                    "usage_count": pattern.usage_count
                }
            ))
    
    return signals
```

---

#### 3. 最佳实践洞察

**触发条件**：发现高效的问题解决策略或工具

**数据结构**：
```python
{
    "insight_type": "best_practice",
    "title": "最佳实践建议",
    "content": "工具 代码解释器 使用效果优秀 (成功率: 92%)",
    "confidence": 0.92,
    "actions": ["优先使用代码解释器", "参考已验证的方法"]
}
```

---

#### 4. 效率机会洞察

**触发条件**：发现可优化的流程或工具组合

**数据结构**：
```python
{
    "insight_type": "efficiency_opportunity",
    "title": "效率提升机会",
    "content": "发现工具组合模式: 文件搜索 → 代码解释器",
    "confidence": 0.70,
    "actions": ["尝试工具组合: 文件搜索 → 代码解释器"]
}
```

---

#### 5. 知识缺口洞察

**触发条件**：检测到知识覆盖不足

**数据结构**：
```python
{
    "insight_type": "knowledge_gap",
    "title": "知识缺口提示",
    "content": "语义知识覆盖度较低，可能存在知识缺口",
    "confidence": 0.60,
    "actions": ["主动补充相关知识", "询问用户是否需要详细解释"]
}
```

---

#### 6. 情感模式洞察

**触发条件**：识别到主导情感倾向

**数据结构**：
```python
{
    "insight_type": "emotional_pattern",
    "title": "情感模式洞察",
    "content": "用户情感倾向: 积极 (65%)",
    "confidence": 0.65,
    "actions": []
}
```

---

#### 7. 身份演化洞察

**触发条件**：检测到成长节点积累

**数据结构**：
```python
{
    "insight_type": "identity_evolution",
    "title": "身份演化追踪",
    "content": "用户有 5 个成长节点",
    "confidence": 0.70,
    "actions": []
}
```

---

## 信号生成机制

### 信号生命周期

```
原始观察
    ↓
信号检测
    ↓
置信度评估
    ↓
阈值过滤
    ↓
洞察生成
    ↓
优先级排序
    ↓
上下文注入
```

### InsightSignal 结构

```python
class InsightSignal:
    signal_id: str                 # 信号ID
    signal_type: InsightType       # 信号类型
    confidence: float              # 置信度 (0.0-1.0)
    data: dict[str, Any]           # 信号数据
    raw_observation: str           # 原始观察描述
    timestamp: datetime            # 时间戳
```

### 信号生成流程

```python
def generate_signals(
    long_term_memory: LongTermMemoryContainer,
    context: ReconstructedContext
) -> list[InsightSignal]:
    """
    生成洞察信号
    
    Args:
        long_term_memory: 长期记忆
        context: 重构上下文
    
    Returns:
        洞察信号列表
    """
    signals = []
    
    # 1. 用户偏好信号
    if long_term_memory.user_profile:
        signals.extend(detect_user_preference(
            long_term_memory.user_profile.data
        ))
    
    # 2. 行为模式信号
    if long_term_memory.procedural:
        signals.extend(detect_behavioral_pattern(
            long_term_memory.procedural.data
        ))
    
    # 3. 最佳实践信号
    if long_term_memory.procedural:
        signals.extend(detect_best_practice(
            long_term_memory.procedural.data
        ))
    
    # 4. 效率机会信号
    if long_term_memory.procedural:
        signals.extend(detect_efficiency_opportunity(
            long_term_memory.procedural.data
        ))
    
    # 5. 情感模式信号
    if long_term_memory.emotional:
        signals.extend(detect_emotional_pattern(
            long_term_memory.emotional.data
        ))
    
    # 6. 身份演化信号
    if long_term_memory.narrative:
        signals.extend(detect_identity_evolution(
            long_term_memory.narrative.data
        ))
    
    return signals
```

---

## 契合度计算

### 契合度定义

契合度衡量洞察信号与当前任务的相关程度。

### 计算公式

```python
def calculate_fit_score(
    signal: InsightSignal,
    current_task: str,
    user_profile: UserProfileData
) -> float:
    """
    计算契合度分数
    
    Args:
        signal: 洞察信号
        current_task: 当前任务
        user_profile: 用户画像
    
    Returns:
        契合度分数 (0.0-1.0)
    """
    # 基础分数 = 置信度
    base_score = signal.confidence
    
    # 任务相关性加成
    task_relevance = 0.0
    if signal.signal_type == InsightType.BEST_PRACTICE:
        if "tool" in signal.data:
            task_relevance = 0.1
    
    # 用户身份匹配加成
    identity_match = 0.0
    if signal.signal_type == InsightType.IDENTITY_EVOLUTION:
        identity_match = 0.1
    
    # 计算最终分数
    fit_score = base_score + task_relevance + identity_match
    
    return min(1.0, fit_score)
```

### 契合度阈值

| 契合度范围 | 处理方式 |
|------------|----------|
| 0.8 - 1.0 | 强制注入上下文 |
| 0.6 - 0.8 | 推荐注入 |
| 0.4 - 0.6 | 可选注入 |
| 0.0 - 0.4 | 不注入 |

---

## 信号注入

### 注入策略

洞察信号作为上下文增强注入，不影响主流程。

### 注入格式

```python
def inject_signals(
    context: ReconstructedContext,
    insights: list[Insight]
) -> ReconstructedContext:
    """
    注入洞察信号到上下文
    
    Args:
        context: 原始上下文
        insights: 洞察列表
    
    Returns:
        增强后的上下文
    """
    # 构建洞察摘要
    insight_summary = []
    for insight in insights:
        if insight.priority in [InsightPriority.HIGH, InsightPriority.MEDIUM]:
            insight_summary.append({
                "type": insight.insight_type.value,
                "title": insight.title,
                "content": insight.content,
                "confidence": insight.confidence,
                "actions": insight.actions[:2]  # 最多2个行动建议
            })
    
    # 注入到元数据
    context.metadata["active_insights"] = insight_summary
    
    return context
```

### 注入位置

```
System Prompt
    ↓
[记忆上下文]
    ↓
[洞察信号] ← 注入位置
    ↓
User Message
    ↓
Model Response
```

### 注入示例

```
## 记忆上下文
- 用户偏好：直接沟通风格
- 当前任务：技术实现

## 智能洞察
- [最佳实践] 工具 代码解释器 使用效果优秀 (置信度: 92%)
  建议：优先使用代码解释器
  
- [效率机会] 发现工具组合模式: 文件搜索 → 代码解释器
  建议：尝试此工具组合
```

---

## 最佳实践

### 1. 信号去重

```python
def deduplicate_signals(signals: list[InsightSignal]) -> list[InsightSignal]:
    """去重相似信号"""
    seen = set()
    unique = []
    
    for signal in signals:
        key = (signal.signal_type, signal.raw_observation[:50])
        if key not in seen:
            seen.add(key)
            unique.append(signal)
    
    return unique
```

### 2. 信号优先级

```python
PRIORITY_RULES = {
    InsightType.ERROR_PREVENTION: InsightPriority.HIGH,
    InsightType.BEST_PRACTICE: InsightPriority.HIGH,
    InsightType.USER_PREFERENCE: InsightPriority.MEDIUM,
    InsightType.EFFICIENCY_OPPORTUNITY: InsightPriority.MEDIUM,
    InsightType.BEHAVIORAL_PATTERN: InsightPriority.MEDIUM,
    InsightType.KNOWLEDGE_GAP: InsightPriority.LOW,
    InsightType.EMOTIONAL_PATTERN: InsightPriority.LOW,
    InsightType.IDENTITY_EVOLUTION: InsightPriority.LOW,
}
```

### 3. 信号时效性

```python
def is_signal_valid(signal: InsightSignal, max_age_hours: int = 24) -> bool:
    """检查信号时效性"""
    age = (datetime.now() - signal.timestamp).total_seconds() / 3600
    return age <= max_age_hours
```

### 4. 用户反馈闭环

```python
def record_insight_feedback(
    insight_id: str,
    user_action: str,
    effectiveness: float
) -> None:
    """
    记录洞察反馈
    
    Args:
        insight_id: 洞察ID
        user_action: 用户采取的行动
        effectiveness: 有效度 (0.0-1.0)
    """
    # 更新洞察统计
    # 调整未来生成权重
    pass
```

---

## 性能指标

| 指标 | 目标值 |
|------|--------|
| 信号生成延迟 | < 30ms |
| 信号数量限制 | ≤ 5 个/请求 |
| 契合度计算延迟 | < 10ms |
| 注入开销 | < 5ms |

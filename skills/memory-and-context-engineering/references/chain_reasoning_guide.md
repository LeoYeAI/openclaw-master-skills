# 链式推理增强模块使用指南

## 目录
- [概览](#概览)
- [核心概念](#核心概念)
- [快速开始](#快速开始)
- [与 LangGraph 集成](#与-langgraph-集成)
- [API 参考](#api-参考)
- [最佳实践](#最佳实践)
- [示例场景](#示例场景)

## 概览

链式推理增强模块（Chain Reasoning Enhancer）为智能体提供**模型自检测反思**能力，支持：

1. **反思检测**：模型通过输出 `ReflectionSignal` 字段主动触发反思
2. **反思执行**：分析问题、评估严重程度、生成修正建议
3. **验证执行**：判断是否需要验证、执行验证逻辑
4. **回退管理**：安全回退到之前的状态检查点
5. **持久化**：反思结果存储到长期记忆的 `EXTENDED_REFLECTION` 分类
6. **元学习**：提取训练数据，用于优化模型的"何时反思"能力

### 设计原则

- **最小干预**：仅在模型发出反思信号时介入，不影响正常推理热路径
- **状态感知**：与 `GlobalStateCapture` 深度集成，利用状态同步和检查点能力
- **类型安全**：所有接口使用 Pydantic 模型，确保类型安全

## 核心概念

### 反思信号（ReflectionSignal）

模型在推理输出中包含此字段，表示需要反思：

```python
from scripts.types import ReflectionSignal

signal = ReflectionSignal(
    need_reflect=True,
    reflect_reason="检测到信息矛盾",
    reflect_confidence=0.85,
)
```

### 反思触发类型（ReflectionTriggerType）

| 类型 | 说明 |
|------|------|
| `SELF_DETECTED` | 模型自检测触发 |
| `EXTERNAL_TRIGGER` | 外部触发（用户反馈等） |
| `SCHEDULED` | 定期检查触发 |
| `CONTEXT_CHANGE` | 上下文变化触发 |

### 反思结果（ReflectionOutcome）

| 结果 | 说明 |
|------|------|
| `CONFIRMED` | 确认正确，无需修改 |
| `CORRECTED` | 发现问题并已修正 |
| `ABORTED` | 中止反思 |
| `FALSE_POSITIVE` | 误报，无需反思 |

### 学习价值（LearningValue）

| 价值 | 说明 |
|------|------|
| `HIGH` | 高价值（如修正成功） |
| `MEDIUM` | 中等价值（如确认正确） |
| `LOW` | 低价值（如误报） |

## 快速开始

### 初始化

```python
from scripts.chain_reasoning import ChainReasoningEnhancer
from scripts.state_capture import GlobalStateCapture
from scripts.short_term import ShortTermMemoryManager
from scripts.long_term import LongTermMemoryManager

# 初始化依赖
state_capture = GlobalStateCapture(user_id="user_123")
short_term = ShortTermMemoryManager()
long_term = LongTermMemoryManager(user_id="user_123")

# 创建增强器
enhancer = ChainReasoningEnhancer(
    state_capture=state_capture,
    short_term=short_term,
    long_term=long_term,
    config={
        "max_rollback_count": 3,
        "verification_threshold": 0.7,
    },
)
```

### 处理推理步骤

```python
# 模型输出包含反思信号
reasoning_step = {
    "thought": "分析用户需求...",
    "need_reflect": True,
    "reflect_reason": "检测到信息矛盾",
    "reflect_confidence": 0.85,
}

# 处理步骤
result = enhancer.process_reasoning_step(
    step=reasoning_step,
    step_index=12,
    task_type="analysis",
)

if result["should_reflect"]:
    # 执行反思
    reflection_result = enhancer.execute_reflection(
        signal=result["signal"],
        context_snapshot=result["context_snapshot"],
    )

    if not reflection_result.passed:
        print(f"发现问题: {reflection_result.issues}")
        print(f"建议: {reflection_result.suggestion}")
```

### 持久化反思结果

```python
from scripts.types import ReflectionOutcome

# 持久化
memory_id = enhancer.persist_reflection_result(
    trigger_record=result["trigger_record"],
    reflection_result=reflection_result,
    verification_result=None,
    final_outcome=ReflectionOutcome.CORRECTED,
)

print(f"已存储到长期记忆: {memory_id}")
```

### 提取元学习数据

```python
from scripts.types import LearningValue

# 提取高价值训练数据
training_data = enhancer.extract_meta_learning_data(
    min_learning_value=LearningValue.MEDIUM,
    limit=100,
)

print(f"获取 {len(training_data)} 个训练样本")
```

## 与 LangGraph 集成

### 作为节点嵌入

```python
from langgraph.graph import StateGraph, END

# 创建工作流
workflow = StateGraph(State)

# 添加推理节点
workflow.add_node("reasoning", reasoning_node)

# 添加反思节点
workflow.add_node("reflection", enhancer.as_reflection_node())

# 添加验证节点
workflow.add_node("verification", enhancer.as_verification_node())

# 添加条件边
workflow.add_conditional_edges(
    "reasoning",
    ChainReasoningEnhancer.should_reflect,
    {
        "reflection": "reflection",
        "continue": "next_node",
    },
)

workflow.add_conditional_edges(
    "reflection",
    ChainReasoningEnhancer.should_verify,
    {
        "verification": "verification",
        "continue": "next_node",
        "rollback": "rollback_node",
    },
)
```

### 条件边函数

| 函数 | 用途 |
|------|------|
| `should_reflect(state)` | 判断是否需要反思 |
| `should_verify(state)` | 判断是否需要验证 |
| `should_rollback(state)` | 判断是否需要回退 |

### 回退处理

```python
# 在回退节点中处理
def rollback_node(state: dict[str, Any]) -> dict[str, Any]:
    step_index = state.get("current_step", 0)

    rollback_info = enhancer.handle_rollback(
        step_index=step_index,
        reason="验证失败",
    )

    if rollback_info["success"]:
        # 恢复到检查点
        checkpoint_id = rollback_info["checkpoint_id"]
        if checkpoint_id:
            state_capture.restore_checkpoint(checkpoint_id)

    return state
```

## API 参考

### ChainReasoningEnhancer

#### `__init__`

```python
def __init__(
    self,
    state_capture: GlobalStateCapture,
    short_term: ShortTermMemoryManager,
    long_term: LongTermMemoryManager,
    config: dict[str, Any] | None = None,
) -> None
```

**参数：**
- `state_capture`: 全局状态捕捉器
- `short_term`: 短期记忆管理器
- `long_term`: 长期记忆管理器
- `config`: 配置参数
  - `max_rollback_count`: 最大回退次数（默认 3）
  - `verification_threshold`: 验证阈值（默认 0.7）
  - `learning_value_threshold`: 学习价值阈值
  - `meta_learning_sample_limit`: 元学习样本上限

#### `process_reasoning_step`

```python
def process_reasoning_step(
    self,
    step: dict[str, Any] | ReasoningStepWithReflection,
    step_index: int,
    task_type: str = "unknown",
) -> dict[str, Any]
```

**返回：**
```python
{
    "should_reflect": bool,
    "signal": ReflectionSignal,
    "context_snapshot": dict,
    "trigger_record": ReflectionTriggerRecord | None,
}
```

#### `execute_reflection`

```python
def execute_reflection(
    self,
    signal: ReflectionSignal,
    context_snapshot: dict[str, Any],
    reasoning_context: list[dict[str, Any]] | None = None,
) -> ReflectionProcessResult
```

#### `execute_verification`

```python
def execute_verification(
    self,
    reflection_result: ReflectionProcessResult,
    context_snapshot: dict[str, Any],
) -> VerificationResult
```

#### `handle_rollback`

```python
def handle_rollback(
    self,
    step_index: int,
    reason: str,
) -> dict[str, Any]
```

**返回：**
```python
{
    "rollback_to": int,
    "checkpoint_id": str | None,
    "success": bool,
    "reason": str,
}
```

#### `persist_reflection_result`

```python
def persist_reflection_result(
    self,
    trigger_record: ReflectionTriggerRecord,
    reflection_result: ReflectionProcessResult,
    verification_result: VerificationResult | None,
    final_outcome: ReflectionOutcome,
) -> str
```

**返回：** 存储的记忆 ID

#### `extract_meta_learning_data`

```python
def extract_meta_learning_data(
    self,
    min_learning_value: LearningValue = LearningValue.MEDIUM,
    limit: int = 100,
) -> list[MetaLearningSample]
```

## 最佳实践

### 1. 反思信号设计

模型应在以下场景输出反思信号：

- 检测到信息矛盾
- 推理置信度低于阈值
- 发现遗漏关键信息
- 推理路径存在风险

### 2. 验证策略

高严重程度问题必须验证：
- `CRITICAL`: 必须验证并可能回退
- `HIGH`: 建议验证
- `MEDIUM`: 可选验证
- `LOW`: 通常跳过

高风险场景必须验证：
- 金融决策
- 法律分析
- 医疗建议
- 调试排错

### 3. 回退管理

- 设置合理的 `max_rollback_count`，避免无限循环
- 每次新任务开始时调用 `reset_rollback_state()`
- 利用检查点机制快速恢复状态

### 4. 持久化时机

在以下时机持久化反思结果：
- 反思成功修正后
- 验证失败回退前
- 高学习价值场景

## 示例场景

### 场景 1：信息矛盾检测

```python
# 模型输出
reasoning_output = {
    "thought": "用户说想要 X，但上下文显示之前拒绝过 X",
    "need_reflect": True,
    "reflect_reason": "检测到用户需求矛盾",
    "reflect_confidence": 0.9,
}

result = enhancer.process_reasoning_step(
    step=reasoning_output,
    step_index=5,
    task_type="requirement_analysis",
)

# 执行反思
reflection = enhancer.execute_reflection(
    signal=result["signal"],
    context_snapshot=result["context_snapshot"],
)

# reflection.issues = ["检测到用户需求矛盾"]
# reflection.suggestion = "需要向用户确认真实需求"
```

### 场景 2：低置信度触发

```python
# 模型输出
reasoning_output = {
    "thought": "尝试推断用户意图，但证据不足",
    "need_reflect": True,
    "reflect_reason": "推断置信度不足",
    "reflect_confidence": 0.4,
}

result = enhancer.process_reasoning_step(
    step=reasoning_output,
    step_index=8,
)

reflection = enhancer.execute_reflection(
    signal=result["signal"],
    context_snapshot=result["context_snapshot"],
)

# reflection.severity = ReflectionSeverity.HIGH
# reflection.need_verification = True
```

### 场景 3：回退恢复

```python
# 验证失败，需要回退
verification = enhancer.execute_verification(
    reflection_result=reflection,
    context_snapshot=context_snapshot,
)

if verification.result == "failed":
    rollback_info = enhancer.handle_rollback(
        step_index=10,
        reason="验证失败：存在关键错误",
    )

    if rollback_info["success"] and rollback_info["checkpoint_id"]:
        # 恢复到检查点
        state_capture.restore_checkpoint(rollback_info["checkpoint_id"])
        # 重新推理
        ...
```

### 场景 4：元学习训练

```python
# 定期提取训练数据
training_samples = enhancer.extract_meta_learning_data(
    min_learning_value=LearningValue.HIGH,
    limit=200,
)

# 转换为训练格式
for sample in training_samples:
    print(f"样本ID: {sample.sample_id}")
    print(f"是否应该反思: {sample.should_reflect}")
    print(f"反思原因: {sample.reflect_reason}")
    print(f"结果是否正确: {sample.was_correct}")
    print("---")
```

## 配置参考

### 默认配置

```python
DEFAULT_CONFIG = {
    "max_rollback_count": 3,
    "verification_threshold": 0.7,
    "learning_value_threshold": LearningValue.MEDIUM,
    "meta_learning_sample_limit": 100,
}
```

### 自定义配置

```python
enhancer = ChainReasoningEnhancer(
    state_capture=state_capture,
    short_term=short_term,
    long_term=long_term,
    config={
        "max_rollback_count": 5,  # 允许更多回退
        "verification_threshold": 0.8,  # 更严格的验证阈值
        "meta_learning_sample_limit": 500,  # 更多训练样本
    },
)
```

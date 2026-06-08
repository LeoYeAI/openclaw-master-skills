---
name: agent-memory
description: 当智能体涉及"memory"与"Context"的操作时触发skill；智能体底层记忆基础设施，完整实现Context Engineering五大核心能力：选择（噪声过滤+相关性筛选）、压缩（因果结构提取+工具结果压缩）、检索（结果重排序+多样性保证）、状态（任务进度追踪+目标对齐）、记忆（冲突检测+跨会话关联）；认知模型层支持认知模型构建、因果链提取、知识缺口识别、检索时机决策、质量评估、状态一致性校验、状态推理、跨会话关联、遗忘机制；作为元技能强制常驻运行
always: true
dependency:
  python:
    - pydantic>=2.0.0
    - typing-extensions>=4.0.0
    - cryptography>=41.0.0
    - redis>=4.5.0
    - tiktoken>=0.5.0
---

# Agent Memory System

## 任务目标

- 本 Skill 用于：为智能体构建完整的记忆能力基础设施，实现 Context Engineering 核心能力
- 触发条件：**元技能，强制常驻运行**（`always: true`）
- 架构总览：详见 [references/architecture_overview.md](references/architecture_overview.md)
- 枚举参考：详见 [references/api_enums.md](references/api_enums.md)

## 前置准备

### 依赖

```
pydantic>=2.0.0
typing-extensions>=4.0.0
cryptography>=41.0.0
redis>=4.5.0
tiktoken>=0.5.0
```

### 存储路径（必需）

所有模块初始化时**必须指定存储路径**：

```python
base_path = "./memory_data"
key_storage_path = f"{base_path}/keys"
sync_state_path = f"{base_path}/sync_state"
index_storage_path = f"{base_path}/memory_index"
credential_path = f"{base_path}/credentials"
```

### Redis 连接（推荐）

```python
from scripts.redis_adapter import create_redis_adapter

redis_adapter = create_redis_adapter(host="localhost", port=6379)
if redis_adapter.is_available():
    print("Redis 连接成功")
```

## 操作步骤

### Step 1: 隐私配置（必需）

```python
from scripts.privacy import PrivacyManager, ConsentStatus

privacy_manager = PrivacyManager(user_id="user_123")
if privacy_manager.get_consent_status("memory_storage") == ConsentStatus.NOT_REQUESTED:
    privacy_manager.request_consent(
        consent_type="memory_storage",
        description="是否允许存储交互记忆以提供个性化服务？"
    )
```

### Step 2: 感知与短期记忆

```python
from scripts.perception import PerceptionMemoryStore
from scripts.short_term import ShortTermMemoryManager
from scripts.types import SemanticBucketType

# 感知记忆
perception = PerceptionMemoryStore()
session_id = perception.create_session()

# 短期记忆（智能体判断语义分类）
short_term = ShortTermMemoryManager()
item_id = short_term.store_with_semantics(
    content="用户想要实现登录功能",
    bucket_type=SemanticBucketType.USER_INTENT,
    topic_label="用户登录",
    relevance_score=0.85,
)
```

### Step 3: 长期记忆

```python
from scripts.long_term import LongTermMemoryManager

long_term = LongTermMemoryManager()
long_term.update_user_profile(profile_data)
long_term.apply_heat_policy()
```

### Step 4: 上下文重构与洞察

```python
from scripts.context_reconstructor import ContextReconstructor
from scripts.insight_module import InsightModule

reconstructor = ContextReconstructor()
insight_module = InsightModule()

context = reconstructor.reconstruct(situation, long_term.get_all_memories())
insights = insight_module.process(context, long_term.get_all_memories())
```

### Step 5: 全局状态捕捉（LangGraph集成）

```python
from scripts.state_capture import GlobalStateCapture, StateEventType

capture = GlobalStateCapture(
    user_id="user_123",
    storage_path="./state_storage",
)

# 从 LangGraph 同步
checkpoint_id = capture.sync_from_langgraph(
    state={"phase": "executing", "current_task": "create_memory"},
    node_name="executor",
)

# 事件订阅
subscription_id = capture.subscribe(
    event_types=[StateEventType.PHASE_CHANGE, StateEventType.TASK_SWITCH],
    callback=on_phase_change,
)
```

### Step 6: Context Orchestrator（总控层）

```python
from scripts.context_orchestrator import create_context_orchestrator
from scripts.types import SemanticBucketType

orchestrator = create_context_orchestrator(
    user_id="user_123",
    session_id="session_456",
    max_context_tokens=32000,
)

# 存储记忆
orchestrator.store_memory(
    content="用户想要实现登录功能",
    bucket_type=SemanticBucketType.USER_INTENT,
    topic_label="用户登录",
)

# 准备上下文
context = orchestrator.prepare_context(
    user_input="帮我分析这段代码的性能问题",
    system_instruction="你是一个代码分析专家",
    retrieval_results=["性能优化最佳实践"],
    tool_results=["代码分析结果..."],
)

# 结束会话
final_stats = orchestrator.end_session()
```

### Step 7: 认知模型构建

```python
from scripts.cognitive_model_builder import CognitiveModelBuilder, StepResult, FactSource

builder = CognitiveModelBuilder(session_id="session_001")

# 设置任务上下文
builder.set_task_context(
    goal="实现用户登录功能",
    sub_goals=["数据库设计", "前端表单", "后端验证"],
    current_focus="后端验证逻辑",
)

# 添加已知事实和约束
builder.add_fact(content="用户使用Python 3.9", source=FactSource.MEMORY, confidence=0.9)
builder.add_constraint("must_use", "bcrypt加密")
builder.add_knowledge_gap(description="SSO集成方案", importance="high")

# 构建认知模型
model = builder.build()
print(model.to_context_string())  # 输出模型可理解的上下文
```

### Step 8: 因果链提取

```python
from scripts.causal_chain_extractor import CausalChainExtractor

extractor = CausalChainExtractor()
chains = extractor.extract("登录失败是因为数据库连接超时...")

for chain in chains:
    print(chain.to_summary())
    # 问题: 登录失败
    # 根本原因: 连接池配置过小
    # 解决方案: 增加连接池大小
```

### Step 9: 知识缺口识别

```python
from scripts.knowledge_gap_identifier import KnowledgeGapIdentifier, KnowledgeType

identifier = KnowledgeGapIdentifier()

# 注册已有知识
identifier.register_knowledge(content="用户使用Python 3.9", knowledge_type=KnowledgeType.FACTUAL)

# 定义所需知识
identifier.define_required(description="数据库连接配置", for_task="配置连接", importance=4)

# 分析缺口
result = identifier.analyze()
print(f"知识缺口: {result.total_gaps}, 覆盖率: {result.coverage_ratio:.1%}")
```

### Step 10: 检索决策与评估

```python
from scripts.retrieval_decision_engine import RetrievalDecisionEngine
from scripts.retrieval_quality_evaluator import RetrievalQualityEvaluator

# 检索决策
engine = RetrievalDecisionEngine()
decision = engine.decide(query="如何优化Python代码性能")

if decision.need in ["required", "recommended"]:
    print(f"建议检索: {decision.queries}")

# 质量评估
evaluator = RetrievalQualityEvaluator()
result = evaluator.evaluate(query="...", items=[{"item_id": "1", "content": "...", "score": 0.9}])
print(f"质量评分: {result.quality.overall_score:.2f}")
```

### Step 11: 状态一致性校验

```python
from scripts.state_consistency_validator import StateConsistencyValidator, StateModule

validator = StateConsistencyValidator()

# 注册各模块状态
validator.register_state(module=StateModule.TASK_PROGRESS, state={"current_task": "登录功能"})
validator.register_state(module=StateModule.SHORT_TERM_MEMORY, state={"topic": "用户认证"})

# 执行校验
report = validator.validate()
if report.conflicts:
    fixed = validator.auto_fix(report)
    print(f"修复了 {fixed} 个冲突")
```

### Step 12: 状态推理

```python
from scripts.state_inference_engine import StateInferenceEngine

engine = StateInferenceEngine()
engine.add_premise("任务进度是80%", confidence=0.9)
engine.add_premise("没有阻塞问题", confidence=0.8)

result = engine.infer_next_state()
print(f"推理结果: {result.inferred_value}, 置信度: {result.confidence:.2f}")
```

### Step 13: 跨会话关联

```python
from scripts.cross_session_memory_linker import CrossSessionMemoryLinker, LinkType

linker = CrossSessionMemoryLinker()

linker.register_session(session_id="session_001", topics=["Python优化"], entities=["Pandas"])
linker.register_session(session_id="session_002", topics=["Python优化"], entities=["Redis"])

# 发现关联
links = linker.discover_links()
related = linker.get_related_sessions("session_001")
```

### Step 14: 遗忘机制

```python
from scripts.memory_forgetting_mechanism import MemoryForgettingMechanism, MemoryImportance

mechanism = MemoryForgettingMechanism()

mechanism.register_memory(memory_id="mem_001", importance=MemoryImportance.HIGH)
mechanism.access_memory("mem_001")  # 提升活跃度

candidates = mechanism.analyze_forgetting_candidates()
report = mechanism.execute_forgetting(candidates)
print(f"活跃记忆: {report.active_memories}, 归档: {report.archived_memories}")
```

### Step 15: 多源协调

```python
from scripts.multi_source_coordinator import MultiSourceCoordinator, SourceType

coordinator = MultiSourceCoordinator()

coordinator.register_source(source_type=SourceType.SYSTEM_INSTRUCTION, content="你是代码分析专家")
coordinator.register_source(source_type=SourceType.USER_QUERY, content="帮我分析代码")
coordinator.register_source(source_type=SourceType.LONG_TERM_MEMORY, content="用户偏好Python")

context = coordinator.coordinate(max_tokens=8000)
print(f"Token使用: {context.token_count}, 来源: {len(context.sources_used)}")
```

### Step 16: 上下文懒加载

```python
from scripts.context_lazy_loader import create_lazy_loader

loader = create_lazy_loader(max_cache_size=1000)
loader.register_loader("user_profile", lambda: fetch_user_profile())

result = loader.load("user_profile")
predicted = loader.predict_and_preload("user_profile")
print(f"缓存命中率: {loader.get_stats().cache_hit_rate:.1%}")
```

### Step 17: 权限边界控制

```python
from scripts.permission_boundary_controller import create_permission_controller

controller = create_permission_controller()
controller.set_user_permission(user_id="user_123", roles=["user"])

# 检查访问权限
result = controller.check_access(user_id="user_123", resource="memory:long_term", action="read")

# 过滤敏感信息
filtered = controller.filter_sensitive("我的API Key是 sk-xxx，邮箱是 user@example.com")
print(f"过滤后: {filtered.filtered}")
```

### Step 18: 可观测性管理

```python
from scripts.observability_manager import create_observability_manager, LatencyTracker

manager = create_observability_manager(token_cost_per_1k=0.03)

# 记录Token使用
record = manager.record_token_usage(session_id="session_001", total_tokens=1800, model="gpt-4")
print(f"成本: ${record.cost_estimate:.4f}")

# 延迟追踪
with LatencyTracker(manager, "context_prepare") as tracker:
    tracker.start_stage("memory_load")
    # ... 加载记忆
    tracker.end_stage("memory_load")

# 获取统计
stats = manager.get_stats(hours=24)
print(f"总Token: {stats.total_tokens}, 总成本: ${stats.total_cost:.2f}")
```

### Step 19: 结果压缩

```python
from scripts.result_compressor import ResultCompressor, CompressionStrategy

compressor = ResultCompressor()
result = compressor.compress_tool_result(content=long_log_content, target_tokens=1000)

print(f"压缩率: {result.compression_ratio:.2%}")
print(f"因果链: {len(result.causal_chains)} 个")
```

### Step 20: 任务进度追踪

```python
from scripts.task_progress import TaskProgressTracker, StepType

tracker = TaskProgressTracker(task_id="task_001", task_name="实现登录功能")
tracker.set_goal(goal_id="goal_001", goal_name="实现登录", success_criteria=["用户可以登录"])

tracker.track_step(step_id="step_001", step_name="设计流程", step_type=StepType.PLANNING)
tracker.start_step("step_001")
tracker.complete_step("step_001", result="流程设计完成")

report = tracker.get_progress_report()
print(f"完成率: {report.completion_rate:.1%}")
```

### Step 21: 记忆冲突检测

```python
from scripts.memory_conflict import MemoryConflictDetector

detector = MemoryConflictDetector()
conflicts = detector.detect_all_conflicts(new_memory=item, existing_memories=memories)

if conflicts:
    result = detector.resolve_conflict(conflict=conflicts[0], mode="recency")
    print(f"解决方案: {result.rationale}")
```

### Step 22: 链式推理增强

```python
from scripts.chain_reasoning import ChainReasoningEnhancer

enhancer = ChainReasoningEnhancer(state_capture=capture, short_term=short_term, long_term=long_term)

result = enhancer.process_reasoning_step(
    step={"thought": "分析...", "need_reflect": True, "reflect_reason": "信息矛盾"},
    step_index=12,
)

if result["should_reflect"]:
    reflection_result = enhancer.execute_reflection(signal=result["signal"], context_snapshot=result["context_snapshot"])
```

## 资源索引

### 核心脚本（40个）

| 脚本 | 用途 | 层级 |
|------|------|------|
| [scripts/types.py](scripts/types.py) | 核心类型定义 | 基础 |
| [scripts/redis_adapter.py](scripts/redis_adapter.py) | Redis 连接管理 | 基础设施 |
| [scripts/encryption.py](scripts/encryption.py) | 数据加密模块 | 基础设施 |
| [scripts/credential_manager.py](scripts/credential_manager.py) | 凭证管理 | 基础设施 |
| [scripts/perception.py](scripts/perception.py) | 感知记忆 | 存储层 |
| [scripts/short_term.py](scripts/short_term.py) | 短期记忆（文件存储） | 存储层 |
| [scripts/short_term_insight.py](scripts/short_term_insight.py) | 短期记忆洞察分析 | 存储层 |
| [scripts/long_term.py](scripts/long_term.py) | 长期记忆 | 存储层 |
| [scripts/memory_index.py](scripts/memory_index.py) | 记忆索引管理 | 存储层 |
| [scripts/heat_manager.py](scripts/heat_manager.py) | 热度管理 | 存储层 |
| [scripts/memory_forgetting_mechanism.py](scripts/memory_forgetting_mechanism.py) | 记忆遗忘机制 | 存储层 |
| [scripts/async_writer.py](scripts/async_writer.py) | 异步写入器（性能优化） | 基础设施 |
| [scripts/batched_writer.py](scripts/batched_writer.py) | 批量写入器（性能优化） | 基础设施 |
| [scripts/state_capture.py](scripts/state_capture.py) | 状态捕捉 | 协调层 |
| [scripts/incremental_sync.py](scripts/incremental_sync.py) | 增量同步 | 协调层 |
| [scripts/chain_reasoning.py](scripts/chain_reasoning.py) | 链式推理增强 | 协调层 |
| [scripts/context_reconstructor.py](scripts/context_reconstructor.py) | 上下文重构 | 协调层 |
| [scripts/insight_module.py](scripts/insight_module.py) | 独立洞察 | 协调层 |
| [scripts/task_progress.py](scripts/task_progress.py) | 任务进度追踪器 | 协调层 |
| [scripts/memory_conflict.py](scripts/memory_conflict.py) | 记忆冲突检测器 | 协调层 |
| [scripts/conflict_resolver.py](scripts/conflict_resolver.py) | 冲突解决器 | 协调层 |
| [scripts/state_consistency_validator.py](scripts/state_consistency_validator.py) | 状态一致性校验器 | 协调层 |
| [scripts/state_inference_engine.py](scripts/state_inference_engine.py) | 状态推理引擎 | 协调层 |
| [scripts/cross_session_memory_linker.py](scripts/cross_session_memory_linker.py) | 跨会话记忆关联器 | 协调层 |
| [scripts/context_orchestrator.py](scripts/context_orchestrator.py) | 上下文编排器（总控） | 编排层 |
| [scripts/token_budget.py](scripts/token_budget.py) | Token 预算管理 | 编排层 |
| [scripts/result_compressor.py](scripts/result_compressor.py) | 结果压缩器 | 编排层 |
| [scripts/retrieval_organizer.py](scripts/retrieval_organizer.py) | 检索结果组织器 | 编排层 |
| [scripts/noise_filter.py](scripts/noise_filter.py) | 噪声过滤器 | 编排层 |
| [scripts/multi_source_coordinator.py](scripts/multi_source_coordinator.py) | 多源协调器 | 编排层 |
| [scripts/context_lazy_loader.py](scripts/context_lazy_loader.py) | 上下文懒加载器 | 编排层 |
| [scripts/permission_boundary_controller.py](scripts/permission_boundary_controller.py) | 权限边界控制器 | 编排层 |
| [scripts/observability_manager.py](scripts/observability_manager.py) | 可观测性管理器 | 编排层 |
| [scripts/cognitive_model_builder.py](scripts/cognitive_model_builder.py) | 认知模型构建器 | 编排层 |
| [scripts/causal_chain_extractor.py](scripts/causal_chain_extractor.py) | 因果链提取器 | 编排层 |
| [scripts/knowledge_gap_identifier.py](scripts/knowledge_gap_identifier.py) | 知识缺口识别器 | 编排层 |
| [scripts/retrieval_decision_engine.py](scripts/retrieval_decision_engine.py) | 检索时机决策引擎 | 编排层 |
| [scripts/retrieval_quality_evaluator.py](scripts/retrieval_quality_evaluator.py) | 检索质量评估器 | 编排层 |
| [scripts/privacy.py](scripts/privacy.py) | 隐私配置 | 基础 |

### 参考文档

| 文档 | 何时读取 |
|------|----------|
| [architecture_overview.md](references/architecture_overview.md) | 需要全局架构视角 |
| [api_enums.md](references/api_enums.md) | 查阅枚举类型定义 |
| [api_class_reference.md](references/api_class_reference.md) | 查看所有导出类名和职责 |
| [memory_types.md](references/memory_types.md) | 深入理解记忆结构 |
| [chain_reasoning_guide.md](references/chain_reasoning_guide.md) | 链式推理增强集成 |
| [encryption_guide.md](references/encryption_guide.md) | 了解数据加密机制 |
| [async_optimization_guide.md](references/async_optimization_guide.md) | 异步写入优化方案 |
| [privacy_guide.md](references/privacy_guide.md) | 隐私配置和合规要求 |
| [insight_design.md](references/insight_design.md) | 洞察生成机制设计 |
| [activation_mechanism.md](references/activation_mechanism.md) | 记忆激活机制 |
| [agent_loops_guide.md](references/agent_loops_guide.md) | 智能体循环集成 |
| [index_sync_guide.md](references/index_sync_guide.md) | 索引同步机制 |
| [short_term_insight_guide.md](references/short_term_insight_guide.md) | 短期记忆洞察分析 |

## 注意事项

1. **路径必传**：所有存储路径无默认值，必须显式传入
2. **隐私优先**：处理用户数据前必须初始化 `PrivacyManager` 并获取同意
3. **敏感数据**：系统自动识别密码、账号等敏感信息，默认不存储
4. **类型安全**：所有函数必须有类型注解，禁止使用裸 dict
5. **异步优先**：提炼、热度计算等后台异步执行
6. **降级策略**：模块故障时自动降级，保证核心流程可用

## 快速开始

```python
from scripts.perception import PerceptionMemoryStore
from scripts.short_term import ShortTermMemoryManager
from scripts.long_term import LongTermMemoryManager
from scripts.context_reconstructor import ContextReconstructor

# 初始化
perception = PerceptionMemoryStore()
short_term = ShortTermMemoryManager()
long_term = LongTermMemoryManager()
reconstructor = ContextReconstructor()

# 处理对话
session_id = perception.create_session()
perception.store_conversation(session_id, user_message, system_response)

# 短期记忆
short_term.store_with_semantics(user_message, SemanticBucketType.USER_INTENT, "话题", 0.8)

# 上下文重构
context = reconstructor.reconstruct(situation, long_term.get_all_memories())
```

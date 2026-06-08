"""
Agent Memory System - 核心类型定义

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证和序列化
  * typing-extensions: >=4.0.0
    - 用途：类型扩展支持
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  typing-extensions>=4.0.0
  ```
=== 声明结束 ===

安全提醒：定期运行 pip audit 进行安全审计
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class MemoryType(str, Enum):
    """记忆类型枚举"""

    USER_PROFILE = "user_profile"
    PROCEDURAL = "procedural"
    NARRATIVE = "narrative"
    SEMANTIC = "semantic"
    EMOTIONAL = "emotional"


class MemoryCategory(str, Enum):
    """8种记忆分类体系

    注意：上下文（Context）是动态的、会话级别的，由短期记忆和上下文重构器管理，
    不属于长期记忆的持久化范畴。
    """

    # 核心层（持久化，跨会话稳定）
    CORE_IDENTITY = "core_identity"  # 核心身份 → UserProfileMemory.identity
    CORE_PREFERENCE = "core_preference"  # 核心偏好 → UserProfileMemory.preferences
    CORE_SKILL = "core_skill"  # 核心技能 → ProceduralMemory（工具使用、决策模式）
    # 扩展层（动态更新，跨会话积累）
    EXTENDED_BEHAVIOR = "extended_behavior"  # 扩展行为 → ProceduralMemory.operation_preferences
    EXTENDED_EMOTION = "extended_emotion"  # 扩展情感 → EmotionalMemory
    EXTENDED_KNOWLEDGE = "extended_knowledge"  # 扩展知识 → SemanticMemory
    EXTENDED_NARRATIVE = "extended_narrative"  # 扩展叙事 → NarrativeMemory
    # 反思层（链式推理增强）
    EXTENDED_REFLECTION = "extended_reflection"  # 反思记忆 → 元学习训练数据


class SemanticBucketType(str, Enum):
    """语义分类桶类型"""

    TASK_CONTEXT = "task_context"  # 任务上下文桶
    USER_INTENT = "user_intent"  # 用户意图桶
    KNOWLEDGE_GAP = "knowledge_gap"  # 知识缺口桶
    EMOTIONAL_TRACE = "emotional_trace"  # 情感痕迹桶
    DECISION_CONTEXT = "decision_context"  # 决策上下文桶


class QualityDimension(str, Enum):
    """六维质量评估维度"""

    RELEVANCE = "relevance"  # 相关性
    COMPLETENESS = "completeness"  # 完整性
    COHERENCE = "coherence"  # 连贯性
    TIMELINESS = "timeliness"  # 时效性
    DIVERSITY = "diversity"  # 多样性
    ACTIONABILITY = "actionability"  # 可操作性


class ScenarioType(str, Enum):
    """场景类型"""

    CODING = "coding"  # 编码场景
    DEBUGGING = "debugging"  # 调试场景
    DESIGN = "design"  # 设计场景
    ANALYSIS = "analysis"  # 分析场景
    LEARNING = "learning"  # 学习场景
    PLANNING = "planning"  # 规划场景
    REVIEW = "review"  # 审查场景


class PhaseType(str, Enum):
    """阶段类型"""

    EXPLORATION = "exploration"  # 探索阶段
    DESIGN = "design"  # 设计阶段
    IMPLEMENTATION = "implementation"  # 实现阶段
    VERIFICATION = "verification"  # 验证阶段
    REFINEMENT = "refinement"  # 优化阶段


class UserStateType(str, Enum):
    """用户状态类型"""

    FOCUSED = "focused"  # 专注状态
    CONFUSED = "confused"  # 困惑状态
    EXPLORATORY = "exploratory"  # 探索状态
    DECISIVE = "decisive"  # 决断状态
    FRUSTRATED = "frustrated"  # 挫败状态
    SATISFIED = "satisfied"  # 满意状态


class HeatLevel(str, Enum):
    """冷热度层级"""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class ConflictType(str, Enum):
    """冲突类型"""

    FACTUAL_CONTRADICTION = "factual_contradiction"
    TEMPORAL_EVOLUTION = "temporal_evolution"
    CONTEXT_DEPENDENCY = "context_dependency"
    CONFIDENCE_CONFLICT = "confidence_conflict"
    DATA_INCONSISTENCY = "data_inconsistency"
    CONCEPT_AMBIGUITY = "concept_ambiguity"
    STRATEGY_CONFLICT = "strategy_conflict"
    EMOTIONAL_INCONSISTENCY = "emotional_inconsistency"
    TEMPORAL_INVALIDATION = "temporal_invalidation"


class ResolutionMode(str, Enum):
    """冲突解决模式"""

    LOGIC_DOMINANT = "logic_dominant"
    BALANCED = "balanced"
    NEUROTICISM_DOMINANT = "neuroticism_dominant"
    RECENCY = "recency"
    FREQUENCY = "frequency"
    USER_CONFIRMATION = "user_confirmation"
    SOURCE_TRUST = "source_trust"
    CONTEXTUAL = "contextual"


class TriggerDimension(str, Enum):
    """激活器维度"""

    TEMPORAL = "temporal"
    SEMANTIC = "semantic"
    CONTEXTUAL = "contextual"
    EMOTIONAL = "emotional"
    CAUSAL = "causal"
    IDENTITY = "identity"


class SignalType(str, Enum):
    """洞察信号类型"""

    DECISION_SUPPORT = "decision_support"
    PROACTIVE_SUGGESTION = "proactive_suggestion"
    RISK_ALERT = "risk_alert"
    TIMING_HINT = "timing_hint"
    TOOL_RECOMMENDATION = "tool_recommendation"


class InsightType(str, Enum):
    """洞察类型"""

    USER_PREFERENCE = "user_preference"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    BEST_PRACTICE = "best_practice"
    EFFICIENCY_OPPORTUNITY = "efficiency_opportunity"
    KNOWLEDGE_GAP = "knowledge_gap"
    PROCESS_IMPROVEMENT = "process_improvement"
    ERROR_PREVENTION = "error_prevention"
    EMOTIONAL_PATTERN = "emotional_pattern"
    IDENTITY_EVOLUTION = "identity_evolution"


# ============================================================================
# 链式推理增强 - 反思类型
# ============================================================================


class ReflectionTriggerType(str, Enum):
    """反思触发类型"""

    SELF_DETECTED = "self_detected"  # 模型自检测
    RULE_TRIGGERED = "rule_triggered"  # 规则触发（备用）
    MILESTONE = "milestone"  # 关键节点
    RESOURCE_WARNING = "resource_warning"  # 资源预警


class ReflectionOutcome(str, Enum):
    """反思结果类型（元学习标签）"""

    CORRECTED = "corrected"  # 纠正了错误
    CONFIRMED = "confirmed"  # 确认无误
    FALSE_POSITIVE = "false_positive"  # 误报（无需反思）
    UNRESOLVED = "unresolved"  # 未解决


class LearningValue(str, Enum):
    """元学习价值评估"""

    HIGH = "high"  # 高价值：发现真实问题并解决
    MEDIUM = "medium"  # 中价值：确认无误但过程有意义
    LOW = "low"  # 低价值：误报


class ReflectionSeverity(str, Enum):
    """反思问题严重程度"""

    CRITICAL = "critical"  # 严重：需要立即回退
    HIGH = "high"  # 高：需要验证
    MEDIUM = "medium"  # 中：需要注意
    LOW = "low"  # 低：可忽略


class InsightPriority(str, Enum):
    """洞察优先级"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SignalStrength(str, Enum):
    """信号强度"""

    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class DecisionType(str, Enum):
    """决策类型"""

    TOOL_CHOICE = "tool_choice"
    APPROACH_SELECTION = "approach_selection"
    PREFERENCE_EXPRESSION = "preference_expression"
    CONFIRMATION = "confirmation"
    REJECTION = "rejection"


class TaskType(str, Enum):
    """任务类型"""

    TECHNICAL_IMPLEMENTATION = "technical_implementation"
    CODE_DEBUGGING = "code_debugging"
    PRECISE_CALCULATION = "precise_calculation"
    CREATIVE_DESIGN = "creative_design"
    PROBLEM_SOLVING = "problem_solving"
    BRAINSTORMING = "brainstorming"
    DATA_ANALYSIS = "data_analysis"
    KNOWLEDGE_QUERY = "knowledge_query"


# ============================================================================
# 基础数据结构
# ============================================================================


class TimestampMixin(BaseModel):
    """时间戳混入"""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ConfidenceMixin(BaseModel):
    """置信度混入"""

    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class HeatMixin(BaseModel):
    """热度混入"""

    heat_score: float = Field(ge=0.0, le=100.0, default=50.0)
    heat_level: HeatLevel = Field(default=HeatLevel.WARM)
    last_accessed_at: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0)


# ============================================================================
# 链式推理增强 - 反思数据模型
# ============================================================================


class ReflectionSignal(BaseModel):
    """模型自检测的反思信号（嵌入推理输出中）"""

    need_reflect: bool = Field(default=False, description="是否需要反思")
    reflect_reason: str | None = Field(default=None, description="反思原因")
    reflect_confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="反思置信度"
    )


class ReasoningStepWithReflection(BaseModel):
    """带反思信号的推理步骤"""

    thought: str = Field(description="推理思考")
    action: str | None = Field(default=None, description="执行动作")
    action_input: dict[str, Any] | None = Field(default=None, description="动作输入")
    final_answer: str | None = Field(default=None, description="最终答案")

    # 反思信号（模型自检测）
    reflection_signal: ReflectionSignal = Field(
        default_factory=ReflectionSignal, description="反思信号"
    )


class ReflectionTriggerRecord(BaseModel):
    """反思触发记录（存储到短期记忆）"""

    record_id: str = Field(default_factory=lambda: f"refl_trig_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    trigger_type: ReflectionTriggerType = Field(description="触发类型")
    trigger_reason: str = Field(description="触发原因")
    trigger_confidence: float = Field(ge=0.0, le=1.0, description="触发置信度")
    step_index: int = Field(description="推理步骤索引")
    task_type: str = Field(description="任务类型")
    context_snapshot: dict[str, Any] = Field(default_factory=dict, description="状态快照")
    created_at: datetime = Field(default_factory=datetime.now)


class ReflectionProcessResult(BaseModel):
    """反思执行结果"""

    passed: bool = Field(description="是否通过")
    issues: list[str] = Field(default_factory=list, description="发现的问题")
    severity: ReflectionSeverity = Field(
        default=ReflectionSeverity.LOW, description="严重程度"
    )
    suggestion: str | None = Field(default=None, description="修正建议")
    need_verification: bool = Field(default=False, description="是否需要验证")
    corrected_step: ReasoningStepWithReflection | None = Field(
        default=None, description="修正后的步骤"
    )


class VerificationResult(BaseModel):
    """验证结果"""

    triggered: bool = Field(default=False, description="是否触发验证")
    result: str | None = Field(default=None, description="验证结果")
    resolution: str | None = Field(default=None, description="解决方案")
    evidence: list[str] = Field(default_factory=list, description="证据链")


class ReflectionMemoryItem(BaseModel):
    """反思记忆项（持久化到长期记忆）"""

    memory_id: str = Field(
        default_factory=lambda: f"refl_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    category: MemoryCategory = Field(
        default=MemoryCategory.EXTENDED_REFLECTION, description="记忆分类"
    )

    # 触发信息
    trigger_type: ReflectionTriggerType = Field(description="触发类型")
    trigger_reason: str = Field(description="触发原因")
    trigger_confidence: float = Field(ge=0.0, le=1.0, description="触发置信度")
    step_index: int = Field(description="推理步骤索引")
    task_type: str = Field(description="任务类型")

    # 状态快照
    context_snapshot: dict[str, Any] = Field(default_factory=dict, description="状态快照")

    # 反思过程
    reflection_issues: list[str] = Field(default_factory=list, description="发现的问题")
    reflection_severity: ReflectionSeverity = Field(
        default=ReflectionSeverity.LOW, description="问题严重程度"
    )
    reflection_suggestion: str | None = Field(default=None, description="修正建议")

    # 验证结果
    verification_triggered: bool = Field(default=False, description="是否触发验证")
    verification_result: str | None = Field(default=None, description="验证结果")
    verification_resolution: str | None = Field(default=None, description="解决方案")

    # 最终结果（元学习标签）
    outcome: ReflectionOutcome = Field(description="反思结果")
    learning_value: LearningValue = Field(description="元学习价值")

    # 元数据
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str = Field(default="")
    session_id: str = Field(default="")


class MetaLearningSample(BaseModel):
    """元学习训练样本"""

    sample_id: str = Field(
        default_factory=lambda: f"ml_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    # 输入特征
    context_snapshot: dict[str, Any] = Field(description="状态快照")
    step_index: int = Field(description="步骤索引")
    task_type: str = Field(description="任务类型")
    recent_thoughts: list[str] = Field(default_factory=list, description="最近推理")

    # 输出标签
    should_reflect: bool = Field(description="是否应该反思")
    reflect_reason: str | None = Field(default=None, description="反思原因")
    reflect_confidence: float | None = Field(default=None, description="反思置信度")

    # 学习标签
    outcome: ReflectionOutcome = Field(description="实际结果")
    was_correct: bool = Field(description="反思判断是否正确")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 短期记忆类型
# ============================================================================


class ShortTermMemoryItem(BaseModel):
    """短期记忆项
    
    语义分类和话题标签由智能体判断后传入，而非脚本内部关键词匹配。
    """

    item_id: str
    content: str
    bucket_type: SemanticBucketType  # 语义桶类型（智能体指定）
    topic_label: str = ""             # 话题标签（智能体指定，用于聚合）
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5)
    source_turn: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ShortTermMemoryBucket(BaseModel):
    """短期记忆语义分类桶"""

    bucket_type: SemanticBucketType
    items: list[ShortTermMemoryItem] = Field(default_factory=list)
    capacity: int = Field(default=20)
    priority: float = Field(ge=0.0, le=1.0, default=0.5)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class ExtractionTrigger(BaseModel):
    """提炼触发条件"""

    trigger_type: str  # capacity, time_interval, pattern_detected, user_request
    threshold: float
    current_value: float
    triggered: bool = Field(default=False)


# ============================================================================
# 上下文包类型
# ============================================================================


class QualityScores(BaseModel):
    """六维质量分数"""

    relevance: float = Field(ge=0.0, le=1.0, default=0.5)
    completeness: float = Field(ge=0.0, le=1.0, default=0.5)
    coherence: float = Field(ge=0.0, le=1.0, default=0.5)
    timeliness: float = Field(ge=0.0, le=1.0, default=0.5)
    diversity: float = Field(ge=0.0, le=1.0, default=0.5)
    actionability: float = Field(ge=0.0, le=1.0, default=0.5)
    overall_score: float = Field(ge=0.0, le=1.0, default=0.5)


class WeightConfig(BaseModel):
    """权重配置"""

    relevance_weight: float = Field(ge=0.0, le=1.0, default=0.20)
    completeness_weight: float = Field(ge=0.0, le=1.0, default=0.15)
    coherence_weight: float = Field(ge=0.0, le=1.0, default=0.15)
    timeliness_weight: float = Field(ge=0.0, le=1.0, default=0.15)
    diversity_weight: float = Field(ge=0.0, le=1.0, default=0.15)
    actionability_weight: float = Field(ge=0.0, le=1.0, default=0.20)


class ContextPackage(BaseModel):
    """上下文包"""

    package_id: str
    task_context: dict[str, Any]
    user_state: dict[str, Any]
    activated_memories: list[str]
    quality_scores: QualityScores
    weight_config: WeightConfig
    scenario: ScenarioType
    phase: PhaseType
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 用户画像类型
# ============================================================================


class TechnicalBackground(BaseModel):
    """技术背景"""

    domains: list[str] = Field(default_factory=list)
    expertise_level: str = Field(default="intermediate")


class CommunicationStyle(BaseModel):
    """沟通风格"""

    style: str = Field(default="balanced")
    preference: str = Field(default="detailed")
    dislike: list[str] = Field(default_factory=list)


class DecisionPattern(BaseModel):
    """决策模式"""

    type: str = Field(default="balanced")
    requires: str = Field(default="sufficient_evidence")
    focus: str = Field(default="balanced")


class UserProfileData(BaseModel):
    """用户画像数据"""

    identity: list[str] = Field(default_factory=list)
    technical_background: TechnicalBackground = Field(default_factory=TechnicalBackground)
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)
    decision_pattern: DecisionPattern = Field(default_factory=DecisionPattern)
    knowledge_blindspots: list[str] = Field(default_factory=list)
    version: int = Field(default=1)


class UserProfileMemory(BaseModel):
    """用户画像记忆"""

    memory_id: str
    memory_type: MemoryType = MemoryType.USER_PROFILE
    user_id: str
    data: UserProfileData
    heat: HeatMixin = Field(default_factory=HeatMixin)
    timestamp: TimestampMixin = Field(default_factory=TimestampMixin)


# ============================================================================
# 程序性记忆类型
# ============================================================================


class DecisionPatternRecord(BaseModel):
    """决策模式记录"""

    pattern_id: str
    trigger_condition: str
    workflow: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    usage_count: int = Field(default=0)
    success_rate: float = Field(ge=0.0, le=1.0, default=0.5)


class ProblemSolvingStrategy(BaseModel):
    """问题解决策略"""

    problem_type: str
    preferred_approach: str
    tools_preferred: list[str] = Field(default_factory=list)


class ToolUsageRecord(BaseModel):
    """工具使用记录"""

    record_id: str
    timestamp: datetime
    task_type: str
    tool_name: str
    effectiveness_score: float = Field(ge=0.0, le=1.0)
    outcome: str
    user_feedback: Optional[float] = None
    # 状态关联字段（P0: 工具调用状态关联）
    checkpoint_id: Optional[str] = None      # 关联的状态快照ID
    phase: Optional[str] = None              # 调用时的阶段
    scenario: Optional[str] = None           # 调用时的场景
    user_state: Optional[str] = None         # 调用时的用户状态


class ToolOptimalContext(BaseModel):
    """工具最优场景"""

    optimal_scenarios: list[dict[str, Any]]
    avoid_scenarios: list[dict[str, Any]]


class ToolCombinationPattern(BaseModel):
    """工具组合模式"""

    sequence: list[str]
    task_pattern: str
    effectiveness_avg: float
    usage_count: int


class NeuroticismTendency(BaseModel):
    """神经质倾向"""

    score: float = Field(ge=-1.0, le=1.0, default=0.0)
    derived_from: list[str] = Field(default_factory=list)


class ProceduralMemoryData(BaseModel):
    """程序性记忆数据"""

    decision_patterns: list[DecisionPatternRecord] = Field(default_factory=list)
    problem_solving_strategies: list[ProblemSolvingStrategy] = Field(default_factory=list)
    tool_usage_patterns: dict[str, Any] = Field(default_factory=dict)
    tool_effectiveness_records: list[ToolUsageRecord] = Field(default_factory=list)
    tool_optimal_contexts: dict[str, ToolOptimalContext] = Field(default_factory=dict)
    tool_combination_patterns: list[ToolCombinationPattern] = Field(default_factory=list)
    operation_preferences: dict[str, Any] = Field(default_factory=dict)
    neuroticism_tendency: NeuroticismTendency = Field(default_factory=NeuroticismTendency)
    cross_category_insights: list[dict[str, Any]] = Field(default_factory=list)


class ProceduralMemory(BaseModel):
    """程序性记忆"""

    memory_id: str
    memory_type: MemoryType = MemoryType.PROCEDURAL
    user_id: str
    data: ProceduralMemoryData
    heat: HeatMixin = Field(default_factory=HeatMixin)
    timestamp: TimestampMixin = Field(default_factory=TimestampMixin)


# ============================================================================
# 叙事记忆类型
# ============================================================================


class GrowthMilestone(BaseModel):
    """成长节点"""

    timestamp: datetime
    event: str
    significance: str
    importance_score: float = Field(ge=0.0, le=1.0)


class IdentityEvolution(BaseModel):
    """身份演化"""

    timestamp: datetime
    from_identity: str
    to_identity: str
    trigger: str


class NarrativeMemoryData(BaseModel):
    """叙事记忆数据"""

    current_identity: list[str] = Field(default_factory=list)
    growth_milestones: list[GrowthMilestone] = Field(default_factory=list)
    identity_evolution: list[IdentityEvolution] = Field(default_factory=list)
    continuous_concerns: list[dict[str, Any]] = Field(default_factory=list)
    narrative_content: str = Field(default="")


class NarrativeMemory(BaseModel):
    """叙事记忆"""

    memory_id: str
    memory_type: MemoryType = MemoryType.NARRATIVE
    user_id: str
    data: NarrativeMemoryData
    heat: HeatMixin = Field(default_factory=HeatMixin)
    timestamp: TimestampMixin = Field(default_factory=TimestampMixin)


# ============================================================================
# 语义记忆类型
# ============================================================================


class ConceptDefinition(BaseModel):
    """概念定义"""

    concept: str
    definition: str
    attributes: dict[str, str]
    related_concepts: list[str]
    usage_count: int = Field(default=0)
    confidence: float = Field(ge=0.0, le=1.0)


class KnowledgeEntity(BaseModel):
    """知识实体"""

    entity: str
    entity_type: str
    relationships: list[dict[str, Any]]


class Principle(BaseModel):
    """原则"""

    principle: str
    applicability: str
    evidence_support: float


class SemanticMemoryData(BaseModel):
    """语义记忆数据"""

    core_concepts: list[ConceptDefinition] = Field(default_factory=list)
    knowledge_entities: list[KnowledgeEntity] = Field(default_factory=list)
    principles: list[Principle] = Field(default_factory=list)


class SemanticMemory(BaseModel):
    """语义记忆"""

    memory_id: str
    memory_type: MemoryType = MemoryType.SEMANTIC
    user_id: str
    data: SemanticMemoryData
    heat: HeatMixin = Field(default_factory=HeatMixin)
    timestamp: TimestampMixin = Field(default_factory=TimestampMixin)


# ============================================================================
# 情感记忆类型
# ============================================================================


class EmotionState(BaseModel):
    """情绪状态"""

    timestamp: datetime
    emotion_type: str
    intensity: float = Field(ge=0.0, le=1.0)
    trigger_context: str
    topic: str
    decay_factor: float = Field(default=0.98)


class AttitudeTendency(BaseModel):
    """态度倾向"""

    topic: str
    attitude: str
    direction: str
    confidence: float


class SatisfactionRecord(BaseModel):
    """满意度记录"""

    timestamp: datetime
    satisfaction_level: float = Field(ge=0.0, le=1.0)
    trigger_factors: list[str]
    concerns: list[str]
    overall_progress: str


class EmotionalMemoryData(BaseModel):
    """情感记忆数据"""

    emotion_states: list[EmotionState] = Field(default_factory=list)
    attitude_tendencies: list[AttitudeTendency] = Field(default_factory=list)
    satisfaction_records: list[SatisfactionRecord] = Field(default_factory=list)


class EmotionalMemory(BaseModel):
    """情感记忆"""

    memory_id: str
    memory_type: MemoryType = MemoryType.EMOTIONAL
    user_id: str
    data: EmotionalMemoryData
    heat: HeatMixin = Field(default_factory=HeatMixin)
    timestamp: TimestampMixin = Field(default_factory=TimestampMixin)


# ============================================================================
# 感知记忆类型
# ============================================================================


class ConversationTurn(BaseModel):
    """对话轮次"""

    role: str
    content: str
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskState(BaseModel):
    """任务状态"""

    current_topic: str = Field(default="")
    pending_questions: list[str] = Field(default_factory=list)
    context_anchors: list[str] = Field(default_factory=list)


class TemporaryContext(BaseModel):
    """临时上下文"""

    mentioned_concepts: list[str] = Field(default_factory=list)
    implicit_assumptions: list[str] = Field(default_factory=list)


class PerceptionMemoryData(BaseModel):
    """感知记忆数据"""

    session_id: str
    conversation_history: list[ConversationTurn] = Field(default_factory=list)
    task_state: TaskState = Field(default_factory=TaskState)
    temporary_context: TemporaryContext = Field(default_factory=TemporaryContext)


class PerceptionMemory(BaseModel):
    """感知记忆"""

    memory_id: str
    user_id: str
    data: PerceptionMemoryData
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


# ============================================================================
# 情境感知类型
# ============================================================================


class CurrentTask(BaseModel):
    """当前任务"""

    task_type: TaskType
    task_complexity: str = Field(default="medium")
    task_phase: str = Field(default="exploration")
    implicit_requirements: list[str] = Field(default_factory=list)


class UserCurrentState(BaseModel):
    """用户当前状态"""

    technical_level: str = Field(default="intermediate")
    current_focus: str = Field(default="")
    mental_model: str = Field(default="")
    decision_style: str = Field(default="balanced")


class ContextAnchors(BaseModel):
    """上下文锚点"""

    temporal: str = Field(default="")
    semantic: str = Field(default="")
    narrative: str = Field(default="")
    emotional: str = Field(default="")


class SituationAwareness(BaseModel):
    """情境感知"""

    timestamp: datetime = Field(default_factory=datetime.now)
    current_task: CurrentTask
    user_current_state: UserCurrentState
    context_anchors: ContextAnchors


# ============================================================================
# 激活相关类型
# ============================================================================


class ActivationSource(BaseModel):
    """激活来源"""

    dimension: TriggerDimension
    score: float = Field(ge=0.0, le=1.0)


class ActivatedMemory(BaseModel):
    """激活的记忆"""

    memory_id: str
    memory_type: MemoryType
    content_summary: str
    triggered_by: list[TriggerDimension]
    relevance_score: float = Field(ge=0.0, le=1.0)
    heat_level: HeatLevel
    conflicts: list[str] = Field(default_factory=list)
    activation_sources: list[ActivationSource] = Field(default_factory=list)


class ActivationResult(BaseModel):
    """激活结果"""

    activated_memories: list[ActivatedMemory]
    total_count: int
    unique_count: int
    conflicts_detected: int
    activation_coverage: list[TriggerDimension]


# ============================================================================
# 上下文重构类型
# ============================================================================


class TaskContextLayer(BaseModel):
    """任务上下文层"""

    current_task: str
    task_phase: str
    implicit_requirements: list[str]


class UserStateLayer(BaseModel):
    """用户状态层"""

    user_profile_core: dict[str, Any]
    current_focus: str
    decision_style: str
    neuroticism_tendency: float


class ActivatedExperiencesLayer(BaseModel):
    """激活经验层"""

    relevant_patterns: list[dict[str, Any]]
    success_stories: list[dict[str, Any]]
    failure_lessons: list[dict[str, Any]]
    tool_recommendations: list[dict[str, Any]]


class KnowledgeContextLayer(BaseModel):
    """知识上下文层"""

    key_concepts: list[dict[str, Any]]
    concept_relations: list[dict[str, Any]]
    principles: list[str]


class EmotionalContextLayer(BaseModel):
    """情感上下文层"""

    current_emotion: str
    emotional_trend: str
    satisfaction_level: float


class NarrativeAnchorLayer(BaseModel):
    """叙事锚点层"""

    growth_milestones: list[dict[str, Any]]
    identity_evolution: list[str]
    continuous_concerns: list[str]


class ReconstructedContext(BaseModel):
    """重构上下文"""

    task_context: TaskContextLayer
    user_state: UserStateLayer
    activated_experiences: ActivatedExperiencesLayer
    knowledge_context: KnowledgeContextLayer
    emotional_context: EmotionalContextLayer
    narrative_anchor: NarrativeAnchorLayer
    conflicts_handled: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 洞察信号类型
# ============================================================================


class FitScores(BaseModel):
    """契合度分数"""

    user_profile: float = Field(ge=0.0, le=1.0)
    procedural: float = Field(ge=0.0, le=1.0)
    context: float = Field(ge=0.0, le=1.0)
    emotional: float = Field(ge=0.0, le=1.0)
    overall: float = Field(ge=0.0, le=1.0)


class DecisionSupportSignal(BaseModel):
    """决策支持信号"""

    signal_id: str
    signal_type: SignalType = SignalType.DECISION_SUPPORT
    decision_point: str
    options: list[str]
    recommendation: str
    trade_offs: str
    confidence: float = Field(ge=0.0, le=1.0)
    fit_scores: FitScores


class ToolRecommendationSignal(BaseModel):
    """工具推荐信号"""

    signal_id: str
    signal_type: SignalType = SignalType.TOOL_RECOMMENDATION
    recommended_tool: str
    reasons: list[str]
    combination_opportunity: Optional[str] = None
    cautions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    fit_scores: FitScores


class RiskAlertSignal(BaseModel):
    """风险提示信号"""

    signal_id: str
    signal_type: SignalType = SignalType.RISK_ALERT
    risk_type: str
    risk_description: str
    potential_impact: str
    mitigation: str
    urgency: str
    confidence: float = Field(ge=0.0, le=1.0)
    fit_scores: FitScores


class TimingHintSignal(BaseModel):
    """时机提示信号"""

    signal_id: str
    signal_type: SignalType = SignalType.TIMING_HINT
    timing_type: str
    hint: str
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    fit_scores: FitScores


class InsightSignalUnion(BaseModel):
    """洞察信号联合类型"""

    signal: (
        DecisionSupportSignal
        | ToolRecommendationSignal
        | RiskAlertSignal
        | TimingHintSignal
    )


class ContextEnhancement(BaseModel):
    """上下文增强"""

    insight_signals: list[InsightSignalUnion]
    total_signals: int
    total_fit_score: float


# ============================================================================
# 冲突解决类型
# ============================================================================


class MemoryConflict(BaseModel):
    """记忆冲突"""

    conflict_id: str
    conflict_type: ConflictType
    memory_ids: list[str]
    description: str
    detected_at: datetime = Field(default_factory=datetime.now)


class ConflictResolution(BaseModel):
    """冲突解决结果"""

    conflict: MemoryConflict
    resolution_mode: ResolutionMode
    logic_score: float
    neuroticism_score: float
    winner_memory_id: str
    alternative_memory_id: Optional[str] = None
    reasoning: str


# ============================================================================
# 状态捕捉类型
# ============================================================================


class ModuleState(BaseModel):
    """模块状态"""

    module_name: str
    status: str
    last_update: datetime = Field(default_factory=datetime.now)
    metrics: dict[str, Any] = Field(default_factory=dict)


class GlobalState(BaseModel):
    """全局状态"""

    state_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str
    module_states: dict[str, ModuleState]
    cross_module_signals: dict[str, Any] = Field(default_factory=dict)


class AsyncTask(BaseModel):
    """异步任务"""

    task_id: str
    task_type: str
    payload: dict[str, Any]
    priority: str = Field(default="medium")
    submitted_at: datetime = Field(default_factory=datetime.now)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)


# ============================================================================
# 状态同步类型（LangGraph集成）
# ============================================================================


class StateEventType(str, Enum):
    """状态事件类型"""

    STATE_CHANGE = "state_change"           # 通用状态变化
    PHASE_CHANGE = "phase_change"           # 阶段变化
    TASK_COMPLETE = "task_complete"         # 任务完成
    TASK_SWITCH = "task_switch"             # 任务切换
    CHECKPOINT_CREATED = "checkpoint_created"  # 检查点创建
    CHECKPOINT_RESTORED = "checkpoint_restored"  # 检查点恢复
    USER_STATE_CHANGE = "user_state_change"  # 用户状态变化


class CheckpointRecord(BaseModel):
    """检查点记录"""

    checkpoint_id: str
    thread_id: str
    node_name: str                          # 创建检查点的节点名
    timestamp: datetime = Field(default_factory=datetime.now)
    state_hash: str                         # 状态哈希（用于快速比较）
    state_diff: dict[str, Any] = Field(default_factory=dict)  # 增量差异
    metadata: dict[str, Any] = Field(default_factory=dict)
    ttl_hours: int = Field(default=168)     # TTL，默认7天


class StateChangeEvent(BaseModel):
    """状态变化事件"""

    event_id: str
    event_type: StateEventType
    checkpoint_id: str
    thread_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    changes: dict[str, Any] = Field(default_factory=dict)    # 变化内容
    previous_state: dict[str, Any] = Field(default_factory=dict)  # 变化前状态
    current_state: dict[str, Any] = Field(default_factory=dict)   # 变化后状态
    metadata: dict[str, Any] = Field(default_factory=dict)


class StateSubscription(BaseModel):
    """状态订阅配置"""

    subscription_id: str
    event_types: list[StateEventType]       # 订阅的事件类型
    callback_name: str                      # 回调函数名（用于序列化）
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 洞察池类型
# ============================================================================


class InsightSignal(BaseModel):
    """洞察信号"""

    signal_id: str
    signal_type: InsightType
    confidence: float = Field(ge=0.0, le=1.0)
    data: dict[str, Any] = Field(default_factory=dict)
    raw_observation: str
    created_at: datetime = Field(default_factory=datetime.now)


class Insight(BaseModel):
    """洞察"""

    insight_id: str
    insight_type: InsightType
    title: str
    content: str
    priority: InsightPriority
    created_at: datetime = Field(default_factory=datetime.now)
    signal_strength: SignalStrength = SignalStrength.MODERATE
    affected_memories: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    actionable: bool = Field(default=False)
    actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InsightPoolData(BaseModel):
    """洞察池数据"""

    active_insights: list[Insight] = Field(default_factory=list)
    pending_insights: list[Insight] = Field(default_factory=list)
    archived_insights: list[Insight] = Field(default_factory=list)
    max_active: int = Field(default=5)


class UserDecision(BaseModel):
    """用户决策"""

    decision_id: str
    decision_type: DecisionType
    context: str
    chosen_option: str
    alternative_options: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 场景识别类型
# ============================================================================


class SceneContext(BaseModel):
    """场景上下文"""

    scenario: ScenarioType
    phase: PhaseType
    user_state: UserStateType
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    indicators: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class GlobalStateSnapshot(BaseModel):
    """全局状态快照"""

    snapshot_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    current_task: str
    task_phase: str
    user_intent: str
    active_memories: list[str] = Field(default_factory=list)
    decision_context: dict[str, Any] = Field(default_factory=dict)
    emotion_state: str = Field(default="neutral")
    mental_model: str = Field(default="")
    conversation_turn: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 冲突解决扩展类型
# ============================================================================


class ConflictSeverity(str, Enum):
    """冲突严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryConflictExtended(BaseModel):
    """扩展的记忆冲突"""

    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity = ConflictSeverity.MEDIUM
    involved_memories: list[str] = Field(default_factory=list)
    description: str
    detected_at: datetime = Field(default_factory=datetime.now)
    resolution_mode: ResolutionMode = ResolutionMode.BALANCED


class ResolutionResult(BaseModel):
    """解决结果"""

    conflict_id: str
    resolution_mode: ResolutionMode
    winning_memory: str
    losing_memories: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    rationale: str = ""
    user_required: bool = Field(default=False)
    alternatives: list[str] = Field(default_factory=list)


# ============================================================================
# 长期记忆统一容器
# ============================================================================


class LongTermMemoryContainer(BaseModel):
    """长期记忆统一容器"""

    user_id: str
    user_profile: Optional[UserProfileMemory] = None
    procedural: Optional[ProceduralMemory] = None
    narrative: Optional[NarrativeMemory] = None
    semantic: Optional[SemanticMemory] = None
    emotional: Optional[EmotionalMemory] = None
    # 反思记忆索引（P0: 链式推理增强）
    reflection_index: list[dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 短期记忆到长期记忆的映射工具
# ============================================================================


class ExtractionMapping:
    """
    提炼映射工具
    
    定义短期记忆语义桶到长期记忆7分类的映射关系
    """
    
    # 核心映射表
    BUCKET_TO_CATEGORY: dict[SemanticBucketType, list[str]] = {
        # 用户意图 → 核心偏好（首选）/ 核心身份（备选）
        SemanticBucketType.USER_INTENT: [
            MemoryCategory.CORE_PREFERENCE.value,
            MemoryCategory.CORE_IDENTITY.value,
        ],
        # 决策上下文 → 上下文重构器（非线性激活），不存储到长期记忆
        SemanticBucketType.DECISION_CONTEXT: [
            "CONTEXT_ACTIVATION",  # 特殊标记：传递给上下文重构器
        ],
        # 任务上下文 → 扩展叙事 + 同时用于上下文激活
        SemanticBucketType.TASK_CONTEXT: [
            MemoryCategory.EXTENDED_NARRATIVE.value,
            "CONTEXT_ACTIVATION",  # 同时传递给上下文重构器
        ],
        # 知识缺口 → 扩展知识
        SemanticBucketType.KNOWLEDGE_GAP: [
            MemoryCategory.EXTENDED_KNOWLEDGE.value,
        ],
        # 情感痕迹 → 扩展情感
        SemanticBucketType.EMOTIONAL_TRACE: [
            MemoryCategory.EXTENDED_EMOTION.value,
        ],
    }
    
    # 分类层级
    CORE_CATEGORIES: set[MemoryCategory] = {
        MemoryCategory.CORE_IDENTITY,
        MemoryCategory.CORE_PREFERENCE,
        MemoryCategory.CORE_SKILL,
    }
    
    EXTENDED_CATEGORIES: set[MemoryCategory] = {
        MemoryCategory.EXTENDED_BEHAVIOR,
        MemoryCategory.EXTENDED_EMOTION,
        MemoryCategory.EXTENDED_KNOWLEDGE,
        MemoryCategory.EXTENDED_NARRATIVE,
    }
    
    @classmethod
    def get_target_category(
        cls,
        bucket_type: SemanticBucketType,
        confidence: float = 0.5,
    ) -> str:
        """
        根据桶类型和置信度确定目标分类
        
        Args:
            bucket_type: 语义桶类型
            confidence: 置信度（用于选择首选或备选分类）
            
        Returns:
            目标记忆分类（字符串，可能是 MemoryCategory 或特殊标记）
        """
        categories = cls.BUCKET_TO_CATEGORY.get(bucket_type, [])
        
        if not categories:
            # 默认归类为扩展叙事
            return MemoryCategory.EXTENDED_NARRATIVE.value
        
        # 高置信度选首选，低置信度选备选（如果有）
        if confidence >= 0.7 or len(categories) == 1:
            return categories[0]
        else:
            return categories[-1]
    
    @classmethod
    def is_for_context_activation(cls, target: str) -> bool:
        """判断是否需要传递给上下文重构器"""
        return target == "CONTEXT_ACTIVATION"
    
    @classmethod
    def is_for_long_term_storage(cls, target: str) -> bool:
        """判断是否需要存储到长期记忆"""
        return target in [c.value for c in cls.CORE_CATEGORIES | cls.EXTENDED_CATEGORIES]
    
    @classmethod
    def is_core_category(cls, category: MemoryCategory) -> bool:
        """判断是否为核心层分类"""
        return category in cls.CORE_CATEGORIES
    
    @classmethod
    def is_extended_category(cls, category: MemoryCategory) -> bool:
        """判断是否为扩展层分类"""
        return category in cls.EXTENDED_CATEGORIES


# ============================================================================
# 导出类型
# ============================================================================


__all__ = [
    # 枚举
    "MemoryType",
    "MemoryCategory",
    "SemanticBucketType",
    "QualityDimension",
    "ScenarioType",
    "PhaseType",
    "UserStateType",
    "HeatLevel",
    "ConflictType",
    "ResolutionMode",
    "TriggerDimension",
    "SignalType",
    "InsightType",
    "InsightPriority",
    "SignalStrength",
    "DecisionType",
    "TaskType",
    "ConflictSeverity",
    # 反思类型
    "ReflectionTriggerType",
    "ReflectionOutcome",
    "LearningValue",
    "ReflectionSeverity",
    "ReflectionSignal",
    "ReasoningStepWithReflection",
    "ReflectionTriggerRecord",
    "ReflectionProcessResult",
    "VerificationResult",
    "ReflectionMemoryItem",
    "MetaLearningSample",
    # 映射工具
    "ExtractionMapping",
    # 混入
    "TimestampMixin",
    "ConfidenceMixin",
    "HeatMixin",
    # 短期记忆
    "ShortTermMemoryItem",
    "ShortTermMemoryBucket",
    "ExtractionTrigger",
    # 上下文包
    "QualityScores",
    "WeightConfig",
    "ContextPackage",
    # 用户画像
    "TechnicalBackground",
    "CommunicationStyle",
    "DecisionPattern",
    "UserProfileData",
    "UserProfileMemory",
    # 程序性记忆
    "DecisionPatternRecord",
    "ProblemSolvingStrategy",
    "ToolUsageRecord",
    "ToolOptimalContext",
    "ToolCombinationPattern",
    "NeuroticismTendency",
    "ProceduralMemoryData",
    "ProceduralMemory",
    # 叙事记忆
    "GrowthMilestone",
    "IdentityEvolution",
    "NarrativeMemoryData",
    "NarrativeMemory",
    # 语义记忆
    "ConceptDefinition",
    "KnowledgeEntity",
    "Principle",
    "SemanticMemoryData",
    "SemanticMemory",
    # 情感记忆
    "EmotionState",
    "AttitudeTendency",
    "SatisfactionRecord",
    "EmotionalMemoryData",
    "EmotionalMemory",
    # 感知记忆
    "ConversationTurn",
    "TaskState",
    "TemporaryContext",
    "PerceptionMemoryData",
    "PerceptionMemory",
    # 情境感知
    "CurrentTask",
    "UserCurrentState",
    "ContextAnchors",
    "SituationAwareness",
    # 激活
    "ActivationSource",
    "ActivatedMemory",
    "ActivationResult",
    # 上下文重构
    "TaskContextLayer",
    "UserStateLayer",
    "ActivatedExperiencesLayer",
    "KnowledgeContextLayer",
    "EmotionalContextLayer",
    "NarrativeAnchorLayer",
    "ReconstructedContext",
    # 洞察信号
    "FitScores",
    "DecisionSupportSignal",
    "ToolRecommendationSignal",
    "RiskAlertSignal",
    "TimingHintSignal",
    "InsightSignalUnion",
    "ContextEnhancement",
    "InsightSignal",
    "Insight",
    "InsightPoolData",
    "UserDecision",
    # 状态同步（LangGraph集成）
    "StateEventType",
    "CheckpointRecord",
    "StateChangeEvent",
    "StateSubscription",
    # 冲突
    "MemoryConflict",
    "ConflictResolution",
    "MemoryConflictExtended",
    "ResolutionResult",
    # 状态
    "ModuleState",
    "GlobalState",
    "AsyncTask",
    "GlobalStateSnapshot",
    "SceneContext",
    # 容器
    "LongTermMemoryContainer",
]

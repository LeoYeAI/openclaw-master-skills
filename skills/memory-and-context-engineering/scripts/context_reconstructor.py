"""
Agent Memory System - 上下文重构器

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
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

import uuid
from datetime import datetime, timedelta
from typing import Any, TYPE_CHECKING

from .types import (
    QualityDimension,
    QualityScores,
    WeightConfig,
    ContextPackage,
    ScenarioType,
    PhaseType,
    UserStateType,
    TaskType,
    TriggerDimension,
    MemoryType,
    HeatLevel,
    ActivationSource,
    ActivatedMemory,
    ActivationResult,
    ReconstructedContext,
    TaskContextLayer,
    UserStateLayer,
    ActivatedExperiencesLayer,
    KnowledgeContextLayer,
    EmotionalContextLayer,
    NarrativeAnchorLayer,
    SituationAwareness,
    LongTermMemoryContainer,
    UserProfileMemory,
    ProceduralMemory,
    NarrativeMemory,
    SemanticMemory,
    EmotionalMemory,
    StateEventType,
)

# 避免循环导入
if TYPE_CHECKING:
    from .state_capture import GlobalStateCapture, StateChangeEvent


class QualityEvaluator:
    """
    六维质量评估器

    评估上下文质量的六个维度：相关性、完整性、连贯性、时效性、多样性、可操作性
    """

    def __init__(self) -> None:
        """初始化质量评估器"""
        self._dimension_weights: dict[QualityDimension, float] = {
            QualityDimension.RELEVANCE: 0.25,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.COHERENCE: 0.15,
            QualityDimension.TIMELINESS: 0.15,
            QualityDimension.DIVERSITY: 0.15,
            QualityDimension.ACTIONABILITY: 0.15,
        }

    def evaluate(
        self,
        activated_memories: list[ActivatedMemory],
        situation: SituationAwareness,
    ) -> QualityScores:
        """
        评估上下文质量

        Args:
            activated_memories: 激活的记忆列表
            situation: 当前情境

        Returns:
            质量分数
        """
        # 相关性：与当前任务的相关程度
        relevance: float = self._evaluate_relevance(activated_memories, situation)

        # 完整性：信息覆盖的完整程度
        completeness: float = self._evaluate_completeness(activated_memories)

        # 连贯性：信息间的逻辑连贯性
        coherence: float = self._evaluate_coherence(activated_memories)

        # 时效性：信息的时效程度
        timeliness: float = self._evaluate_timeliness(activated_memories)

        # 多样性：信息来源的多样性
        diversity: float = self._evaluate_diversity(activated_memories)

        # 可操作性：转化为行动的可能性
        actionability: float = self._evaluate_actionability(activated_memories, situation)

        # 综合分数
        overall: float = (
            relevance * self._dimension_weights[QualityDimension.RELEVANCE]
            + completeness * self._dimension_weights[QualityDimension.COMPLETENESS]
            + coherence * self._dimension_weights[QualityDimension.COHERENCE]
            + timeliness * self._dimension_weights[QualityDimension.TIMELINESS]
            + diversity * self._dimension_weights[QualityDimension.DIVERSITY]
            + actionability * self._dimension_weights[QualityDimension.ACTIONABILITY]
        )

        return QualityScores(
            relevance=relevance,
            completeness=completeness,
            coherence=coherence,
            timeliness=timeliness,
            diversity=diversity,
            actionability=actionability,
            overall_score=overall,
        )

    def _evaluate_relevance(
        self,
        memories: list[ActivatedMemory],
        situation: SituationAwareness,
    ) -> float:
        """评估相关性"""
        if not memories:
            return 0.0

        # 基于激活分数计算平均相关性
        total_relevance: float = sum(m.relevance_score for m in memories)
        avg_relevance: float = total_relevance / len(memories)

        # 根据任务类型调整
        task_type: TaskType = situation.current_task.task_type
        if task_type in [TaskType.TECHNICAL_IMPLEMENTATION, TaskType.CODE_DEBUGGING]:
            # 技术任务需要更高的相关性
            return min(1.0, avg_relevance * 1.1)
        elif task_type in [TaskType.BRAINSTORMING, TaskType.CREATIVE_DESIGN]:
            # 创意任务可以接受较低的相关性
            return avg_relevance

        return avg_relevance

    def _evaluate_completeness(self, memories: list[ActivatedMemory]) -> float:
        """评估完整性"""
        if not memories:
            return 0.0

        # 检查覆盖的记忆类型
        covered_types: set[MemoryType] = {m.memory_type for m in memories}

        # 期望覆盖的类型
        expected_types: set[MemoryType] = {
            MemoryType.USER_PROFILE,
            MemoryType.PROCEDURAL,
            MemoryType.SEMANTIC,
        }

        coverage: float = len(covered_types & expected_types) / len(expected_types)
        return coverage

    def _evaluate_coherence(self, memories: list[ActivatedMemory]) -> float:
        """评估连贯性"""
        if len(memories) < 2:
            return 1.0

        # 检查激活维度的一致性
        all_dimensions: list[TriggerDimension] = []
        for m in memories:
            all_dimensions.extend(m.triggered_by)

        if not all_dimensions:
            return 0.5

        # 计算维度重叠度
        dimension_counts: dict[TriggerDimension, int] = {}
        for dim in all_dimensions:
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

        # 如果大部分记忆共享相同的触发维度，则连贯性较高
        max_overlap: int = max(dimension_counts.values())
        coherence: float = max_overlap / len(memories)

        return coherence

    def _evaluate_timeliness(self, memories: list[ActivatedMemory]) -> float:
        """评估时效性"""
        if not memories:
            return 0.0

        # 基于热度层级计算时效性
        timeliness_scores: dict[HeatLevel, float] = {
            HeatLevel.HOT: 1.0,
            HeatLevel.WARM: 0.7,
            HeatLevel.COLD: 0.4,
        }

        total_score: float = 0.0
        for m in memories:
            total_score += timeliness_scores.get(m.heat_level, 0.5)

        return total_score / len(memories)

    def _evaluate_diversity(self, memories: list[ActivatedMemory]) -> float:
        """评估多样性"""
        if len(memories) < 2:
            return 0.5

        # 检查来源维度的多样性
        all_dimensions: set[TriggerDimension] = set()
        for m in memories:
            all_dimensions.update(m.triggered_by)

        # 六维激活器的理论最大维度数
        max_dimensions: int = 6
        diversity: float = len(all_dimensions) / max_dimensions

        return diversity

    def _evaluate_actionability(
        self,
        memories: list[ActivatedMemory],
        situation: SituationAwareness,
    ) -> float:
        """评估可操作性"""
        if not memories:
            return 0.0

        # 检查是否有程序性记忆（通常更具可操作性）
        procedural_count: int = sum(
            1 for m in memories if m.memory_type == MemoryType.PROCEDURAL
        )

        # 检查任务阶段（实现阶段需要更高的可操作性）
        phase: str = situation.current_task.task_phase
        phase_multiplier: float = 1.2 if phase in ["implementation", "verification"] else 1.0

        actionability: float = min(1.0, procedural_count / 3) * phase_multiplier
        return actionability

    def set_dimension_weights(
        self, weights: dict[QualityDimension, float]
    ) -> None:
        """
        设置维度权重

        Args:
            weights: 维度权重字典
        """
        for dim, weight in weights.items():
            if dim in self._dimension_weights:
                self._dimension_weights[dim] = weight


class WeightAdapter:
    """
    比重适配器

    根据任务类型和场景动态调整权重配置
    """

    def __init__(self) -> None:
        """初始化比重适配器"""
        # 预设权重配置
        self._preset_weights: dict[ScenarioType, WeightConfig] = {
            ScenarioType.CODING: WeightConfig(
                relevance_weight=0.25,
                completeness_weight=0.20,
                coherence_weight=0.15,
                timeliness_weight=0.15,
                diversity_weight=0.10,
                actionability_weight=0.15,
            ),
            ScenarioType.DEBUGGING: WeightConfig(
                relevance_weight=0.30,
                completeness_weight=0.15,
                coherence_weight=0.15,
                timeliness_weight=0.20,
                diversity_weight=0.05,
                actionability_weight=0.15,
            ),
            ScenarioType.DESIGN: WeightConfig(
                relevance_weight=0.15,
                completeness_weight=0.15,
                coherence_weight=0.10,
                timeliness_weight=0.10,
                diversity_weight=0.30,
                actionability_weight=0.20,
            ),
            ScenarioType.ANALYSIS: WeightConfig(
                relevance_weight=0.20,
                completeness_weight=0.25,
                coherence_weight=0.20,
                timeliness_weight=0.10,
                diversity_weight=0.15,
                actionability_weight=0.10,
            ),
            ScenarioType.LEARNING: WeightConfig(
                relevance_weight=0.20,
                completeness_weight=0.20,
                coherence_weight=0.15,
                timeliness_weight=0.10,
                diversity_weight=0.20,
                actionability_weight=0.15,
            ),
            ScenarioType.PLANNING: WeightConfig(
                relevance_weight=0.20,
                completeness_weight=0.20,
                coherence_weight=0.20,
                timeliness_weight=0.15,
                diversity_weight=0.10,
                actionability_weight=0.15,
            ),
            ScenarioType.REVIEW: WeightConfig(
                relevance_weight=0.25,
                completeness_weight=0.20,
                coherence_weight=0.15,
                timeliness_weight=0.20,
                diversity_weight=0.05,
                actionability_weight=0.15,
            ),
        }

        # 当前权重配置
        self._current_config: WeightConfig = WeightConfig()

    def adapt(self, scenario: ScenarioType) -> WeightConfig:
        """
        根据场景适配权重

        Args:
            scenario: 场景类型

        Returns:
            权重配置
        """
        config: WeightConfig | None = self._preset_weights.get(scenario)
        if config:
            self._current_config = config
        return self._current_config

    def adapt_by_task_type(self, task_type: TaskType) -> WeightConfig:
        """
        根据任务类型适配权重

        Args:
            task_type: 任务类型

        Returns:
            权重配置
        """
        # 任务类型到场景类型的映射
        task_to_scenario: dict[TaskType, ScenarioType] = {
            TaskType.TECHNICAL_IMPLEMENTATION: ScenarioType.CODING,
            TaskType.CODE_DEBUGGING: ScenarioType.DEBUGGING,
            TaskType.CREATIVE_DESIGN: ScenarioType.DESIGN,
            TaskType.BRAINSTORMING: ScenarioType.DESIGN,
            TaskType.DATA_ANALYSIS: ScenarioType.ANALYSIS,
            TaskType.PROBLEM_SOLVING: ScenarioType.PLANNING,
            TaskType.PRECISE_CALCULATION: ScenarioType.ANALYSIS,
            TaskType.KNOWLEDGE_QUERY: ScenarioType.LEARNING,
        }

        scenario: ScenarioType = task_to_scenario.get(task_type, ScenarioType.CODING)
        return self.adapt(scenario)

    def get_current_config(self) -> WeightConfig:
        """
        获取当前权重配置

        Returns:
            权重配置
        """
        return self._current_config

    def set_custom_config(self, config: WeightConfig) -> None:
        """
        设置自定义权重配置

        Args:
            config: 权重配置
        """
        self._current_config = config


class MemoryActivator:
    """
    记忆激活器基类

    所有维度激活器的基类
    """

    dimension: TriggerDimension = TriggerDimension.TEMPORAL

    def activate(
        self,
        situation: SituationAwareness,
        memories: LongTermMemoryContainer,
    ) -> list[ActivationSource]:
        """
        激活相关记忆

        Args:
            situation: 当前情境
            memories: 长期记忆容器

        Returns:
            激活来源列表
        """
        raise NotImplementedError


class TemporalActivator(MemoryActivator):
    """时间激活器"""

    dimension = TriggerDimension.TEMPORAL

    def __init__(self) -> None:
        self._time_windows: dict[str, tuple[float, float]] = {
            "immediate": (0, 1),
            "recent": (1, 24),
            "weekly": (24, 168),
            "monthly": (168, 720),
            "archived": (720, float("inf")),
        }
        self._window_weights: dict[str, float] = {
            "immediate": 1.0,
            "recent": 0.85,
            "weekly": 0.70,
            "monthly": 0.55,
            "archived": 0.35,
        }

    def activate(
        self,
        situation: SituationAwareness,
        memories: LongTermMemoryContainer,
    ) -> list[ActivationSource]:
        sources: list[ActivationSource] = []

        if memories.user_profile:
            hours: float = self._hours_since(memories.user_profile.timestamp.updated_at)
            weight: float = self._get_window_weight(hours)
            if weight > 0.5:
                sources.append(ActivationSource(dimension=self.dimension, score=weight))

        if memories.procedural:
            hours_p: float = self._hours_since(memories.procedural.timestamp.updated_at)
            weight_p: float = self._get_window_weight(hours_p)
            if weight_p > 0.5:
                sources.append(ActivationSource(dimension=self.dimension, score=weight_p))

        return sources

    def _hours_since(self, timestamp: datetime) -> float:
        delta = datetime.now() - timestamp
        return delta.total_seconds() / 3600

    def _get_window_weight(self, hours: float) -> float:
        for window_name, (low, high) in self._time_windows.items():
            if low <= hours < high:
                return self._window_weights.get(window_name, 0.5)
        return 0.35


class SemanticActivator(MemoryActivator):
    """语义激活器"""

    dimension = TriggerDimension.SEMANTIC

    def activate(
        self,
        situation: SituationAwareness,
        memories: LongTermMemoryContainer,
    ) -> list[ActivationSource]:
        sources: list[ActivationSource] = []

        task_keywords: list[str] = self._extract_keywords(situation)

        if memories.semantic:
            match_score: float = self._match_concepts(task_keywords, memories.semantic)
            if match_score > 0.5:
                sources.append(ActivationSource(dimension=self.dimension, score=match_score))

        return sources

    def _extract_keywords(self, situation: SituationAwareness) -> list[str]:
        keywords: list[str] = []
        task_desc: str = situation.current_task.task_type.value
        keywords.extend(task_desc.split("_"))
        return keywords

    def _match_concepts(self, keywords: list[str], semantic: SemanticMemory) -> float:
        if not semantic.data.core_concepts:
            return 0.0

        match_count: int = 0
        for concept in semantic.data.core_concepts:
            if concept.concept.lower() in [kw.lower() for kw in keywords]:
                match_count += 1

        return min(1.0, match_count / 3.0)


class ContextualActivator(MemoryActivator):
    """情境激活器"""

    dimension = TriggerDimension.CONTEXTUAL

    def activate(
        self,
        situation: SituationAwareness,
        memories: LongTermMemoryContainer,
    ) -> list[ActivationSource]:
        sources: list[ActivationSource] = []

        if memories.procedural:
            context_score: float = self._match_context(situation, memories.procedural)
            if context_score > 0.5:
                sources.append(ActivationSource(dimension=self.dimension, score=context_score))

        return sources

    def _match_context(
        self, situation: SituationAwareness, procedural: ProceduralMemory
    ) -> float:
        task_type: str = situation.current_task.task_type.value

        for strategy in procedural.data.problem_solving_strategies:
            if strategy.problem_type.lower() in task_type.lower():
                return 0.8

        return 0.0


class EmotionalActivator(MemoryActivator):
    """情感激活器"""

    dimension = TriggerDimension.EMOTIONAL

    def activate(
        self,
        situation: SituationAwareness,
        memories: LongTermMemoryContainer,
    ) -> list[ActivationSource]:
        sources: list[ActivationSource] = []

        current_emotion: str = situation.context_anchors.emotional

        if memories.emotional:
            emotion_score: float = self._match_emotion(current_emotion, memories.emotional)
            if emotion_score > 0.3:
                sources.append(ActivationSource(dimension=self.dimension, score=emotion_score))

        return sources

    def _match_emotion(self, current: str, emotional: EmotionalMemory) -> float:
        if not emotional.data.emotion_states:
            return 0.0

        recent_states = emotional.data.emotion_states[-5:]
        for state in recent_states:
            if state.emotion_type in current or current in state.emotion_type:
                return 0.7 * state.intensity

        return 0.0


class CausalActivator(MemoryActivator):
    """因果激活器"""

    dimension = TriggerDimension.CAUSAL

    def activate(
        self,
        situation: SituationAwareness,
        memories: LongTermMemoryContainer,
    ) -> list[ActivationSource]:
        sources: list[ActivationSource] = []

        if memories.procedural:
            causal_score: float = self._match_causal_patterns(situation, memories.procedural)
            if causal_score > 0.5:
                sources.append(ActivationSource(dimension=self.dimension, score=causal_score))

        return sources

    def _match_causal_patterns(
        self, situation: SituationAwareness, procedural: ProceduralMemory
    ) -> float:
        if procedural.data.decision_patterns:
            avg_success: float = sum(
                p.success_rate for p in procedural.data.decision_patterns
            ) / len(procedural.data.decision_patterns)
            return avg_success

        return 0.0


class IdentityActivator(MemoryActivator):
    """身份激活器"""

    dimension = TriggerDimension.IDENTITY

    def activate(
        self,
        situation: SituationAwareness,
        memories: LongTermMemoryContainer,
    ) -> list[ActivationSource]:
        sources: list[ActivationSource] = []

        if memories.user_profile and memories.narrative:
            identity_score: float = self._match_identity(
                situation, memories.user_profile, memories.narrative
            )
            if identity_score > 0.5:
                sources.append(ActivationSource(dimension=self.dimension, score=identity_score))

        return sources

    def _match_identity(
        self,
        situation: SituationAwareness,
        profile: UserProfileMemory,
        narrative: NarrativeMemory,
    ) -> float:
        task_focus: str = situation.current_task.task_type.value

        for identity in profile.data.identity:
            if identity.lower() in task_focus.lower():
                return 0.8

        return 0.0


class ContextReconstructor:
    """
    上下文重构器

    核心模块：负责六维质量评估、比重适配、上下文重构
    支持与GlobalStateCapture集成，实现状态驱动的上下文质量优化
    """

    def __init__(self) -> None:
        """初始化上下文重构器"""
        # 初始化六维激活器
        self._activators: list[MemoryActivator] = [
            TemporalActivator(),
            SemanticActivator(),
            ContextualActivator(),
            EmotionalActivator(),
            CausalActivator(),
            IdentityActivator(),
        ]

        # 质量评估器
        self._quality_evaluator: QualityEvaluator = QualityEvaluator()

        # 比重适配器
        self._weight_adapter: WeightAdapter = WeightAdapter()

        # 配置
        self._max_activated_memories: int = 15
        self._relevance_threshold: float = 0.5

        # P0: 状态捕捉器集成
        self._state_capture: GlobalStateCapture | None = None
        self._state_subscription_id: str | None = None
        self._state_history: list[dict[str, Any]] = []
        self._last_phase: PhaseType | None = None

    # ========== P0: 状态集成方法 ==========

    def bind_state_capture(
        self,
        state_capture: GlobalStateCapture,
        subscribe_events: bool = True,
    ) -> None:
        """
        绑定状态捕捉器，建立事件订阅

        Args:
            state_capture: 全局状态捕捉器实例
            subscribe_events: 是否订阅状态变化事件
        """
        self._state_capture = state_capture

        if subscribe_events:
            # 订阅阶段变化事件
            self._state_subscription_id = state_capture.subscribe(
                event_types=[
                    StateEventType.PHASE_CHANGE,
                    StateEventType.TASK_SWITCH,
                    StateEventType.USER_STATE_CHANGE,
                ],
                callback=self._on_state_change,
            )

    def unbind_state_capture(self) -> None:
        """解绑状态捕捉器，取消事件订阅"""
        if self._state_capture and self._state_subscription_id:
            self._state_capture.unsubscribe(self._state_subscription_id)
            self._state_subscription_id = None
        self._state_capture = None

    def _on_state_change(self, event: StateChangeEvent) -> None:
        """
        状态变化事件回调

        Args:
            event: 状态变化事件
        """
        # 记录状态历史
        self._state_history.append({
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "changes": event.changes,
            "checkpoint_id": event.checkpoint_id,
        })

        # 保留最近50条状态历史
        if len(self._state_history) > 50:
            self._state_history = self._state_history[-50:]

        # 阶段变化时触发权重适配
        if event.event_type == StateEventType.PHASE_CHANGE:
            new_phase: str | None = event.changes.get("modified", {}).get("phase", {}).get("new")
            if new_phase:
                self._adapt_weights_by_phase(new_phase)

    def _adapt_weights_by_phase(self, phase: str) -> None:
        """
        根据阶段动态调整权重

        Args:
            phase: 阶段名称
        """
        phase_mapping: dict[str, ScenarioType] = {
            "exploration": ScenarioType.LEARNING,
            "design": ScenarioType.DESIGN,
            "planning": ScenarioType.PLANNING,
            "implementation": ScenarioType.CODING,
            "executing": ScenarioType.CODING,
            "verification": ScenarioType.DEBUGGING,
            "refinement": ScenarioType.DEBUGGING,
        }

        scenario: ScenarioType = phase_mapping.get(phase.lower(), ScenarioType.CODING)
        self._weight_adapter.adapt(scenario)

    def get_state_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        获取状态历史

        Args:
            limit: 最大数量

        Returns:
            状态历史列表
        """
        return self._state_history[-limit:]

    def get_state_aware_context(self) -> dict[str, Any]:
        """
        获取状态感知的上下文信息

        Returns:
            状态感知上下文
        """
        if not self._state_capture:
            return {"state_enabled": False}

        return {
            "state_enabled": True,
            "subscription_active": self._state_subscription_id is not None,
            "state_history_count": len(self._state_history),
            "recent_state_changes": self.get_state_history(5),
        }

    # ========== 核心方法 ==========

    def activate_memories(
        self,
        situation: SituationAwareness,
        long_term_memory: LongTermMemoryContainer,
    ) -> ActivationResult:
        """
        激活相关记忆

        Args:
            situation: 当前情境
            long_term_memory: 长期记忆容器

        Returns:
            激活结果
        """
        activated_memories: list[ActivatedMemory] = []
        activation_coverage: list[TriggerDimension] = []

        # 并行执行六维激活
        all_sources: dict[str, list[ActivationSource]] = {}
        for activator in self._activators:
            sources: list[ActivationSource] = activator.activate(
                situation, long_term_memory
            )
            if sources:
                all_sources[activator.dimension.value] = sources
                activation_coverage.append(activator.dimension)

        # 为每个记忆类型构建激活记录
        memory_items: list[tuple[str, MemoryType, Any, HeatLevel]] = []

        if long_term_memory.user_profile:
            memory_items.append(
                (
                    long_term_memory.user_profile.memory_id,
                    MemoryType.USER_PROFILE,
                    long_term_memory.user_profile,
                    long_term_memory.user_profile.heat.heat_level,
                )
            )

        if long_term_memory.procedural:
            memory_items.append(
                (
                    long_term_memory.procedural.memory_id,
                    MemoryType.PROCEDURAL,
                    long_term_memory.procedural,
                    long_term_memory.procedural.heat.heat_level,
                )
            )

        if long_term_memory.narrative:
            memory_items.append(
                (
                    long_term_memory.narrative.memory_id,
                    MemoryType.NARRATIVE,
                    long_term_memory.narrative,
                    long_term_memory.narrative.heat.heat_level,
                )
            )

        if long_term_memory.semantic:
            memory_items.append(
                (
                    long_term_memory.semantic.memory_id,
                    MemoryType.SEMANTIC,
                    long_term_memory.semantic,
                    long_term_memory.semantic.heat.heat_level,
                )
            )

        if long_term_memory.emotional:
            memory_items.append(
                (
                    long_term_memory.emotional.memory_id,
                    MemoryType.EMOTIONAL,
                    long_term_memory.emotional,
                    long_term_memory.emotional.heat.heat_level,
                )
            )

        # 计算综合激活分数
        for memory_id, memory_type, memory_obj, heat_level in memory_items:
            triggered_by: list[TriggerDimension] = []
            activation_sources: list[ActivationSource] = []
            total_score: float = 0.0

            for dim, sources_list in all_sources.items():
                for source in sources_list:
                    total_score += source.score
                    dim_enum: TriggerDimension = TriggerDimension(dim)
                    if dim_enum not in triggered_by:
                        triggered_by.append(dim_enum)
                    activation_sources.append(source)

            relevance_score: float = min(1.0, total_score / 3.0)

            if relevance_score >= self._relevance_threshold:
                activated_memories.append(
                    ActivatedMemory(
                        memory_id=memory_id,
                        memory_type=memory_type,
                        content_summary=self._summarize_memory(memory_obj),
                        triggered_by=triggered_by,
                        relevance_score=relevance_score,
                        heat_level=heat_level,
                        conflicts=[],
                        activation_sources=activation_sources,
                    )
                )

        # 按相关性排序并限制数量
        activated_memories.sort(key=lambda x: x.relevance_score, reverse=True)
        activated_memories = activated_memories[: self._max_activated_memories]

        unique_count: int = len(activated_memories)

        return ActivationResult(
            activated_memories=activated_memories,
            total_count=len(activated_memories),
            unique_count=unique_count,
            conflicts_detected=0,
            activation_coverage=activation_coverage,
        )

    def _summarize_memory(self, memory: Any) -> str:
        """生成记忆摘要"""
        if hasattr(memory, "data"):
            if hasattr(memory.data, "identity"):
                return f"用户画像: {', '.join(memory.data.identity[:3])}"
            elif hasattr(memory.data, "decision_patterns"):
                patterns_count: int = len(memory.data.decision_patterns)
                return f"程序性记忆: {patterns_count} 个决策模式"
            elif hasattr(memory.data, "growth_milestones"):
                milestones_count: int = len(memory.data.growth_milestones)
                return f"叙事记忆: {milestones_count} 个成长节点"
            elif hasattr(memory.data, "core_concepts"):
                concepts_count: int = len(memory.data.core_concepts)
                return f"语义记忆: {concepts_count} 个核心概念"
            elif hasattr(memory.data, "emotion_states"):
                emotions_count: int = len(memory.data.emotion_states)
                return f"情感记忆: {emotions_count} 个情绪状态"
        return "记忆内容"

    def reconstruct(
        self,
        situation: SituationAwareness,
        long_term_memory: LongTermMemoryContainer,
        scenario: ScenarioType | None = None,
        # P0: 状态集成参数
        use_state_history: bool = True,
    ) -> ContextPackage:
        """
        重构上下文（状态感知增强版）

        Args:
            situation: 当前情境
            long_term_memory: 长期记忆容器
            scenario: 场景类型（可选）
            use_state_history: 是否利用状态历史优化上下文

        Returns:
            上下文包
        """
        # P0: 状态感知优化
        state_context: dict[str, Any] = {}
        if use_state_history and self._state_capture:
            state_context = self._get_state_enhanced_context(situation)

        # 1. 激活记忆
        activation_result: ActivationResult = self.activate_memories(
            situation, long_term_memory
        )

        # 2. 确定场景（优先使用状态感知场景）
        if state_context.get("suggested_scenario"):
            detected_scenario: ScenarioType = state_context["suggested_scenario"]
        else:
            detected_scenario = scenario or self._detect_scenario(situation)

        # 3. 适配权重（状态感知权重已通过事件回调调整）
        weight_config: WeightConfig = self._weight_adapter.get_current_config()

        # 4. 评估质量
        quality_scores: QualityScores = self._quality_evaluator.evaluate(
            activation_result.activated_memories, situation
        )

        # P0: 根据状态历史调整质量分数
        if state_context.get("phase_stability"):
            # 阶段稳定时，提高连贯性分数
            quality_scores.coherence = min(1.0, quality_scores.coherence * 1.1)

        # 5. 构建上下文包
        package_id: str = f"pkg_{uuid.uuid4().hex[:12]}"

        context_package: ContextPackage = ContextPackage(
            package_id=package_id,
            task_context=self._build_task_context(situation, activation_result),
            user_state=self._build_user_state(situation, long_term_memory),
            activated_memories=[m.memory_id for m in activation_result.activated_memories],
            quality_scores=quality_scores,
            weight_config=weight_config,
            scenario=detected_scenario,
            phase=self._detect_phase(situation),
            metadata={
                "activation_coverage": [d.value for d in activation_result.activation_coverage],
                "total_memories_activated": len(activation_result.activated_memories),
            },
        )

        return context_package

    def _get_state_enhanced_context(
        self,
        situation: SituationAwareness,
    ) -> dict[str, Any]:
        """
        获取状态增强的上下文信息

        Args:
            situation: 当前情境

        Returns:
            状态增强上下文
        """
        result: dict[str, Any] = {
            "phase_stability": False,
            "suggested_scenario": None,
            "state_history_len": len(self._state_history),
        }

        if not self._state_history:
            return result

        # 分析最近的阶段变化
        recent_phases: list[str] = []
        for state in self._state_history[-10:]:
            phase_change: dict = state.get("changes", {}).get("modified", {}).get("phase", {})
            if phase_change:
                recent_phases.append(phase_change.get("new", ""))

        # 如果最近5条状态记录中没有阶段变化，认为阶段稳定
        if len([s for s in self._state_history[-5:] if s["event_type"] == StateEventType.PHASE_CHANGE.value]) == 0:
            result["phase_stability"] = True

        # 根据状态历史推断建议场景
        if recent_phases:
            last_phase: str = recent_phases[-1]
            result["suggested_scenario"] = self._phase_to_scenario(last_phase)

        return result

    def _phase_to_scenario(self, phase: str) -> ScenarioType | None:
        """
        将阶段映射到场景类型

        Args:
            phase: 阶段名称

        Returns:
            场景类型
        """
        mapping: dict[str, ScenarioType] = {
            "exploration": ScenarioType.LEARNING,
            "design": ScenarioType.DESIGN,
            "planning": ScenarioType.PLANNING,
            "implementation": ScenarioType.CODING,
            "executing": ScenarioType.CODING,
            "verification": ScenarioType.DEBUGGING,
            "refinement": ScenarioType.DEBUGGING,
        }
        return mapping.get(phase.lower())

    def _detect_scenario(self, situation: SituationAwareness) -> ScenarioType:
        """检测场景类型"""
        task_type: TaskType = situation.current_task.task_type

        mapping: dict[TaskType, ScenarioType] = {
            TaskType.TECHNICAL_IMPLEMENTATION: ScenarioType.CODING,
            TaskType.CODE_DEBUGGING: ScenarioType.DEBUGGING,
            TaskType.CREATIVE_DESIGN: ScenarioType.DESIGN,
            TaskType.BRAINSTORMING: ScenarioType.DESIGN,
            TaskType.DATA_ANALYSIS: ScenarioType.ANALYSIS,
            TaskType.PROBLEM_SOLVING: ScenarioType.PLANNING,
            TaskType.PRECISE_CALCULATION: ScenarioType.ANALYSIS,
            TaskType.KNOWLEDGE_QUERY: ScenarioType.LEARNING,
        }

        return mapping.get(task_type, ScenarioType.CODING)

    def _detect_phase(self, situation: SituationAwareness) -> PhaseType:
        """检测阶段类型"""
        phase_str: str = situation.current_task.task_phase.lower()

        mapping: dict[str, PhaseType] = {
            "exploration": PhaseType.EXPLORATION,
            "design": PhaseType.DESIGN,
            "implementation": PhaseType.IMPLEMENTATION,
            "verification": PhaseType.VERIFICATION,
            "refinement": PhaseType.REFINEMENT,
        }

        return mapping.get(phase_str, PhaseType.EXPLORATION)

    def _build_task_context(
        self,
        situation: SituationAwareness,
        activation_result: ActivationResult,
    ) -> dict[str, Any]:
        """构建任务上下文"""
        return {
            "task_type": situation.current_task.task_type.value,
            "complexity": situation.current_task.task_complexity,
            "implicit_requirements": situation.current_task.implicit_requirements,
            "activated_count": len(activation_result.activated_memories),
        }

    def _build_user_state(
        self,
        situation: SituationAwareness,
        long_term_memory: LongTermMemoryContainer,
    ) -> dict[str, Any]:
        """构建用户状态"""
        state: dict[str, Any] = {
            "technical_level": situation.user_current_state.technical_level,
            "current_focus": situation.user_current_state.current_focus,
            "mental_model": situation.user_current_state.mental_model,
            "decision_style": situation.user_current_state.decision_style,
        }

        if long_term_memory.user_profile:
            state["identity"] = long_term_memory.user_profile.data.identity

        if long_term_memory.procedural:
            state["neuroticism_tendency"] = (
                long_term_memory.procedural.data.neuroticism_tendency.score
            )

        return state

    def reconstruct_context(
        self, activation_result: ActivationResult
    ) -> ReconstructedContext:
        """
        重构上下文（兼容旧接口）

        Args:
            activation_result: 激活结果

        Returns:
            重构后的上下文
        """
        activated: list[ActivatedMemory] = activation_result.activated_memories

        task_context: TaskContextLayer = self._build_task_context_layer(activated)
        user_state: UserStateLayer = self._build_user_state_layer(activated)
        experiences: ActivatedExperiencesLayer = self._build_experiences_layer(activated)
        knowledge: KnowledgeContextLayer = self._build_knowledge_layer(activated)
        emotional: EmotionalContextLayer = self._build_emotional_layer(activated)
        narrative: NarrativeAnchorLayer = self._build_narrative_layer(activated)

        return ReconstructedContext(
            task_context=task_context,
            user_state=user_state,
            activated_experiences=experiences,
            knowledge_context=knowledge,
            emotional_context=emotional,
            narrative_anchor=narrative,
            conflicts_handled=[],
            metadata={
                "total_memories_used": len(activated),
                "activation_coverage": [d.value for d in activation_result.activation_coverage],
            },
        )

    def _build_task_context_layer(
        self, activated: list[ActivatedMemory]
    ) -> TaskContextLayer:
        return TaskContextLayer(
            current_task="基于激活记忆推断的任务",
            task_phase="探索阶段",
            implicit_requirements=["需要记忆支持"],
        )

    def _build_user_state_layer(
        self, activated: list[ActivatedMemory]
    ) -> UserStateLayer:
        profile_data: dict[str, Any] = {}
        for mem in activated:
            if mem.memory_type == MemoryType.USER_PROFILE:
                profile_data["identity"] = mem.content_summary

        return UserStateLayer(
            user_profile_core=profile_data,
            current_focus="当前任务焦点",
            decision_style="balanced",
            neuroticism_tendency=0.0,
        )

    def _build_experiences_layer(
        self, activated: list[ActivatedMemory]
    ) -> ActivatedExperiencesLayer:
        patterns: list[dict[str, Any]] = []

        for mem in activated:
            if mem.memory_type == MemoryType.PROCEDURAL:
                patterns.append(
                    {
                        "memory_id": mem.memory_id,
                        "relevance": mem.relevance_score,
                        "summary": mem.content_summary,
                    }
                )

        return ActivatedExperiencesLayer(
            relevant_patterns=patterns,
            success_stories=[],
            failure_lessons=[],
            tool_recommendations=[],
        )

    def _build_knowledge_layer(
        self, activated: list[ActivatedMemory]
    ) -> KnowledgeContextLayer:
        concepts: list[dict[str, Any]] = []

        for mem in activated:
            if mem.memory_type == MemoryType.SEMANTIC:
                concepts.append(
                    {
                        "memory_id": mem.memory_id,
                        "summary": mem.content_summary,
                    }
                )

        return KnowledgeContextLayer(
            key_concepts=concepts,
            concept_relations=[],
            principles=[],
        )

    def _build_emotional_layer(
        self, activated: list[ActivatedMemory]
    ) -> EmotionalContextLayer:
        current_emotion: str = "中性"

        for mem in activated:
            if mem.memory_type == MemoryType.EMOTIONAL:
                current_emotion = mem.content_summary
                break

        return EmotionalContextLayer(
            current_emotion=current_emotion,
            emotional_trend="稳定",
            satisfaction_level=0.5,
        )

    def _build_narrative_layer(
        self, activated: list[ActivatedMemory]
    ) -> NarrativeAnchorLayer:
        milestones: list[dict[str, Any]] = []

        for mem in activated:
            if mem.memory_type == MemoryType.NARRATIVE:
                milestones.append(
                    {
                        "memory_id": mem.memory_id,
                        "summary": mem.content_summary,
                    }
                )

        return NarrativeAnchorLayer(
            growth_milestones=milestones,
            identity_evolution=[],
            continuous_concerns=[],
        )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "QualityEvaluator",
    "WeightAdapter",
    "MemoryActivator",
    "TemporalActivator",
    "SemanticActivator",
    "ContextualActivator",
    "EmotionalActivator",
    "CausalActivator",
    "IdentityActivator",
    "ContextReconstructor",
]

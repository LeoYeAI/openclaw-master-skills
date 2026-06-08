"""
Agent Memory System - 独立洞察模块

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
    Insight,
    InsightSignal,
    InsightType,
    InsightPriority,
    SignalStrength,
    InsightPoolData,
    UserDecision,
    DecisionType,
    LongTermMemoryContainer,
    ReconstructedContext,
    ContextPackage,
    ScenarioType,
    PhaseType,
    UserStateType,
    StateEventType,
)

# 避免循环导入
if TYPE_CHECKING:
    from .state_capture import GlobalStateCapture


class InsightPool:
    """
    洞察池

    管理洞察的生命周期：活跃、待处理、归档
    """

    def __init__(self, max_active: int = 5) -> None:
        """
        初始化洞察池

        Args:
            max_active: 最大活跃洞察数
        """
        self._data: InsightPoolData = InsightPoolData(max_active=max_active)

    def add_insight(self, insight: Insight) -> bool:
        """
        添加洞察

        Args:
            insight: 洞察对象

        Returns:
            是否成功添加
        """
        # 如果有空位，直接添加到活跃
        if len(self._data.active_insights) < self._data.max_active:
            self._data.active_insights.append(insight)
            return True

        # 否则添加到待处理
        self._data.pending_insights.append(insight)
        return True

    def promote_insight(self, insight_id: str) -> bool:
        """
        将洞察提升为活跃状态

        Args:
            insight_id: 洞察ID

        Returns:
            是否成功提升
        """
        # 从待处理中查找
        for i, insight in enumerate(self._data.pending_insights):
            if insight.insight_id == insight_id:
                # 检查活跃槽位
                if len(self._data.active_insights) >= self._data.max_active:
                    # 移除最低优先级的活跃洞察
                    self._data.active_insights.sort(
                        key=lambda x: x.priority.value, reverse=True
                    )
                    removed = self._data.active_insights.pop()
                    self._data.archived_insights.append(removed)

                # 提升到活跃
                self._data.active_insights.append(insight)
                self._data.pending_insights.pop(i)
                return True

        return False

    def archive_insight(self, insight_id: str) -> bool:
        """
        将洞察归档

        Args:
            insight_id: 洞察ID

        Returns:
            是否成功归档
        """
        # 从活跃中查找
        for i, insight in enumerate(self._data.active_insights):
            if insight.insight_id == insight_id:
                self._data.archived_insights.append(insight)
                self._data.active_insights.pop(i)

                # 从待处理中提升一个
                if self._data.pending_insights:
                    next_insight = self._data.pending_insights.pop(0)
                    self._data.active_insights.append(next_insight)

                return True

        # 从待处理中查找
        for i, insight in enumerate(self._data.pending_insights):
            if insight.insight_id == insight_id:
                self._data.archived_insights.append(insight)
                self._data.pending_insights.pop(i)
                return True

        return False

    def get_active_insights(self) -> list[Insight]:
        """
        获取活跃洞察

        Returns:
            活跃洞察列表
        """
        return self._data.active_insights.copy()

    def get_pending_insights(self) -> list[Insight]:
        """
        获取待处理洞察

        Returns:
            待处理洞察列表
        """
        return self._data.pending_insights.copy()

    def get_insights_by_type(self, insight_type: InsightType) -> list[Insight]:
        """
        按类型获取洞察

        Args:
            insight_type: 洞察类型

        Returns:
            该类型的洞察列表
        """
        all_insights = (
            self._data.active_insights + self._data.pending_insights
        )
        return [i for i in all_insights if i.insight_type == insight_type]

    def get_high_priority_insights(self) -> list[Insight]:
        """
        获取高优先级洞察

        Returns:
            高优先级洞察列表
        """
        return [
            i for i in self._data.active_insights
            if i.priority == InsightPriority.HIGH
        ]

    def clear_expired(self, max_age_hours: int = 24) -> int:
        """
        清理过期洞察

        Args:
            max_age_hours: 最大保留时间（小时）

        Returns:
            清理数量
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        cleaned = 0

        # 清理活跃
        original_len = len(self._data.active_insights)
        self._data.active_insights = [
            i for i in self._data.active_insights
            if i.created_at > cutoff
        ]
        cleaned += original_len - len(self._data.active_insights)

        # 清理待处理
        original_len = len(self._data.pending_insights)
        self._data.pending_insights = [
            i for i in self._data.pending_insights
            if i.created_at > cutoff
        ]
        cleaned += original_len - len(self._data.pending_insights)

        return cleaned

    def get_stats(self) -> dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计数据
        """
        return {
            "active_count": len(self._data.active_insights),
            "pending_count": len(self._data.pending_insights),
            "archived_count": len(self._data.archived_insights),
            "max_active": self._data.max_active,
        }


class DetachedObserver:
    """
    超然观察者

    独立于主流程，以观察者身份监控记忆系统，生成非强制性建议
    """

    def __init__(self) -> None:
        """初始化超然观察者"""
        # 观察阈值
        self._signal_thresholds: dict[InsightType, float] = {
            InsightType.USER_PREFERENCE: 0.6,
            InsightType.BEHAVIORAL_PATTERN: 0.7,
            InsightType.BEST_PRACTICE: 0.75,
            InsightType.EFFICIENCY_OPPORTUNITY: 0.5,
            InsightType.KNOWLEDGE_GAP: 0.65,
            InsightType.PROCESS_IMPROVEMENT: 0.6,
            InsightType.ERROR_PREVENTION: 0.7,
            InsightType.EMOTIONAL_PATTERN: 0.55,
            InsightType.IDENTITY_EVOLUTION: 0.65,
        }

        # 观察记录
        self._observations: list[dict[str, Any]] = []
        self._max_observations: int = 100

    def observe(
        self,
        context_package: ContextPackage,
        long_term_memory: LongTermMemoryContainer,
    ) -> list[InsightSignal]:
        """
        观察当前状态并生成信号

        Args:
            context_package: 上下文包
            long_term_memory: 长期记忆容器

        Returns:
            洞察信号列表
        """
        signals: list[InsightSignal] = []

        # 观察用户偏好
        pref_signals = self._observe_preferences(long_term_memory)
        signals.extend(pref_signals)

        # 观察行为模式
        pattern_signals = self._observe_patterns(long_term_memory)
        signals.extend(pattern_signals)

        # 观察最佳实践
        practice_signals = self._observe_best_practices(long_term_memory)
        signals.extend(practice_signals)

        # 观察效率机会
        efficiency_signals = self._observe_efficiency(long_term_memory)
        signals.extend(efficiency_signals)

        # 观察知识缺口
        gap_signals = self._observe_knowledge_gaps(long_term_memory, context_package)
        signals.extend(gap_signals)

        # 观察情感模式
        emotion_signals = self._observe_emotional_patterns(long_term_memory)
        signals.extend(emotion_signals)

        # 观察身份演化
        identity_signals = self._observe_identity_evolution(long_term_memory)
        signals.extend(identity_signals)

        # 记录观察
        self._record_observation(context_package, signals)

        return signals

    def _observe_preferences(
        self, memory: LongTermMemoryContainer
    ) -> list[InsightSignal]:
        """观察用户偏好"""
        signals: list[InsightSignal] = []

        if memory.user_profile:
            profile: Any = memory.user_profile.data

            # 沟通风格偏好
            style: str = profile.communication_style.style
            if style:
                signals.append(
                    InsightSignal(
                        signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                        signal_type=InsightType.USER_PREFERENCE,
                        confidence=0.85,
                        data={"communication_style": style},
                        raw_observation=f"用户偏好 {style} 的沟通方式",
                    )
                )

            # 决策模式偏好
            decision_type: str = profile.decision_pattern.type
            if decision_type:
                signals.append(
                    InsightSignal(
                        signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                        signal_type=InsightType.USER_PREFERENCE,
                        confidence=0.75,
                        data={"decision_style": decision_type},
                        raw_observation=f"用户决策风格: {decision_type}",
                    )
                )

        return signals

    def _observe_patterns(
        self, memory: LongTermMemoryContainer
    ) -> list[InsightSignal]:
        """观察行为模式"""
        signals: list[InsightSignal] = []

        if memory.procedural:
            procedural: Any = memory.procedural.data

            # 决策模式检测
            for pattern in procedural.decision_patterns:
                if pattern.usage_count >= 3:
                    signals.append(
                        InsightSignal(
                            signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                            signal_type=InsightType.BEHAVIORAL_PATTERN,
                            confidence=pattern.confidence,
                            data={
                                "pattern": pattern.workflow,
                                "trigger": pattern.trigger_condition,
                                "usage_count": pattern.usage_count,
                            },
                            raw_observation=f"发现重复决策模式: {' → '.join(pattern.workflow)}",
                        )
                    )

        return signals

    def _observe_best_practices(
        self, memory: LongTermMemoryContainer
    ) -> list[InsightSignal]:
        """观察最佳实践"""
        signals: list[InsightSignal] = []

        if memory.procedural:
            procedural: Any = memory.procedural.data

            # 检查成功的问题解决策略
            for strategy in procedural.problem_solving_strategies:
                if strategy.success_rate >= 0.8:
                    signals.append(
                        InsightSignal(
                            signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                            signal_type=InsightType.BEST_PRACTICE,
                            confidence=strategy.success_rate,
                            data={
                                "strategy_id": strategy.problem_type,
                                "approach": strategy.preferred_approach,
                            },
                            raw_observation=f"发现高效策略: {strategy.problem_type}",
                        )
                    )

            # 检查工具使用效果
            tool_scores: dict[str, dict[str, float]] = {}
            for record in procedural.tool_effectiveness_records:
                tool: str = record.tool_name
                if tool not in tool_scores:
                    tool_scores[tool] = {"total": 0.0, "success": 0.0}
                tool_scores[tool]["total"] += 1
                if record.outcome == "success":
                    tool_scores[tool]["success"] += 1

            for tool, stats in tool_scores.items():
                if stats["total"] >= 3 and stats["success"] / stats["total"] >= 0.8:
                    signals.append(
                        InsightSignal(
                            signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                            signal_type=InsightType.BEST_PRACTICE,
                            confidence=stats["success"] / stats["total"],
                            data={
                                "tool": tool,
                                "success_rate": stats["success"] / stats["total"],
                            },
                            raw_observation=f"工具 {tool} 使用效果优秀",
                        )
                    )

        return signals

    def _observe_efficiency(
        self, memory: LongTermMemoryContainer
    ) -> list[InsightSignal]:
        """观察效率机会"""
        signals: list[InsightSignal] = []

        if memory.procedural:
            procedural: Any = memory.procedural.data

            # 检查工具组合模式
            for pattern in procedural.tool_combination_patterns:
                if pattern.usage_count >= 2:
                    signals.append(
                        InsightSignal(
                            signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                            signal_type=InsightType.EFFICIENCY_OPPORTUNITY,
                            confidence=0.7,
                            data={
                                "combination": pattern.sequence,
                                "context": pattern.task_pattern,
                            },
                            raw_observation=f"发现工具组合模式: {' → '.join(pattern.sequence)}",
                        )
                    )

        return signals

    def _observe_knowledge_gaps(
        self,
        memory: LongTermMemoryContainer,
        context: ContextPackage,
    ) -> list[InsightSignal]:
        """观察知识缺口"""
        signals: list[InsightSignal] = []

        if memory.semantic:
            semantic: Any = memory.semantic.data

            # 如果核心概念较少，提示知识缺口
            if len(semantic.core_concepts) < 5:
                signals.append(
                    InsightSignal(
                        signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                        signal_type=InsightType.KNOWLEDGE_GAP,
                        confidence=0.6,
                        data={"concept_count": len(semantic.core_concepts)},
                        raw_observation="语义知识覆盖度较低，可能存在知识缺口",
                    )
                )

        return signals

    def _observe_emotional_patterns(
        self, memory: LongTermMemoryContainer
    ) -> list[InsightSignal]:
        """观察情感模式"""
        signals: list[InsightSignal] = []

        if memory.emotional:
            emotional: Any = memory.emotional.data

            # 统计情感类型分布
            emotion_counts: dict[str, int] = {}
            for state in emotional.emotion_states[-20:]:
                emotion_type: str = state.emotion_type
                emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1

            # 检测主导情感
            if emotion_counts:
                dominant_emotion: str = max(emotion_counts, key=emotion_counts.get)
                dominant_ratio: float = emotion_counts[dominant_emotion] / sum(emotion_counts.values())

                if dominant_ratio >= 0.5 and dominant_emotion != "neutral":
                    signals.append(
                        InsightSignal(
                            signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                            signal_type=InsightType.EMOTIONAL_PATTERN,
                            confidence=dominant_ratio,
                            data={
                                "dominant_emotion": dominant_emotion,
                                "ratio": dominant_ratio,
                            },
                            raw_observation=f"用户情感倾向: {dominant_emotion} ({dominant_ratio:.0%})",
                        )
                    )

        return signals

    def _observe_identity_evolution(
        self, memory: LongTermMemoryContainer
    ) -> list[InsightSignal]:
        """观察身份演化"""
        signals: list[InsightSignal] = []

        if memory.narrative:
            narrative: Any = memory.narrative.data

            # 检查成长节点
            if len(narrative.growth_milestones) >= 3:
                signals.append(
                    InsightSignal(
                        signal_id=f"sig_{uuid.uuid4().hex[:8]}",
                        signal_type=InsightType.IDENTITY_EVOLUTION,
                        confidence=0.7,
                        data={
                            "milestone_count": len(narrative.growth_milestones),
                        },
                        raw_observation=f"用户有 {len(narrative.growth_milestones)} 个成长节点",
                    )
                )

        return signals

    def _record_observation(
        self,
        context: ContextPackage,
        signals: list[InsightSignal],
    ) -> None:
        """记录观察"""
        observation: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "context_id": context.package_id,
            "scenario": context.scenario.value,
            "phase": context.phase.value,
            "signal_count": len(signals),
            "signal_types": [s.signal_type.value for s in signals],
        }

        self._observations.append(observation)

        # 限制观察记录数量
        if len(self._observations) > self._max_observations:
            self._observations = self._observations[-self._max_observations:]

    def generate_insights(
        self,
        signals: list[InsightSignal],
        context: ContextPackage,
    ) -> list[Insight]:
        """
        从信号生成洞察

        Args:
            signals: 洞察信号列表
            context: 上下文包

        Returns:
            洞察列表
        """
        insights: list[Insight] = []

        # 按类型分组信号
        signals_by_type: dict[InsightType, list[InsightSignal]] = {}
        for signal in signals:
            signal_type: InsightType = signal.signal_type
            if signal_type not in signals_by_type:
                signals_by_type[signal_type] = []
            signals_by_type[signal_type].append(signal)

        # 为每种类型生成洞察
        for insight_type, type_signals in signals_by_type.items():
            threshold: float = self._signal_thresholds.get(insight_type, 0.5)

            # 筛选超过阈值的信号
            qualified_signals: list[InsightSignal] = [
                s for s in type_signals if s.confidence >= threshold
            ]

            if qualified_signals:
                # 合并相似信号
                merged_signal: InsightSignal = self._merge_signals(
                    qualified_signals, insight_type
                )

                # 确定优先级
                priority: InsightPriority = self._determine_priority(
                    merged_signal, insight_type
                )

                # 生成洞察
                insight: Insight = Insight(
                    insight_id=f"insight_{uuid.uuid4().hex[:12]}",
                    insight_type=insight_type,
                    title=self._generate_title(merged_signal),
                    content=self._generate_content(merged_signal),
                    priority=priority,
                    created_at=datetime.now(),
                    signal_strength=SignalStrength.STRONG
                    if merged_signal.confidence >= 0.8
                    else SignalStrength.MODERATE,
                    affected_memories=[s.signal_id for s in qualified_signals],
                    confidence=merged_signal.confidence,
                    actionable=self._is_actionable(insight_type),
                    actions=self._generate_actions(merged_signal, insight_type),
                    metadata={"signal_count": len(qualified_signals)},
                )
                insights.append(insight)

        # 按优先级排序
        insights.sort(key=lambda x: x.priority.value, reverse=True)

        return insights

    def _merge_signals(
        self, signals: list[InsightSignal], insight_type: InsightType
    ) -> InsightSignal:
        """合并相似信号"""
        if len(signals) == 1:
            return signals[0]

        avg_confidence: float = sum(s.confidence for s in signals) / len(signals)

        merged_data: dict[str, Any] = {}
        for signal in signals:
            merged_data.update(signal.data)

        return InsightSignal(
            signal_id=f"merged_{uuid.uuid4().hex[:8]}",
            signal_type=insight_type,
            confidence=avg_confidence,
            data=merged_data,
            raw_observation=" | ".join(s.raw_observation for s in signals[:3]),
        )

    def _determine_priority(
        self, signal: InsightSignal, insight_type: InsightType
    ) -> InsightPriority:
        """确定洞察优先级"""
        if signal.confidence >= 0.85:
            return InsightPriority.HIGH
        elif signal.confidence >= 0.7:
            return InsightPriority.MEDIUM
        else:
            return InsightPriority.LOW

    def _generate_title(self, signal: InsightSignal) -> str:
        """生成洞察标题"""
        type_titles: dict[InsightType, str] = {
            InsightType.USER_PREFERENCE: "用户偏好发现",
            InsightType.BEHAVIORAL_PATTERN: "行为模式识别",
            InsightType.BEST_PRACTICE: "最佳实践建议",
            InsightType.EFFICIENCY_OPPORTUNITY: "效率提升机会",
            InsightType.KNOWLEDGE_GAP: "知识缺口提示",
            InsightType.PROCESS_IMPROVEMENT: "流程改进建议",
            InsightType.ERROR_PREVENTION: "错误预防提醒",
            InsightType.EMOTIONAL_PATTERN: "情感模式洞察",
            InsightType.IDENTITY_EVOLUTION: "身份演化追踪",
        }
        return type_titles.get(signal.signal_type, "洞察发现")

    def _generate_content(self, signal: InsightSignal) -> str:
        """生成洞察内容"""
        return signal.raw_observation

    def _is_actionable(self, insight_type: InsightType) -> bool:
        """判断是否可执行"""
        actionable_types: set[InsightType] = {
            InsightType.BEST_PRACTICE,
            InsightType.EFFICIENCY_OPPORTUNITY,
            InsightType.PROCESS_IMPROVEMENT,
            InsightType.ERROR_PREVENTION,
        }
        return insight_type in actionable_types

    def _generate_actions(
        self, signal: InsightSignal, insight_type: InsightType
    ) -> list[str]:
        """生成行动建议"""
        actions: list[str] = []

        if insight_type == InsightType.USER_PREFERENCE:
            if "communication_style" in signal.data:
                actions.append(f"采用 {signal.data['communication_style']} 沟通风格")
            if "decision_style" in signal.data:
                actions.append(f"决策时参考 {signal.data['decision_style']} 模式")

        elif insight_type == InsightType.BEST_PRACTICE:
            if "tool" in signal.data:
                actions.append(f"优先使用 {signal.data['tool']} 工具")

        elif insight_type == InsightType.EFFICIENCY_OPPORTUNITY:
            if "combination" in signal.data:
                actions.append(f"尝试工具组合: {' → '.join(signal.data['combination'])}")

        elif insight_type == InsightType.KNOWLEDGE_GAP:
            actions.append("主动补充相关知识")
            actions.append("询问用户是否需要详细解释")

        return actions[:3]


# ============================================================================
# P1: 状态模式分析器
# ============================================================================


class StatePatternAnalyzer:
    """
    状态模式分析器

    分析状态历史，识别用户行为模式和效率优化机会
    """

    def __init__(self) -> None:
        """初始化状态模式分析器"""
        # 阶段时长统计
        self._phase_durations: dict[str, list[float]] = {}
        # 状态转换计数
        self._transition_counts: dict[str, int] = {}
        # 用户状态与效率关联
        self._state_efficiency: dict[str, dict[str, float]] = {}
        # 分析窗口（小时）
        self._analysis_window_hours: int = 24

    def analyze(
        self,
        state_history: list[dict[str, Any]],
        tool_records: list[Any] | None = None,
    ) -> list[Insight]:
        """
        分析状态历史，生成洞察

        Args:
            state_history: 状态历史列表
            tool_records: 工具使用记录（可选）

        Returns:
            洞察列表
        """
        insights: list[Insight] = []

        if not state_history:
            return insights

        # 1. 阶段时长分析
        duration_insights: list[Insight] = self._analyze_phase_durations(state_history)
        insights.extend(duration_insights)

        # 2. 状态转换模式分析
        transition_insights: list[Insight] = self._analyze_transition_patterns(state_history)
        insights.extend(transition_insights)

        # 3. 用户状态与效率关联分析
        if tool_records:
            efficiency_insights: list[Insight] = self._analyze_state_efficiency(
                state_history, tool_records
            )
            insights.extend(efficiency_insights)

        return insights

    def _analyze_phase_durations(
        self,
        state_history: list[dict[str, Any]],
    ) -> list[Insight]:
        """
        分析阶段停留时长

        Args:
            state_history: 状态历史

        Returns:
            洞察列表
        """
        insights: list[Insight] = []

        # 提取阶段变化事件
        phase_changes: list[dict[str, Any]] = []
        for state in state_history:
            if state.get("event_type") == StateEventType.PHASE_CHANGE.value:
                phase_changes.append(state)

        if len(phase_changes) < 2:
            return insights

        # 计算每个阶段的停留时长
        phase_durations: dict[str, list[float]] = {}
        for i in range(len(phase_changes) - 1):
            try:
                t1: datetime = datetime.fromisoformat(phase_changes[i]["timestamp"])
                t2: datetime = datetime.fromisoformat(phase_changes[i + 1]["timestamp"])
                duration_minutes: float = (t2 - t1).total_seconds() / 60

                # 获取阶段名称
                changes: dict = phase_changes[i].get("changes", {})
                new_phase: str = changes.get("modified", {}).get("phase", {}).get("new", "unknown")

                if new_phase not in phase_durations:
                    phase_durations[new_phase] = []
                phase_durations[new_phase].append(duration_minutes)
            except (ValueError, KeyError):
                continue

        # 分析异常时长
        for phase, durations in phase_durations.items():
            if not durations:
                continue

            avg_duration: float = sum(durations) / len(durations)

            # 定义基准时长（分钟）
            baseline_durations: dict[str, float] = {
                "planning": 15.0,
                "exploration": 20.0,
                "design": 25.0,
                "implementation": 30.0,
                "executing": 25.0,
                "verification": 15.0,
                "refinement": 10.0,
            }

            baseline: float = baseline_durations.get(phase, 20.0)

            # 如果平均时长超过基准的1.5倍，生成洞察
            if avg_duration > baseline * 1.5:
                insight: Insight = Insight(
                    insight_id=f"insight_phase_{uuid.uuid4().hex[:8]}",
                    insight_type=InsightType.EFFICIENCY_OPPORTUNITY,
                    title=f"{phase}阶段耗时偏长",
                    content=f"{phase}阶段平均停留 {avg_duration:.1f} 分钟，高于基准 {baseline:.1f} 分钟",
                    priority=InsightPriority.MEDIUM,
                    signal_strength=SignalStrength.MODERATE,
                    confidence=0.7,
                    actionable=True,
                    actions=[f"考虑使用模板或工具加速{phase}阶段"],
                    metadata={
                        "phase": phase,
                        "avg_duration": avg_duration,
                        "baseline": baseline,
                        "sample_count": len(durations),
                    },
                )
                insights.append(insight)

        return insights

    def _analyze_transition_patterns(
        self,
        state_history: list[dict[str, Any]],
    ) -> list[Insight]:
        """
        分析状态转换模式

        Args:
            state_history: 状态历史

        Returns:
            洞察列表
        """
        insights: list[Insight] = []

        # 统计转换模式
        transitions: dict[str, int] = {}
        prev_phase: str | None = None

        for state in state_history:
            if state.get("event_type") != StateEventType.PHASE_CHANGE.value:
                continue

            changes: dict = state.get("changes", {})
            new_phase: str = changes.get("modified", {}).get("phase", {}).get("new", "")

            if prev_phase and new_phase:
                transition_key: str = f"{prev_phase}→{new_phase}"
                transitions[transition_key] = transitions.get(transition_key, 0) + 1

            prev_phase = new_phase

        # 识别回退模式
        backtracking_patterns: list[str] = []
        for transition, count in transitions.items():
            if count >= 2:
                # 检查是否是回退
                parts: list[str] = transition.split("→")
                if len(parts) == 2:
                    from_phase, to_phase = parts
                    # 简单回退检测：从后阶段回到前阶段
                    phase_order: list[str] = ["planning", "exploration", "design", "implementation", "executing", "verification", "refinement"]
                    try:
                        from_idx: int = phase_order.index(from_phase)
                        to_idx: int = phase_order.index(to_phase)
                        if to_idx < from_idx:
                            backtracking_patterns.append(f"{transition} (×{count})")
                    except ValueError:
                        pass

        if backtracking_patterns:
            insight: Insight = Insight(
                insight_id=f"insight_backtrack_{uuid.uuid4().hex[:8]}",
                insight_type=InsightType.BEHAVIORAL_PATTERN,
                title="检测到阶段回退模式",
                content=f"用户经常从后阶段回退到前阶段: {', '.join(backtracking_patterns[:3])}",
                priority=InsightPriority.MEDIUM,
                signal_strength=SignalStrength.MODERATE,
                confidence=0.6,
                actionable=True,
                actions=["在前阶段投入更多时间确保需求清晰", "考虑使用增量验证减少回退"],
                metadata={
                    "patterns": backtracking_patterns,
                    "transition_counts": transitions,
                },
            )
            insights.append(insight)

        return insights

    def _analyze_state_efficiency(
        self,
        state_history: list[dict[str, Any]],
        tool_records: list[Any],
    ) -> list[Insight]:
        """
        分析用户状态与效率关联

        Args:
            state_history: 状态历史
            tool_records: 工具使用记录

        Returns:
            洞察列表
        """
        insights: list[Insight] = []

        # 统计不同用户状态下的工具成功率
        state_tool_stats: dict[str, dict[str, Any]] = {}

        for record in tool_records:
            user_state: str = getattr(record, "user_state", None) or "unknown"
            outcome: str = getattr(record, "outcome", "unknown")

            if user_state not in state_tool_stats:
                state_tool_stats[user_state] = {"total": 0, "success": 0}

            state_tool_stats[user_state]["total"] += 1
            if outcome == "success":
                state_tool_stats[user_state]["success"] += 1

        # 找出高效和低效状态
        high_efficiency_states: list[dict[str, Any]] = []
        low_efficiency_states: list[dict[str, Any]] = []

        for state, stats in state_tool_stats.items():
            if stats["total"] >= 3:  # 至少3次记录才分析
                success_rate: float = stats["success"] / stats["total"]
                if success_rate >= 0.8:
                    high_efficiency_states.append({
                        "state": state,
                        "success_rate": success_rate,
                        "count": stats["total"],
                    })
                elif success_rate <= 0.5:
                    low_efficiency_states.append({
                        "state": state,
                        "success_rate": success_rate,
                        "count": stats["total"],
                    })

        # 生成高效状态洞察
        if high_efficiency_states:
            best_state: dict[str, Any] = max(high_efficiency_states, key=lambda x: x["success_rate"])
            insight: Insight = Insight(
                insight_id=f"insight_efficient_{uuid.uuid4().hex[:8]}",
                insight_type=InsightType.BEST_PRACTICE,
                title=f"{best_state['state']}状态下效率最高",
                content=f"在{best_state['state']}状态下，工具使用成功率高达 {best_state['success_rate']:.0%}",
                priority=InsightPriority.HIGH,
                signal_strength=SignalStrength.STRONG,
                confidence=0.8,
                actionable=True,
                actions=[f"在{best_state['state']}状态下优先执行关键任务"],
                metadata=best_state,
            )
            insights.append(insight)

        # 生成低效状态洞察
        if low_efficiency_states:
            worst_state: dict[str, Any] = min(low_efficiency_states, key=lambda x: x["success_rate"])
            insight: Insight = Insight(
                insight_id=f"insight_inefficient_{uuid.uuid4().hex[:8]}",
                insight_type=InsightType.ERROR_PREVENTION,
                title=f"{worst_state['state']}状态下效率较低",
                content=f"在{worst_state['state']}状态下，工具使用成功率仅 {worst_state['success_rate']:.0%}，建议稍后再试或切换任务",
                priority=InsightPriority.HIGH,
                signal_strength=SignalStrength.STRONG,
                confidence=0.75,
                actionable=True,
                actions=[f"避免在{worst_state['state']}状态下执行复杂任务", "建议休息或切换到简单任务"],
                metadata=worst_state,
            )
            insights.append(insight)

        return insights


# ============================================================================
# 洞察模块主类
# ============================================================================
class InsightModule:
    """
    独立洞察模块

    核心模块：整合洞察池和超然观察者，提供统一的洞察管理接口
    """

    def __init__(self, max_active_insights: int = 5) -> None:
        """
        初始化洞察模块

        Args:
            max_active_insights: 最大活跃洞察数
        """
        self._observer: DetachedObserver = DetachedObserver()
        self._pool: InsightPool = InsightPool(max_active=max_active_insights)
        self._history: list[Insight] = []
        # P1: 状态模式分析器
        self._state_analyzer: StatePatternAnalyzer = StatePatternAnalyzer()
        self._state_capture: GlobalStateCapture | None = None

    # ========== P1: 状态分析方法 ==========

    def bind_state_capture(
        self,
        state_capture: GlobalStateCapture,
    ) -> None:
        """
        绑定状态捕捉器

        Args:
            state_capture: 全局状态捕捉器实例
        """
        self._state_capture = state_capture

    def unbind_state_capture(self) -> None:
        """解绑状态捕捉器"""
        self._state_capture = None

    def analyze_state_patterns(
        self,
        thread_id: str | None = None,
        tool_records: list[Any] | None = None,
    ) -> list[Insight]:
        """
        分析状态模式，生成洞察

        Args:
            thread_id: 线程ID（用于获取状态历史）
            tool_records: 工具使用记录（可选，用于效率关联分析）

        Returns:
            洞察列表
        """
        if not self._state_capture:
            return []

        # 获取状态历史
        state_history: list[dict[str, Any]] = self._state_capture.get_state_history(
            thread_id=thread_id or "",
            limit=100,
        )

        # 提取状态变化事件
        state_events: list[dict[str, Any]] = []
        for history_item in state_history:
            state_events.append({
                "event_type": "state_change",
                "timestamp": history_item.get("timestamp", ""),
                "state": history_item.get("state", {}),
            })

        # 分析
        insights: list[Insight] = self._state_analyzer.analyze(
            state_history=state_events,
            tool_records=tool_records,
        )

        # 添加到洞察池
        for insight in insights:
            self._pool.add_insight(insight)

        return insights

    # ========== 核心方法 ==========

    def process(
        self,
        context_package: ContextPackage,
        long_term_memory: LongTermMemoryContainer,
    ) -> list[Insight]:
        """
        处理上下文和记忆，生成洞察

        Args:
            context_package: 上下文包
            long_term_memory: 长期记忆

        Returns:
            洞察列表
        """
        # 观察并生成信号
        signals: list[InsightSignal] = self._observer.observe(
            context_package, long_term_memory
        )

        # 从信号生成洞察
        insights: list[Insight] = self._observer.generate_insights(
            signals, context_package
        )

        # 添加到洞察池
        for insight in insights:
            self._pool.add_insight(insight)

        # 记录历史
        self._history.extend(insights)
        self._history = self._history[-100:]

        return insights

    def get_active_insights(self) -> list[Insight]:
        """
        获取当前活跃洞察

        Returns:
            活跃洞察列表
        """
        return self._pool.get_active_insights()

    def get_insights_by_type(self, insight_type: InsightType) -> list[Insight]:
        """
        按类型获取洞察

        Args:
            insight_type: 洞察类型

        Returns:
            该类型的洞察列表
        """
        return self._pool.get_insights_by_type(insight_type)

    def get_high_priority_insights(self) -> list[Insight]:
        """
        获取高优先级洞察

        Returns:
            高优先级洞察列表
        """
        return self._pool.get_high_priority_insights()

    def archive_insight(self, insight_id: str) -> bool:
        """
        归档洞察

        Args:
            insight_id: 洞察ID

        Returns:
            是否成功归档
        """
        return self._pool.archive_insight(insight_id)

    def promote_insight(self, insight_id: str) -> bool:
        """
        提升洞察为活跃状态

        Args:
            insight_id: 洞察ID

        Returns:
            是否成功提升
        """
        return self._pool.promote_insight(insight_id)

    def record_decision(
        self,
        decision: UserDecision,
        long_term_memory: LongTermMemoryContainer,
    ) -> dict[str, Any]:
        """
        记录用户决策

        Args:
            decision: 用户决策
            long_term_memory: 长期记忆容器

        Returns:
            更新结果
        """
        result: dict[str, Any] = {"updated": False, "changes": []}

        # 根据决策类型更新相关洞察
        if decision.decision_type == DecisionType.TOOL_CHOICE:
            result["changes"].append("tool_usage_updated")
            result["updated"] = True

        elif decision.decision_type == DecisionType.APPROACH_SELECTION:
            result["changes"].append("decision_pattern_updated")
            result["updated"] = True

        elif decision.decision_type == DecisionType.PREFERENCE_EXPRESSION:
            result["changes"].append("user_preference_updated")
            result["updated"] = True

        return result

    def get_stats(self) -> dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计数据
        """
        return {
            **self._pool.get_stats(),
            "total_history": len(self._history),
        }

    def cleanup(self, max_age_hours: int = 24) -> int:
        """
        清理过期洞察

        Args:
            max_age_hours: 最大保留时间（小时）

        Returns:
            清理数量
        """
        return self._pool.clear_expired(max_age_hours)

    def format_insights_for_context(self) -> str:
        """
        格式化洞察用于上下文注入

        Returns:
            格式化的洞察字符串
        """
        active_insights = self.get_active_insights()

        if not active_insights:
            return ""

        lines: list[str] = ["## 智能洞察"]

        for insight in active_insights[:5]:
            priority_marker = {
                InsightPriority.HIGH: "!",
                InsightPriority.MEDIUM: "*",
                InsightPriority.LOW: "-",
            }.get(insight.priority, "-")

            lines.append(f"{priority_marker} [{insight.title}] {insight.content}")

            if insight.actionable and insight.actions:
                lines.append(f"  建议: {insight.actions[0]}")

        return "\n".join(lines)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "InsightPool",
    "DetachedObserver",
    "InsightModule",
    "StatePatternAnalyzer",
]

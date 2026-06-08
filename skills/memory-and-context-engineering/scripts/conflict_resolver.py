"""
Agent Memory System - 冲突解决器

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
from datetime import datetime
from typing import Any

from .types import (
    ActivatedMemory,
    MemoryConflict,
    ConflictType,
    ConflictSeverity,
    ResolutionMode,
    ResolutionResult,
    LongTermMemoryContainer,
)


class ConflictResolver:
    """
    冲突解决器

    负责检测和解决记忆冲突
    """

    def __init__(self) -> None:
        """初始化冲突解决器"""
        # 冲突检测阈值
        self._similarity_threshold: float = 0.7
        self._contradiction_threshold: float = 0.5

        # 解决策略权重
        self._strategy_weights: dict[ResolutionMode, float] = {
            ResolutionMode.RECENCY: 1.0,
            ResolutionMode.FREQUENCY: 0.8,
            ResolutionMode.USER_CONFIRMATION: 0.95,
            ResolutionMode.SOURCE_TRUST: 0.9,
            ResolutionMode.CONTEXTUAL: 0.85,
        }

    def detect_conflicts(
        self,
        activated_memories: list[ActivatedMemory],
        long_term_memory: LongTermMemoryContainer,
    ) -> list[MemoryConflict]:
        """
        检测记忆冲突

        Args:
            activated_memories: 激活的记忆列表
            long_term_memory: 长期记忆容器

        Returns:
            检测到的冲突列表
        """
        conflicts: list[MemoryConflict] = []

        # 1. 检测数值矛盾
        numeric_conflicts: list[MemoryConflict] = self._detect_numeric_contradictions(
            activated_memories
        )
        conflicts.extend(numeric_conflicts)

        # 2. 检测概念冲突
        concept_conflicts: list[MemoryConflict] = self._detect_concept_conflicts(
            activated_memories, long_term_memory
        )
        conflicts.extend(concept_conflicts)

        # 3. 检测策略冲突
        strategy_conflicts: list[MemoryConflict] = self._detect_strategy_conflicts(
            activated_memories
        )
        conflicts.extend(strategy_conflicts)

        # 4. 检测情感冲突
        emotional_conflicts: list[MemoryConflict] = self._detect_emotional_conflicts(
            activated_memories
        )
        conflicts.extend(emotional_conflicts)

        # 5. 检测时效冲突
        temporal_conflicts: list[MemoryConflict] = self._detect_temporal_conflicts(
            activated_memories
        )
        conflicts.extend(temporal_conflicts)

        return conflicts

    def _detect_numeric_contradictions(
        self, memories: list[ActivatedMemory]
    ) -> list[MemoryConflict]:
        """检测数值矛盾"""
        conflicts: list[MemoryConflict] = []

        # 提取所有数值类记忆
        numeric_memories: list[tuple[str, str, float]] = []
        for mem in memories:
            # 简化的数值提取逻辑
            if "分数" in mem.content_summary or "score" in mem.content_summary.lower():
                numeric_memories.append(
                    (mem.memory_id, mem.memory_type.value, mem.relevance_score)
                )

        # 检查数值差异
        for i, (id1, type1, val1) in enumerate(numeric_memories):
            for id2, type2, val2 in numeric_memories[i + 1 :]:
                if type1 == type2 and abs(val1 - val2) > self._contradiction_threshold:
                    conflicts.append(
                        MemoryConflict(
                            conflict_id=f"conf_{uuid.uuid4().hex[:8]}",
                            conflict_type=ConflictType.DATA_INCONSISTENCY,
                            severity=ConflictSeverity.MEDIUM,
                            involved_memories=[id1, id2],
                            description=f"数值矛盾: {val1:.2f} vs {val2:.2f}",
                            detected_at=datetime.now(),
                            resolution_mode=ResolutionMode.RECENCY,
                        )
                    )

        return conflicts

    def _detect_concept_conflicts(
        self,
        memories: list[ActivatedMemory],
        long_term_memory: LongTermMemoryContainer,
    ) -> list[MemoryConflict]:
        """检测概念冲突"""
        conflicts: list[MemoryConflict] = []

        # 从语义记忆中提取概念
        if long_term_memory.semantic:
            concepts: list[str] = [
                c.concept
                for c in long_term_memory.semantic.data.core_concepts
            ]

            # 检查概念间的矛盾关系
            contradictory_pairs: list[tuple[str, str]] = [
                ("高效", "低效"),
                ("简单", "复杂"),
                ("成功", "失败"),
            ]

            for concept in concepts:
                for pair in contradictory_pairs:
                    if concept.lower() in [p.lower() for p in pair]:
                        # 检查是否同时存在矛盾概念
                        other: str = pair[1] if pair[0].lower() == concept.lower() else pair[0]
                        if any(
                            other.lower() in c.lower() for c in concepts
                        ):
                            conflicts.append(
                                MemoryConflict(
                                    conflict_id=f"conf_{uuid.uuid4().hex[:8]}",
                                    conflict_type=ConflictType.CONCEPT_AMBIGUITY,
                                    severity=ConflictSeverity.LOW,
                                    involved_memories=[],
                                    description=f"概念冲突: {pair[0]} vs {pair[1]}",
                                    detected_at=datetime.now(),
                                    resolution_mode=ResolutionMode.CONTEXTUAL,
                                )
                            )

        return conflicts

    def _detect_strategy_conflicts(
        self, memories: list[ActivatedMemory]
    ) -> list[MemoryConflict]:
        """检测策略冲突"""
        conflicts: list[MemoryConflict] = []

        # 提取程序性记忆中的策略
        strategies: list[tuple[str, list[str]]] = []
        for mem in memories:
            if mem.memory_type.value == "procedural":
                strategies.append((mem.memory_id, mem.triggered_by))

        # 检查策略方向冲突
        for i, (id1, triggers1) in enumerate(strategies):
            for id2, triggers2 in strategies[i + 1 :]:
                # 检查触发维度是否相反
                trigger_set1: set[str] = {t.value for t in triggers1}
                trigger_set2: set[str] = {t.value for t in triggers2}

                if len(trigger_set1 & trigger_set2) == 0 and len(triggers1) > 0 and len(triggers2) > 0:
                    conflicts.append(
                        MemoryConflict(
                            conflict_id=f"conf_{uuid.uuid4().hex[:8]}",
                            conflict_type=ConflictType.STRATEGY_CONFLICT,
                            severity=ConflictSeverity.HIGH,
                            involved_memories=[id1, id2],
                            description="策略方向冲突: 触发维度完全不重叠",
                            detected_at=datetime.now(),
                            resolution_mode=ResolutionMode.USER_CONFIRMATION,
                        )
                    )

        return conflicts

    def _detect_emotional_conflicts(
        self, memories: list[ActivatedMemory]
    ) -> list[MemoryConflict]:
        """检测情感冲突"""
        conflicts: list[MemoryConflict] = []

        # 提取情感状态
        emotions: list[tuple[str, str]] = []
        for mem in memories:
            if mem.memory_type.value == "emotional":
                emotions.append((mem.memory_id, mem.content_summary))

        # 检查情感矛盾
        positive_emotions: set[str] = {"积极", "满意", "开心", "positive"}
        negative_emotions: set[str] = {"焦虑", "沮丧", "不满", "negative"}

        has_positive: bool = False
        has_negative: bool = False
        positive_ids: list[str] = []
        negative_ids: list[str] = []

        for mem_id, emotion in emotions:
            emotion_lower: str = emotion.lower()
            if any(e in emotion_lower for e in positive_emotions):
                has_positive = True
                positive_ids.append(mem_id)
            elif any(e in emotion_lower for e in negative_emotions):
                has_negative = True
                negative_ids.append(mem_id)

        if has_positive and has_negative:
            conflicts.append(
                MemoryConflict(
                    conflict_id=f"conf_{uuid.uuid4().hex[:8]}",
                    conflict_type=ConflictType.EMOTIONAL_INCONSISTENCY,
                    severity=ConflictSeverity.LOW,
                    involved_memories=positive_ids + negative_ids,
                    description="情感状态矛盾: 同时存在积极和消极情绪",
                    detected_at=datetime.now(),
                    resolution_mode=ResolutionMode.RECENCY,
                )
            )

        return conflicts

    def _detect_temporal_conflicts(
        self, memories: list[ActivatedMemory]
    ) -> list[MemoryConflict]:
        """检测时效冲突"""
        conflicts: list[MemoryConflict] = []

        # 检查记忆的新旧程度
        hot_memories: list[str] = []
        cold_memories: list[str] = []

        for mem in memories:
            if mem.heat_level.value == "hot":
                hot_memories.append(mem.memory_id)
            elif mem.heat_level.value == "cold":
                cold_memories.append(mem.memory_id)

        # 如果同时存在热记忆和冷记忆，可能存在时效冲突
        if hot_memories and cold_memories:
            conflicts.append(
                MemoryConflict(
                    conflict_id=f"conf_{uuid.uuid4().hex[:8]}",
                    conflict_type=ConflictType.TEMPORAL_INVALIDATION,
                    severity=ConflictSeverity.MEDIUM,
                    involved_memories=hot_memories[:1] + cold_memories[:1],
                    description="时效冲突: 新旧记忆并存",
                    detected_at=datetime.now(),
                    resolution_mode=ResolutionMode.RECENCY,
                )
            )

        return conflicts

    def resolve(
        self,
        conflict: MemoryConflict,
        memories: list[ActivatedMemory],
        long_term_memory: LongTermMemoryContainer,
    ) -> ResolutionResult:
        """
        解决冲突

        Args:
            conflict: 冲突对象
            memories: 激活的记忆列表
            long_term_memory: 长期记忆容器

        Returns:
            解决结果
        """
        mode: ResolutionMode = conflict.resolution_mode

        # 根据解决模式选择策略
        if mode == ResolutionMode.RECENCY:
            return self._resolve_by_recency(conflict, memories)
        elif mode == ResolutionMode.FREQUENCY:
            return self._resolve_by_frequency(conflict, memories, long_term_memory)
        elif mode == ResolutionMode.USER_CONFIRMATION:
            return self._resolve_by_user_confirmation(conflict)
        elif mode == ResolutionMode.SOURCE_TRUST:
            return self._resolve_by_trust(conflict, memories)
        elif mode == ResolutionMode.CONTEXTUAL:
            return self._resolve_by_context(conflict, memories)
        else:
            return self._resolve_by_recency(conflict, memories)

    def _resolve_by_recency(
        self, conflict: MemoryConflict, memories: list[ActivatedMemory]
    ) -> ResolutionResult:
        """基于新近性解决"""
        involved_ids: set[str] = set(conflict.involved_memories)

        # 找出最新的记忆
        winning_memory: str = ""
        latest_time: datetime = datetime.min

        for mem in memories:
            if mem.memory_id in involved_ids:
                # 使用相关性作为新近性的代理指标
                if mem.relevance_score > 0.5:
                    winning_memory = mem.memory_id
                    break

        if not winning_memory and conflict.involved_memories:
            winning_memory = conflict.involved_memories[0]

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_mode=ResolutionMode.RECENCY,
            winning_memory=winning_memory,
            losing_memories=[mid for mid in involved_ids if mid != winning_memory],
            confidence=0.7,
            rationale="选择最新激活的记忆",
            user_required=False,
        )

    def _resolve_by_frequency(
        self,
        conflict: MemoryConflict,
        memories: list[ActivatedMemory],
        long_term_memory: LongTermMemoryContainer,
    ) -> ResolutionResult:
        """基于频率解决"""
        involved_ids: set[str] = set(conflict.involved_memories)

        # 统计访问频率
        frequencies: dict[str, int] = {}

        for mem_id in involved_ids:
            if long_term_memory.procedural:
                for record in long_term_memory.procedural.data.tool_effectiveness_records:
                    # 简化：使用默认频率
                    frequencies[mem_id] = frequencies.get(mem_id, 0) + 1
            else:
                frequencies[mem_id] = 1

        # 选择频率最高的
        winning_memory: str = max(
            frequencies, key=frequencies.get, default=conflict.involved_memories[0] if conflict.involved_memories else ""
        )

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_mode=ResolutionMode.FREQUENCY,
            winning_memory=winning_memory,
            losing_memories=[mid for mid in involved_ids if mid != winning_memory],
            confidence=0.65,
            rationale="选择使用频率最高的记忆",
            user_required=False,
        )

    def _resolve_by_user_confirmation(
        self, conflict: MemoryConflict
    ) -> ResolutionResult:
        """需要用户确认"""
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_mode=ResolutionMode.USER_CONFIRMATION,
            winning_memory="",
            losing_memories=[],
            confidence=0.0,
            rationale="冲突需要用户确认",
            user_required=True,
            alternatives=conflict.involved_memories,
        )

    def _resolve_by_trust(
        self, conflict: MemoryConflict, memories: list[ActivatedMemory]
    ) -> ResolutionResult:
        """基于可信度解决"""
        involved_ids: set[str] = set(conflict.involved_memories)

        # 计算可信度分数
        trust_scores: dict[str, float] = {}

        for mem in memories:
            if mem.memory_id in involved_ids:
                # 基于热度和相关性计算可信度
                trust: float = mem.relevance_score
                if mem.heat_level.value == "hot":
                    trust += 0.2
                elif mem.heat_level.value == "warm":
                    trust += 0.1

                trust_scores[mem.memory_id] = trust

        # 选择可信度最高的
        winning_memory: str = max(
            trust_scores,
            key=trust_scores.get,
            default=conflict.involved_memories[0] if conflict.involved_memories else "",
        )

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_mode=ResolutionMode.SOURCE_TRUST,
            winning_memory=winning_memory,
            losing_memories=[mid for mid in involved_ids if mid != winning_memory],
            confidence=trust_scores.get(winning_memory, 0.5),
            rationale="选择可信度最高的记忆",
            user_required=False,
        )

    def _resolve_by_context(
        self, conflict: MemoryConflict, memories: list[ActivatedMemory]
    ) -> ResolutionResult:
        """基于上下文相关性解决"""
        involved_ids: set[str] = set(conflict.involved_memories)

        # 选择与当前上下文最相关的记忆
        relevance_scores: dict[str, float] = {}

        for mem in memories:
            if mem.memory_id in involved_ids:
                relevance_scores[mem.memory_id] = mem.relevance_score

        winning_memory: str = max(
            relevance_scores,
            key=relevance_scores.get,
            default=conflict.involved_memories[0] if conflict.involved_memories else "",
        )

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_mode=ResolutionMode.CONTEXTUAL,
            winning_memory=winning_memory,
            losing_memories=[mid for mid in involved_ids if mid != winning_memory],
            confidence=relevance_scores.get(winning_memory, 0.5),
            rationale="选择与当前上下文最相关的记忆",
            user_required=False,
        )

    def resolve_all(
        self,
        conflicts: list[MemoryConflict],
        memories: list[ActivatedMemory],
        long_term_memory: LongTermMemoryContainer,
    ) -> list[ResolutionResult]:
        """
        解决所有冲突

        Args:
            conflicts: 冲突列表
            memories: 激活的记忆列表
            long_term_memory: 长期记忆容器

        Returns:
            解决结果列表
        """
        results: list[ResolutionResult] = []

        for conflict in conflicts:
            result: ResolutionResult = self.resolve(
                conflict, memories, long_term_memory
            )
            results.append(result)

        return results


# ============================================================================
# 导出
# ============================================================================

__all__ = ["ConflictResolver"]

"""
Agent Memory System - Memory Conflict Detector（记忆冲突检测器）

=== 功能说明 ===
对应 Context Engineering 核心能力：记忆

实现文档要求：
- "长期记忆和当前任务冲突"
- 检测新旧记忆冲突

核心能力：
1. 显性冲突检测 - 明确矛盾的事实
2. 语义冲突检测 - 语义相似但内容矛盾
3. 冲突严重程度评估 - 高/中/低/严重
4. 冲突解决策略 - 覆盖/合并/标记
5. 冲突日志记录 - 记录冲突历史

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * redis: >=4.5.0
    - 用途：冲突日志存储（可选）
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  redis>=4.5.0
  ```
=== 声明结束 ===

安全提醒：冲突检测应保守，避免误报
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from .types import (
    ConflictType,
    ConflictSeverity,
    ResolutionMode,
    MemoryConflict,
    ResolutionResult,
    ActivatedMemory,
    LongTermMemoryContainer,
)


# ============================================================================
# 扩展枚举类型
# ============================================================================


class ConflictCategory(str, Enum):
    """冲突类别"""

    FACTUAL = "factual"           # 事实冲突
    PREFERENCE = "preference"     # 偏好冲突
    EMOTIONAL = "emotional"       # 情感冲突
    TEMPORAL = "temporal"         # 时效冲突
    CONTEXTUAL = "contextual"     # 上下文冲突
    SEMANTIC = "semantic"         # 语义冲突


class ConflictAction(str, Enum):
    """冲突处理动作"""

    OVERRIDE = "override"         # 覆盖旧记忆
    MERGE = "merge"               # 合并记忆
    FLAG = "flag"                 # 标记冲突
    ASK_USER = "ask_user"         # 询问用户
    KEEP_BOTH = "keep_both"       # 保留两者
    DISCARD_NEW = "discard_new"   # 丢弃新记忆


# ============================================================================
# 数据模型
# ============================================================================


class SemanticConflict(BaseModel):
    """语义冲突"""

    conflict_id: str = Field(description="冲突ID")
    memory_a_id: str = Field(description="记忆A的ID")
    memory_a_content: str = Field(description="记忆A的内容")
    memory_b_id: str = Field(description="记忆B的ID")
    memory_b_content: str = Field(description="记忆B的内容")

    # 冲突详情
    similarity_score: float = Field(ge=0.0, le=1.0, description="相似度分数")
    contradiction_score: float = Field(ge=0.0, le=1.0, description="矛盾分数")
    conflict_category: ConflictCategory = Field(description="冲突类别")

    # 分析
    conflict_reason: str = Field(description="冲突原因分析")
    keywords_conflict: list[str] = Field(default_factory=list, description="冲突关键词")

    # 时间
    detected_at: datetime = Field(default_factory=datetime.now, description="检测时间")


class ConflictLogEntry(BaseModel):
    """冲突日志条目"""

    log_id: str = Field(description="日志ID")
    conflict: MemoryConflict = Field(description="冲突对象")
    resolution: ResolutionResult | None = Field(default=None, description="解决结果")
    action_taken: ConflictAction | None = Field(default=None, description="采取的动作")
    user_feedback: str | None = Field(default=None, description="用户反馈")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class ConflictStats(BaseModel):
    """冲突统计"""

    total_conflicts: int = Field(default=0, description="总冲突数")
    resolved_conflicts: int = Field(default=0, description="已解决数")
    pending_conflicts: int = Field(default=0, description="待处理数")

    # 按类别统计
    by_category: dict[str, int] = Field(default_factory=dict, description="按类别统计")
    by_severity: dict[str, int] = Field(default_factory=dict, description="按严重程度统计")

    # 按动作统计
    by_action: dict[str, int] = Field(default_factory=dict, description="按处理动作统计")


class ConflictDetectorConfig(BaseModel):
    """冲突检测器配置"""

    # 相似度阈值（高于此值认为可能冲突）
    similarity_threshold: float = Field(
        ge=0.0, le=1.0, default=0.7, description="相似度阈值"
    )

    # 矛盾阈值（高于此值确认冲突）
    contradiction_threshold: float = Field(
        ge=0.0, le=1.0, default=0.5, description="矛盾阈值"
    )

    # 自动解决高置信度冲突
    auto_resolve_high_confidence: bool = Field(
        default=True, description="自动解决高置信度冲突"
    )

    # 置信度阈值
    auto_resolve_threshold: float = Field(
        ge=0.0, le=1.0, default=0.85, description="自动解决置信度阈值"
    )

    # 最大保留冲突数
    max_log_entries: int = Field(default=100, description="最大日志条目数")


# ============================================================================
# Memory Conflict Detector
# ============================================================================


class MemoryConflictDetector:
    """
    记忆冲突检测器

    实现文档要求："长期记忆和当前任务冲突"

    核心能力：
    1. 显性冲突检测 - 检测明确矛盾的事实
    2. 语义冲突检测 - 检测语义相似但内容矛盾的记忆
    3. 冲突严重程度评估 - 评估冲突的影响程度
    4. 冲突解决策略 - 提供多种解决策略
    5. 冲突日志记录 - 记录冲突历史用于分析

    使用示例：
    ```python
    from scripts.memory_conflict import MemoryConflictDetector

    # 初始化
    detector = MemoryConflictDetector()

    # 检测冲突
    conflicts = detector.detect_all_conflicts(
        new_memory=new_memory_item,
        existing_memories=existing_memories,
        long_term_memory=long_term_memory,
    )

    # 评估冲突严重程度
    for conflict in conflicts:
        severity = detector.assess_severity(conflict)
        print(f"冲突严重程度: {severity.value}")

    # 解决冲突
    if conflicts:
        result = detector.resolve_conflict(
            conflict=conflicts[0],
            mode=ResolutionMode.RECENCY,
        )
        print(f"解决方案: {result.rationale}")

    # 记录冲突日志
    detector.log_conflict(
        conflict=conflicts[0],
        resolution=result,
        action=ConflictAction.OVERRIDE,
    )
    ```
    """

    def __init__(
        self,
        config: ConflictDetectorConfig | None = None,
    ) -> None:
        """
        初始化冲突检测器

        Args:
            config: 配置
        """
        self._config = config or ConflictDetectorConfig()

        # 冲突日志
        self._conflict_log: list[ConflictLogEntry] = []

        # 矛盾词对（用于语义冲突检测）
        self._contradiction_pairs: list[tuple[str, str]] = [
            # 布尔矛盾
            ("是", "否"),
            ("有", "无"),
            ("需要", "不需要"),
            ("应该", "不应该"),
            ("可以", "不可以"),
            ("成功", "失败"),
            ("完成", "未完成"),
            # 程度矛盾
            ("高", "低"),
            ("大", "小"),
            ("快", "慢"),
            ("好", "差"),
            ("强", "弱"),
            # 状态矛盾
            ("开启", "关闭"),
            ("启用", "禁用"),
            ("在线", "离线"),
            ("活跃", "不活跃"),
            # 情感矛盾
            ("喜欢", "不喜欢"),
            ("满意", "不满意"),
            ("积极", "消极"),
            ("乐观", "悲观"),
        ]

        # 关键冲突指标
        self._conflict_indicators = [
            "但是",
            "然而",
            "相反",
            "不是",
            "错误",
            "矛盾",
            "冲突",
            "不符合",
        ]

    # -----------------------------------------------------------------------
    # 核心方法：检测所有冲突
    # -----------------------------------------------------------------------

    def detect_all_conflicts(
        self,
        new_memory: ActivatedMemory | dict[str, Any],
        existing_memories: list[ActivatedMemory],
        long_term_memory: LongTermMemoryContainer | None = None,
    ) -> list[MemoryConflict]:
        """
        检测所有冲突

        检测类型：
        1. 事实冲突 - 明确矛盾的事实
        2. 偏好冲突 - 用户偏好变化
        3. 时效冲突 - 新旧信息冲突
        4. 语义冲突 - 语义相似但内容矛盾

        Args:
            new_memory: 新记忆
            existing_memories: 已有记忆列表
            long_term_memory: 长期记忆容器

        Returns:
            MemoryConflict 列表
        """
        conflicts: list[MemoryConflict] = []

        # 获取新记忆内容
        if isinstance(new_memory, dict):
            new_id = new_memory.get("memory_id", "")
            new_content = new_memory.get("content_summary", "")
            new_type = new_memory.get("memory_type", "")
        else:
            new_id = new_memory.memory_id
            new_content = new_memory.content_summary
            new_type = new_memory.memory_type.value

        # 1. 检测事实冲突
        factual_conflicts = self._detect_factual_conflicts(
            new_id=new_id,
            new_content=new_content,
            existing_memories=existing_memories,
        )
        conflicts.extend(factual_conflicts)

        # 2. 检测偏好冲突
        preference_conflicts = self._detect_preference_conflicts(
            new_id=new_id,
            new_content=new_content,
            existing_memories=existing_memories,
            long_term_memory=long_term_memory,
        )
        conflicts.extend(preference_conflicts)

        # 3. 检测时效冲突
        temporal_conflicts = self._detect_temporal_conflicts(
            new_id=new_id,
            new_content=new_content,
            existing_memories=existing_memories,
        )
        conflicts.extend(temporal_conflicts)

        # 4. 检测语义冲突
        semantic_conflicts = self._detect_semantic_conflicts(
            new_id=new_id,
            new_content=new_content,
            existing_memories=existing_memories,
        )
        conflicts.extend(semantic_conflicts)

        return conflicts

    # -----------------------------------------------------------------------
    # 冲突类型检测
    # -----------------------------------------------------------------------

    def _detect_factual_conflicts(
        self,
        new_id: str,
        new_content: str,
        existing_memories: list[ActivatedMemory],
    ) -> list[MemoryConflict]:
        """
        检测事实冲突

        检测明确矛盾的事实，如：
        - 数值矛盾（年龄、时间、数量）
        - 布尔矛盾（是/否、有/无）
        - 状态矛盾（成功/失败）
        """
        conflicts: list[MemoryConflict] = []

        for mem in existing_memories:
            # 检查矛盾词对
            for word_a, word_b in self._contradiction_pairs:
                if word_a in new_content and word_b in mem.content_summary:
                    # 检查上下文是否相似
                    similarity = self._calculate_similarity(new_content, mem.content_summary)

                    if similarity > self._config.similarity_threshold:
                        conflicts.append(MemoryConflict(
                            conflict_id=f"conf_factual_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            conflict_type=ConflictType.FACTUAL_CONTRADICTION,
                            severity=ConflictSeverity.HIGH,
                            involved_memories=[new_id, mem.memory_id],
                            description=f"事实冲突: '{word_a}' vs '{word_b}'",
                            detected_at=datetime.now(),
                            resolution_mode=ResolutionMode.RECENCY,
                        ))

        return conflicts

    def _detect_preference_conflicts(
        self,
        new_id: str,
        new_content: str,
        existing_memories: list[ActivatedMemory],
        long_term_memory: LongTermMemoryContainer | None,
    ) -> list[MemoryConflict]:
        """
        检测偏好冲突

        检测用户偏好的变化，如：
        - 风格偏好变化
        - 工具选择变化
        - 工作方式变化
        """
        conflicts: list[MemoryConflict] = []

        # 从长期记忆获取偏好
        if long_term_memory and long_term_memory.user_profile:
            preferences = long_term_memory.user_profile.data.preferences

            # 检查新记忆是否与偏好冲突
            # 这里简化处理，实际应该更智能
            preference_keywords = {
                "风格": preferences.get("style", ""),
                "语言": preferences.get("language", ""),
            }

            for key, value in preference_keywords.items():
                if value and key in new_content and value not in new_content:
                    conflicts.append(MemoryConflict(
                        conflict_id=f"conf_pref_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        conflict_type=ConflictType.CONCEPT_AMBIGUITY,
                        severity=ConflictSeverity.LOW,
                        involved_memories=[new_id],
                        description=f"偏好可能变化: {key} 相关",
                        detected_at=datetime.now(),
                        resolution_mode=ResolutionMode.USER_CONFIRMATION,
                    ))

        return conflicts

    def _detect_temporal_conflicts(
        self,
        new_id: str,
        new_content: str,
        existing_memories: list[ActivatedMemory],
    ) -> list[MemoryConflict]:
        """
        检测时效冲突

        检测新旧信息的冲突：
        - 热记忆 vs 冷记忆
        - 近期信息 vs 过时信息
        """
        conflicts: list[MemoryConflict] = []

        for mem in existing_memories:
            # 检查内容相似但时间差异大的记忆
            similarity = self._calculate_similarity(new_content, mem.content_summary)

            if similarity > self._config.similarity_threshold:
                # 检查热度和时间差异
                if mem.heat_level.value == "cold":
                    conflicts.append(MemoryConflict(
                        conflict_id=f"conf_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        conflict_type=ConflictType.TEMPORAL_INVALIDATION,
                        severity=ConflictSeverity.MEDIUM,
                        involved_memories=[new_id, mem.memory_id],
                        description="时效冲突: 新记忆可能覆盖过时信息",
                        detected_at=datetime.now(),
                        resolution_mode=ResolutionMode.RECENCY,
                    ))

        return conflicts

    def _detect_semantic_conflicts(
        self,
        new_id: str,
        new_content: str,
        existing_memories: list[ActivatedMemory],
    ) -> list[MemoryConflict]:
        """
        检测语义冲突

        检测语义相似但内容矛盾的记忆：
        - 相同主题但不同结论
        - 相同问题但不同解决方案
        """
        conflicts: list[MemoryConflict] = []

        for mem in existing_memories:
            # 计算相似度和矛盾度
            similarity = self._calculate_similarity(new_content, mem.content_summary)
            contradiction = self._calculate_contradiction(new_content, mem.content_summary)

            # 高相似度 + 高矛盾度 = 语义冲突
            if similarity > self._config.similarity_threshold and contradiction > self._config.contradiction_threshold:
                conflicts.append(MemoryConflict(
                    conflict_id=f"conf_sem_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    conflict_type=ConflictType.CONCEPT_AMBIGUITY,
                    severity=ConflictSeverity.MEDIUM,
                    involved_memories=[new_id, mem.memory_id],
                    description=f"语义冲突: 相似度{similarity:.2f}, 矛盾度{contradiction:.2f}",
                    detected_at=datetime.now(),
                    resolution_mode=ResolutionMode.CONTEXTUAL,
                ))

        return conflicts

    # -----------------------------------------------------------------------
    # 相似度和矛盾度计算
    # -----------------------------------------------------------------------

    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        """
        计算文本相似度

        使用简化的词频方法计算相似度

        Args:
            text_a: 文本A
            text_b: 文本B

        Returns:
            相似度分数 (0-1)
        """
        # 分词（简单按空格和标点分割）
        words_a = set(self._tokenize(text_a.lower()))
        words_b = set(self._tokenize(text_b.lower()))

        # 停用词过滤
        stop_words = {"的", "是", "在", "了", "和", "与", "或", "这", "那", "我", "你", "他", "她"}
        words_a = words_a - stop_words
        words_b = words_b - stop_words

        if not words_a or not words_b:
            return 0.0

        # Jaccard 相似度
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0

    def _calculate_contradiction(self, text_a: str, text_b: str) -> float:
        """
        计算矛盾度

        基于矛盾词对和冲突指标计算矛盾程度

        Args:
            text_a: 文本A
            text_b: 文本B

        Returns:
            矛盾度分数 (0-1)
        """
        contradiction_score = 0.0
        text_a_lower = text_a.lower()
        text_b_lower = text_b.lower()

        # 检查矛盾词对
        for word_a, word_b in self._contradiction_pairs:
            if (word_a in text_a_lower and word_b in text_b_lower) or \
               (word_b in text_a_lower and word_a in text_b_lower):
                contradiction_score += 0.2

        # 检查冲突指标
        for indicator in self._conflict_indicators:
            if indicator in text_a_lower or indicator in text_b_lower:
                contradiction_score += 0.1

        return min(1.0, contradiction_score)

    def _tokenize(self, text: str) -> list[str]:
        """
        简单分词

        Args:
            text: 输入文本

        Returns:
            词列表
        """
        import re
        # 按非字母数字分割
        tokens = re.split(r'[^\w\u4e00-\u9fff]+', text)
        return [t for t in tokens if t]

    # -----------------------------------------------------------------------
    # 冲突解决
    # -----------------------------------------------------------------------

    def resolve_conflict(
        self,
        conflict: MemoryConflict,
        mode: ResolutionMode | None = None,
        memories: list[ActivatedMemory] | None = None,
    ) -> ResolutionResult:
        """
        解决冲突

        Args:
            conflict: 冲突对象
            mode: 解决模式（可选）
            memories: 记忆列表（用于某些模式）

        Returns:
            ResolutionResult 解决结果
        """
        actual_mode = mode or conflict.resolution_mode

        if actual_mode == ResolutionMode.RECENCY:
            return self._resolve_by_recency(conflict, memories or [])
        elif actual_mode == ResolutionMode.FREQUENCY:
            return self._resolve_by_frequency(conflict, memories or [])
        elif actual_mode == ResolutionMode.USER_CONFIRMATION:
            return self._resolve_by_user_confirmation(conflict)
        elif actual_mode == ResolutionMode.SOURCE_TRUST:
            return self._resolve_by_trust(conflict, memories or [])
        elif actual_mode == ResolutionMode.CONTEXTUAL:
            return self._resolve_by_context(conflict, memories or [])
        else:
            return self._resolve_by_recency(conflict, memories or [])

    def _resolve_by_recency(
        self,
        conflict: MemoryConflict,
        memories: list[ActivatedMemory],
    ) -> ResolutionResult:
        """基于新近性解决"""
        involved_ids = set(conflict.involved_memories)

        # 选择第一个（通常是最新的）
        winning_memory = conflict.involved_memories[0] if conflict.involved_memories else ""

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_mode=ResolutionMode.RECENCY,
            winning_memory=winning_memory,
            losing_memories=[mid for mid in involved_ids if mid != winning_memory],
            confidence=0.7,
            rationale="选择最新记忆",
            user_required=False,
        )

    def _resolve_by_frequency(
        self,
        conflict: MemoryConflict,
        memories: list[ActivatedMemory],
    ) -> ResolutionResult:
        """基于频率解决"""
        involved_ids = set(conflict.involved_memories)

        # 简化：选择热度高的
        winning_memory = ""
        max_score = 0.0

        for mem in memories:
            if mem.memory_id in involved_ids:
                score = mem.relevance_score
                if score > max_score:
                    max_score = score
                    winning_memory = mem.memory_id

        if not winning_memory and conflict.involved_memories:
            winning_memory = conflict.involved_memories[0]

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_mode=ResolutionMode.FREQUENCY,
            winning_memory=winning_memory,
            losing_memories=[mid for mid in involved_ids if mid != winning_memory],
            confidence=0.65,
            rationale="选择使用频率更高的记忆",
            user_required=False,
        )

    def _resolve_by_user_confirmation(
        self,
        conflict: MemoryConflict,
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
        self,
        conflict: MemoryConflict,
        memories: list[ActivatedMemory],
    ) -> ResolutionResult:
        """基于可信度解决"""
        involved_ids = set(conflict.involved_memories)

        # 计算可信度
        trust_scores: dict[str, float] = {}
        for mem in memories:
            if mem.memory_id in involved_ids:
                trust = mem.relevance_score
                if mem.heat_level.value == "hot":
                    trust += 0.2
                trust_scores[mem.memory_id] = trust

        winning_memory = max(
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
            rationale="选择可信度更高的记忆",
            user_required=False,
        )

    def _resolve_by_context(
        self,
        conflict: MemoryConflict,
        memories: list[ActivatedMemory],
    ) -> ResolutionResult:
        """基于上下文相关性解决"""
        involved_ids = set(conflict.involved_memories)

        # 选择相关性最高的
        relevance_scores: dict[str, float] = {}
        for mem in memories:
            if mem.memory_id in involved_ids:
                relevance_scores[mem.memory_id] = mem.relevance_score

        winning_memory = max(
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
            rationale="选择与当前上下文更相关的记忆",
            user_required=False,
        )

    # -----------------------------------------------------------------------
    # 冲突严重程度评估
    # -----------------------------------------------------------------------

    def assess_severity(self, conflict: MemoryConflict) -> ConflictSeverity:
        """
        评估冲突严重程度

        基于以下因素：
        1. 冲突类型
        2. 涉及记忆数量
        3. 冲突描述

        Args:
            conflict: 冲突对象

        Returns:
            ConflictSeverity 严重程度
        """
        # 事实冲突通常较严重
        if conflict.conflict_type == ConflictType.FACTUAL_CONTRADICTION:
            return ConflictSeverity.HIGH

        # 时效冲突中等严重
        if conflict.conflict_type == ConflictType.TEMPORAL_INVALIDATION:
            return ConflictSeverity.MEDIUM

        # 情感冲突较低
        if conflict.conflict_type == ConflictType.EMOTIONAL_INCONSISTENCY:
            return ConflictSeverity.LOW

        # 默认
        return conflict.severity

    # -----------------------------------------------------------------------
    # 冲突日志
    # -----------------------------------------------------------------------

    def log_conflict(
        self,
        conflict: MemoryConflict,
        resolution: ResolutionResult | None = None,
        action: ConflictAction | None = None,
        user_feedback: str | None = None,
    ) -> ConflictLogEntry:
        """
        记录冲突日志

        Args:
            conflict: 冲突对象
            resolution: 解决结果
            action: 采取的动作
            user_feedback: 用户反馈

        Returns:
            ConflictLogEntry 日志条目
        """
        entry = ConflictLogEntry(
            log_id=f"log_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            conflict=conflict,
            resolution=resolution,
            action=action,
            user_feedback=user_feedback,
        )

        self._conflict_log.append(entry)

        # 限制日志大小
        if len(self._conflict_log) > self._config.max_log_entries:
            self._conflict_log = self._conflict_log[-self._config.max_log_entries:]

        return entry

    def get_conflict_stats(self) -> ConflictStats:
        """
        获取冲突统计

        Returns:
            ConflictStats 统计信息
        """
        stats = ConflictStats(
            total_conflicts=len(self._conflict_log),
            resolved_conflicts=sum(1 for e in self._conflict_log if e.resolution),
            pending_conflicts=sum(1 for e in self._conflict_log if not e.resolution),
        )

        # 按类别统计
        for entry in self._conflict_log:
            category = entry.conflict.conflict_type.value
            stats.by_category[category] = stats.by_category.get(category, 0) + 1

        # 按严重程度统计
        for entry in self._conflict_log:
            severity = entry.conflict.severity.value
            stats.by_severity[severity] = stats.by_severity.get(severity, 0) + 1

        # 按动作统计
        for entry in self._conflict_log:
            if entry.action:
                action = entry.action.value
                stats.by_action[action] = stats.by_action.get(action, 0) + 1

        return stats

    def get_recent_conflicts(self, limit: int = 10) -> list[ConflictLogEntry]:
        """
        获取最近的冲突

        Args:
            limit: 最大数量

        Returns:
            ConflictLogEntry 列表
        """
        return self._conflict_log[-limit:]

    # -----------------------------------------------------------------------
    # 合并记忆
    # -----------------------------------------------------------------------

    def merge_memories(
        self,
        memory_ids: list[str],
        memories: list[ActivatedMemory],
        merge_strategy: str = "combine",
    ) -> str:
        """
        合并多个记忆

        Args:
            memory_ids: 要合并的记忆ID列表
            memories: 记忆列表
            merge_strategy: 合并策略（combine, latest, most_detailed）

        Returns:
            合并后的内容
        """
        contents: list[str] = []

        for mem in memories:
            if mem.memory_id in memory_ids:
                contents.append(mem.content_summary)

        if merge_strategy == "combine":
            return " | ".join(contents)
        elif merge_strategy == "latest":
            return contents[0] if contents else ""
        elif merge_strategy == "most_detailed":
            return max(contents, key=len) if contents else ""
        else:
            return " | ".join(contents)


# ============================================================================
# 工厂函数
# ============================================================================


def create_memory_conflict_detector(
    similarity_threshold: float = 0.7,
    contradiction_threshold: float = 0.5,
) -> MemoryConflictDetector:
    """
    创建记忆冲突检测器

    Args:
        similarity_threshold: 相似度阈值
        contradiction_threshold: 矛盾阈值

    Returns:
        MemoryConflictDetector 实例
    """
    config = ConflictDetectorConfig(
        similarity_threshold=similarity_threshold,
        contradiction_threshold=contradiction_threshold,
    )

    return MemoryConflictDetector(config=config)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "ConflictCategory",
    "ConflictAction",
    "SemanticConflict",
    "ConflictLogEntry",
    "ConflictStats",
    "ConflictDetectorConfig",
    "MemoryConflictDetector",
    "create_memory_conflict_detector",
]

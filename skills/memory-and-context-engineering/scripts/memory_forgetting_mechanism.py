"""
Agent Memory System - Memory Forgetting Mechanism（记忆遗忘机制）

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  ```
=== 声明结束 ===

核心理念：
智能遗忘机制，保持记忆库的精简和高质量。
遗忘不是删除，而是降低权重、归档冷数据。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class MemoryImportance(str, Enum):
    """记忆重要性"""

    CRITICAL = "critical"        # 关键：永不遗忘
    HIGH = "high"                # 高：长期保留
    MEDIUM = "medium"            # 中：中期保留
    LOW = "low"                  # 低：短期保留
    TRIVIAL = "trivial"          # 琐碎：快速遗忘


class ForgettingTrigger(str, Enum):
    """遗忘触发因素"""

    TIME_DECAY = "time_decay"                # 时间衰减
    LOW_ACCESS = "low_access"                # 低访问
    REDUNDANCY = "redundancy"                # 冗余
    IRRELEVANCE = "irrelevance"              |  # 不相关
    CONFLICT = "conflict"                    # 冲突
    EXPLICIT = "explicit"                    # 显式标记


class ForgettingAction(str, Enum):
    """遗忘动作"""

    ARCHIVE = "archive"          # 归档：移至冷存储
    DEPRIORITIZE = "deprioritize"  # 降权：降低访问优先级
    MERGE = "merge"              # 合并：与相似记忆合并
    DELETE = "delete"            # 删除：完全移除
    KEEP = "keep"                # 保留：不做处理


class MemoryState(str, Enum):
    """记忆状态"""

    ACTIVE = "active"            # 活跃
    DORMANT = "dormant"          |  # 休眠
    ARCHIVED = "archived"        # 已归档
    DELETED = "deleted"          # 已删除


# ============================================================================
# 数据模型
# ============================================================================


class MemoryMetadata(BaseModel):
    """记忆元数据"""

    memory_id: str

    # 访问统计
    access_count: int = Field(default=0)
    last_accessed: datetime | None = None

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # 重要性
    importance: MemoryImportance = Field(default=MemoryImportance.MEDIUM)
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)

    # 当前状态
    state: MemoryState = Field(default=MemoryState.ACTIVE)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class ForgettingCandidate(BaseModel):
    """遗忘候选"""

    memory_id: str
    score: float = Field(ge=0.0, le=1.0, description="遗忘分数（越高越该遗忘）")
    triggers: list[ForgettingTrigger] = Field(default_factory=list)
    suggested_action: ForgettingAction = Field(default=ForgettingAction.DEPRIORITIZE)
    reason: str = Field(default="")

    created_at: datetime = Field(default_factory=datetime.now)


class ForgettingDecision(BaseModel):
    """遗忘决策"""

    decision_id: str = Field(
        default_factory=lambda: f"forget_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )

    # 决策
    action: ForgettingAction = Field(default=ForgettingAction.KEEP)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    # 理由
    reason: str = Field(default="")

    # 影响
    affected_count: int = Field(default=0)
    freed_space: int = Field(default=0)  # bytes

    created_at: datetime = Field(default_factory=datetime.now)


class ForgettingReport(BaseModel):
    """遗忘报告"""

    # 统计
    total_memories: int = Field(default=0)
    active_memories: int = Field(default=0)
    dormant_memories: int = Field(default=0)
    archived_memories: int = Field(default=0)

    # 候选
    candidates: list[ForgettingCandidate] = Field(default_factory=list)

    # 决策
    decisions: list[ForgettingDecision] = Field(default_factory=list)

    # 效果
    space_before: int = Field(default=0)
    space_after: int = Field(default=0)
    compression_ratio: float = Field(default=0.0)

    # 元数据
    report_id: str = Field(
        default_factory=lambda: f"report_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class ForgettingConfig(BaseModel):
    """遗忘机制配置"""

    # 时间衰减
    time_decay_factor: float = Field(default=0.9, description="时间衰减系数")
    half_life_days: int = Field(default=30, description="半衰期（天）")

    # 访问衰减
    access_weight: float = Field(default=0.3, description="访问频率权重")
    min_access_threshold: int = Field(default=3, description="最小访问次数阈值")

    # 遗忘阈值
    forget_threshold: float = Field(default=0.7, description="遗忘阈值")
    archive_threshold: float = Field(default=0.5, description="归档阈值")

    # 保护规则
    protect_critical: bool = Field(default=True, description="保护关键记忆")
    protect_recent_days: int = Field(default=7, description="保护最近N天的记忆")

    # 批处理
    batch_size: int = Field(default=100, description="批处理大小")
    max_forget_per_cycle: int = Field(default=1000, description="每周期最大遗忘数量")


# ============================================================================
# Memory Forgetting Mechanism
# ============================================================================


class MemoryForgettingMechanism:
    """
    记忆遗忘机制

    职责：
    - 识别应遗忘的记忆
    - 执行遗忘决策
    - 维护记忆库健康

    使用示例：
    ```python
    from scripts.memory_forgetting_mechanism import MemoryForgettingMechanism

    mechanism = MemoryForgettingMechanism()

    # 注册记忆
    mechanism.register_memory(
        memory_id="mem_1",
        importance="medium",
        created_at=datetime.now() - timedelta(days=60),
    )

    # 分析遗忘候选
    candidates = mechanism.analyze_forgetting_candidates()
    print(f"发现 {len(candidates)} 个遗忘候选")

    # 执行遗忘
    report = mechanism.execute_forgetting(candidates)
    print(f"压缩率: {report.compression_ratio:.0%}")
    ```
    """

    def __init__(self, config: ForgettingConfig | None = None):
        """初始化遗忘机制"""
        self._config = config or ForgettingConfig()
        self._memories: dict[str, MemoryMetadata] = {}

    # -----------------------------------------------------------------------
    # 记忆管理
    # -----------------------------------------------------------------------

    def register_memory(
        self,
        memory_id: str,
        importance: MemoryImportance | str = MemoryImportance.MEDIUM,
        importance_score: float = 0.5,
    ) -> None:
        """注册记忆"""
        if isinstance(importance, str):
            importance = MemoryImportance(importance)

        metadata = MemoryMetadata(
            memory_id=memory_id,
            importance=importance,
            importance_score=importance_score,
        )
        self._memories[memory_id] = metadata

    def access_memory(self, memory_id: str) -> None:
        """记录记忆访问"""
        if memory_id in self._memories:
            metadata = self._memories[memory_id]
            metadata.access_count += 1
            metadata.last_accessed = datetime.now()
            metadata.updated_at = datetime.now()

    def update_importance(
        self,
        memory_id: str,
        importance: MemoryImportance,
    ) -> bool:
        """更新记忆重要性"""
        if memory_id not in self._memories:
            return False

        self._memories[memory_id].importance = importance
        self._memories[memory_id].updated_at = datetime.now()
        return True

    # -----------------------------------------------------------------------
    # 遗忘分析
    # -----------------------------------------------------------------------

    def analyze_forgetting_candidates(self) -> list[ForgettingCandidate]:
        """分析遗忘候选"""
        candidates: list[ForgettingCandidate] = []

        for memory_id, metadata in self._memories.items():
            # 跳过受保护的记忆
            if self._is_protected(metadata):
                continue

            # 计算遗忘分数
            score, triggers = self._compute_forgetting_score(metadata)

            # 判断是否为候选
            if score >= self._config.forget_threshold:
                action = self._determine_action(score, metadata)
                candidate = ForgettingCandidate(
                    memory_id=memory_id,
                    score=score,
                    triggers=triggers,
                    suggested_action=action,
                    reason=self._generate_reason(score, triggers),
                )
                candidates.append(candidate)

        # 按分数排序
        candidates.sort(key=lambda c: c.score, reverse=True)

        return candidates[:self._config.max_forget_per_cycle]

    def _is_protected(self, metadata: MemoryMetadata) -> bool:
        """检查是否受保护"""
        # 关键记忆保护
        if self._config.protect_critical and metadata.importance == MemoryImportance.CRITICAL:
            return True

        # 最近记忆保护
        if self._config.protect_recent_days > 0:
            recent_cutoff = datetime.now() - timedelta(days=self._config.protect_recent_days)
            if metadata.created_at > recent_cutoff:
                return True

        return False

    def _compute_forgetting_score(
        self,
        metadata: MemoryMetadata,
    ) -> tuple[float, list[ForgettingTrigger]]:
        """计算遗忘分数"""
        score = 0.0
        triggers: list[ForgettingTrigger] = []

        # 时间衰减
        age_days = (datetime.now() - metadata.created_at).days
        time_score = self._time_decay(age_days)
        if time_score > 0.5:
            score += time_score * 0.4
            triggers.append(ForgettingTrigger.TIME_DECAY)

        # 访问频率
        if metadata.access_count < self._config.min_access_threshold:
            access_score = 1 - (metadata.access_count / self._config.min_access_threshold)
            score += access_score * self._config.access_weight
            triggers.append(ForgettingTrigger.LOW_ACCESS)

        # 重要性反向权重
        importance_scores = {
            MemoryImportance.CRITICAL: 0.0,
            MemoryImportance.HIGH: 0.2,
            MemoryImportance.MEDIUM: 0.5,
            MemoryImportance.LOW: 0.7,
            MemoryImportance.TRIVIAL: 0.9,
        }
        imp_score = importance_scores.get(metadata.importance, 0.5)
        if imp_score > 0.5:
            score += imp_score * 0.3
            if metadata.importance == MemoryImportance.TRIVIAL:
                triggers.append(ForgettingTrigger.TRIVIAL)

        return min(1.0, score), triggers

    def _time_decay(self, age_days: int) -> float:
        """时间衰减函数"""
        # 指数衰减
        decay = (self._config.time_decay_factor ** (age_days / self._config.half_life_days))
        return 1 - decay

    def _determine_action(
        self,
        score: float,
        metadata: MemoryMetadata,
    ) -> ForgettingAction:
        """确定遗忘动作"""
        if score >= 0.9:
            return ForgettingAction.DELETE
        elif score >= 0.7:
            return ForgettingAction.ARCHIVE
        elif score >= 0.5:
            return ForgettingAction.DEPRIORITIZE
        else:
            return ForgettingAction.KEEP

    def _generate_reason(
        self,
        score: float,
        triggers: list[ForgettingTrigger],
    ) -> str:
        """生成遗忘理由"""
        trigger_names = {
            ForgettingTrigger.TIME_DECAY: "时间衰减",
            ForgettingTrigger.LOW_ACCESS: "低访问频率",
            ForgettingTrigger.REDUNDANCY: "冗余",
            ForgettingTrigger.IRRELEVANCE: "不相关",
            ForgettingTrigger.CONFLICT: "冲突",
            ForgettingTrigger.EXPLICIT: "显式标记",
        }

        trigger_str = "、".join(trigger_names.get(t, str(t)) for t in triggers)
        return f"遗忘分数 {score:.2f}，触发因素：{trigger_str}"

    # -----------------------------------------------------------------------
    # 遗忘执行
    # -----------------------------------------------------------------------

    def execute_forgetting(
        self,
        candidates: list[ForgettingCandidate] | None = None,
    ) -> ForgettingReport:
        """执行遗忘"""
        if candidates is None:
            candidates = self.analyze_forgetting_candidates()

        decisions: list[ForgettingDecision] = []
        affected_count = 0

        for candidate in candidates[:self._config.batch_size]:
            decision = self._execute_single(candidate)
            decisions.append(decision)

            if decision.action != ForgettingAction.KEEP:
                affected_count += 1

        # 生成报告
        report = ForgettingReport(
            total_memories=len(self._memories),
            active_memories=sum(
                1 for m in self._memories.values()
                if m.state == MemoryState.ACTIVE
            ),
            dormant_memories=sum(
                1 for m in self._memories.values()
                if m.state == MemoryState.DORMANT
            ),
            archived_memories=sum(
                1 for m in self._memories.values()
                if m.state == MemoryState.ARCHIVED
            ),
            candidates=candidates,
            decisions=decisions,
            affected_count=affected_count,
        )

        return report

    def _execute_single(self, candidate: ForgettingCandidate) -> ForgettingDecision:
        """执行单个遗忘决策"""
        memory_id = candidate.memory_id

        if memory_id not in self._memories:
            return ForgettingDecision(
                action=ForgettingAction.KEEP,
                reason="记忆不存在",
            )

        metadata = self._memories[memory_id]
        action = candidate.suggested_action

        # 执行动作
        if action == ForgettingAction.ARCHIVE:
            metadata.state = MemoryState.ARCHIVED
            metadata.weight = 0.3
        elif action == ForgettingAction.DEPRIORITIZE:
            metadata.state = MemoryState.DORMANT
            metadata.weight = 0.5
        elif action == ForgettingAction.DELETE:
            metadata.state = MemoryState.DELETED
            metadata.weight = 0.0

        metadata.updated_at = datetime.now()

        return ForgettingDecision(
            action=action,
            confidence=1 - candidate.score,
            reason=candidate.reason,
            affected_count=1,
        )

    # -----------------------------------------------------------------------
    # 维护操作
    # -----------------------------------------------------------------------

    def restore_memory(self, memory_id: str) -> bool:
        """恢复记忆"""
        if memory_id not in self._memories:
            return False

        metadata = self._memories[memory_id]
        metadata.state = MemoryState.ACTIVE
        metadata.weight = 1.0
        metadata.updated_at = datetime.now()

        return True

    def mark_as_critical(self, memory_id: str) -> bool:
        """标记为关键记忆"""
        return self.update_importance(memory_id, MemoryImportance.CRITICAL)

    def cleanup_deleted(self) -> int:
        """清理已删除的记忆"""
        to_delete = [
            mid for mid, m in self._memories.items()
            if m.state == MemoryState.DELETED
        ]

        for mid in to_delete:
            del self._memories[mid]

        return len(to_delete)

    # -----------------------------------------------------------------------
    # 统计
    # -----------------------------------------------------------------------

    def get_statistics(self) -> dict[str, Any]:
        """获取统计信息"""
        states = {
            MemoryState.ACTIVE: 0,
            MemoryState.DORMANT: 0,
            MemoryState.ARCHIVED: 0,
            MemoryState.DELETED: 0,
        }

        for metadata in self._memories.values():
            states[metadata.state] += 1

        return {
            "total": len(self._memories),
            "by_state": states,
            "by_importance": {
                imp.value: sum(
                    1 for m in self._memories.values()
                    if m.importance == imp
                )
                for imp in MemoryImportance
            },
        }


# ============================================================================
# 工厂函数
# ============================================================================


def create_forgetting_mechanism() -> MemoryForgettingMechanism:
    """创建记忆遗忘机制"""
    return MemoryForgettingMechanism()


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "MemoryImportance",
    "ForgettingTrigger",
    "ForgettingAction",
    "MemoryState",
    "MemoryMetadata",
    "ForgettingCandidate",
    "ForgettingDecision",
    "ForgettingReport",
    "ForgettingConfig",
    "MemoryForgettingMechanism",
    "create_forgetting_mechanism",
]

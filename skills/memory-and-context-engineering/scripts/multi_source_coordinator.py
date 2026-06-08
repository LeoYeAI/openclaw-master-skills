"""
Agent Memory System - Multi-Source Coordinator（多源协调器）

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

安全提醒：作为总控层协调器，需确保所有来源的安全性和一致性
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class SourceType(str, Enum):
    """九类上下文来源
    
    按优先级从高到低排列
    """

    SYSTEM_INSTRUCTION = "system_instruction"      # 1. 系统指令 - 定义行为边界
    USER_QUERY = "user_query"                      # 2. 用户当前问题 - 触发点
    CONVERSATION_HISTORY = "conversation_history"  # 3. 历史对话 - 决策轨迹
    RETRIEVAL_RESULT = "retrieval_result"          # 4. 检索结果 - 知识补充
    TOOL_OUTPUT = "tool_output"                    # 5. 工具返回 - 执行结果
    TASK_STATE = "task_state"                      # 6. 任务状态 - 进度追踪
    USER_PREFERENCE = "user_preference"            # 7. 用户偏好 - 个性化
    LONG_TERM_MEMORY = "long_term_memory"          # 8. 长期记忆 - 持续协作
    PERMISSION_CONSTRAINT = "permission_constraint" # 9. 权限约束 - 安全边界


class ConflictType(str, Enum):
    """来源冲突类型"""

    PRIORITY_CONFLICT = "priority_conflict"      # 优先级冲突
    CONTENT_CONTRADICTION = "content_contradiction"  # 内容矛盾
    TEMPORAL_CONFLICT = "temporal_conflict"      # 时间冲突
    SCOPE_CONFLICT = "scope_conflict"            # 范围冲突
    PERMISSION_CONFLICT = "permission_conflict"  # 权限冲突


class ResolutionStrategy(str, Enum):
    """冲突解决策略"""

    HIGHEST_PRIORITY = "highest_priority"        # 最高优先级优先
    RECENCY = "recency"                          # 最新内容优先
    USER_PREFERENCE = "user_preference"          # 用户偏好优先
    SAFETY_FIRST = "safety_first"                # 安全优先
    CONTEXTUAL = "contextual"                    # 上下文相关决策


# ============================================================================
# 数据模型
# ============================================================================


class SourcePriority(BaseModel):
    """来源优先级配置"""

    source: SourceType
    base_priority: int = Field(ge=1, le=100, description="基础优先级（1-100）")
    dynamic_boost: float = Field(default=0.0, ge=0.0, le=50.0, description="动态提升")
    max_priority: int = Field(default=100, ge=1, le=100)

    @property
    def effective_priority(self) -> int:
        """计算有效优先级"""
        return min(
            self.max_priority,
            int(self.base_priority + self.dynamic_boost)
        )


class SourceContent(BaseModel):
    """来源内容"""

    source: SourceType
    content: str
    token_count: int = Field(default=0)
    priority: int = Field(default=50)
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    freshness_score: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class ConflictRecord(BaseModel):
    """冲突记录"""

    conflict_id: str = Field(
        default_factory=lambda: f"conflict_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    conflict_type: ConflictType
    sources_involved: list[SourceType]
    description: str
    severity: str = Field(default="medium")  # low, medium, high, critical
    resolution: ResolutionStrategy
    resolved_content: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class CoordinatorConfig(BaseModel):
    """协调器配置"""

    # 默认优先级配置
    default_priorities: dict[SourceType, int] = Field(
        default_factory=lambda: {
            SourceType.SYSTEM_INSTRUCTION: 100,
            SourceType.USER_QUERY: 95,
            SourceType.CONVERSATION_HISTORY: 80,
            SourceType.RETRIEVAL_RESULT: 70,
            SourceType.TOOL_OUTPUT: 75,
            SourceType.TASK_STATE: 85,
            SourceType.USER_PREFERENCE: 60,
            SourceType.LONG_TERM_MEMORY: 50,
            SourceType.PERMISSION_CONSTRAINT: 99,
        }
    )

    # 冲突解决策略
    default_resolution_strategy: ResolutionStrategy = Field(
        default=ResolutionStrategy.HIGHEST_PRIORITY
    )

    # 动态优先级调整
    enable_dynamic_priority: bool = Field(default=True)
    relevance_boost_factor: float = Field(default=10.0)
    freshness_boost_factor: float = Field(default=5.0)

    # 冲突检测
    enable_conflict_detection: bool = Field(default=True)


class CoordinatedContext(BaseModel):
    """协调后的上下文"""

    # 最终内容
    content: str
    token_count: int = Field(default=0)

    # 来源明细
    sources_used: list[SourceContent] = Field(default_factory=list)
    sources_excluded: list[SourceType] = Field(default_factory=list)

    # 冲突信息
    conflicts_detected: list[ConflictRecord] = Field(default_factory=list)

    # 统计
    stats: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Multi-Source Coordinator
# ============================================================================


class MultiSourceCoordinator:
    """
    多源协调器
    
    职责：
    - 统一协调9类上下文来源
    - 动态调整来源优先级
    - 检测和解决来源冲突
    - 生成协调后的上下文
    
    使用示例：
    ```python
    from scripts.multi_source_coordinator import MultiSourceCoordinator

    coordinator = MultiSourceCoordinator()

    # 注册来源
    coordinator.register_source(
        source_type=SourceType.USER_QUERY,
        content="帮我分析这段代码",
        relevance_score=0.9,
    )

    # 协调上下文
    context = coordinator.coordinate(max_tokens=8000)
    print(f"协调后内容: {context.content}")
    ```
    """

    def __init__(self, config: CoordinatorConfig | None = None):
        """初始化多源协调器"""
        self._config = config or CoordinatorConfig()
        self._sources: dict[SourceType, list[SourceContent]] = {}
        self._priorities: dict[SourceType, SourcePriority] = {}
        self._conflicts: list[ConflictRecord] = []

        # 初始化优先级
        for source, priority in self._config.default_priorities.items():
            self._priorities[source] = SourcePriority(
                source=source,
                base_priority=priority,
            )

    # -----------------------------------------------------------------------
    # 来源注册
    # -----------------------------------------------------------------------

    def register_source(
        self,
        source_type: SourceType,
        content: str,
        token_count: int | None = None,
        relevance_score: float = 0.5,
        freshness_score: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        注册上下文来源

        Args:
            source_type: 来源类型
            content: 内容
            token_count: Token 数量（可选，自动估算）
            relevance_score: 相关性分数
            freshness_score: 新鲜度分数
            metadata: 元数据

        Returns:
            内容 ID
        """
        if source_type not in self._sources:
            self._sources[source_type] = []

        # 估算 token
        if token_count is None:
            token_count = len(content) // 4

        # 动态调整优先级
        if self._config.enable_dynamic_priority:
            self._adjust_priority(source_type, relevance_score, freshness_score)

        source_content = SourceContent(
            source=source_type,
            content=content,
            token_count=token_count,
            priority=self._priorities[source_type].effective_priority,
            relevance_score=relevance_score,
            freshness_score=freshness_score,
            metadata=metadata or {},
        )

        self._sources[source_type].append(source_content)
        return f"{source_type.value}_{len(self._sources[source_type])}"

    def register_provider(
        self,
        source_type: SourceType,
        provider: Callable[[], list[tuple[str, dict[str, Any]]]],
    ) -> None:
        """
        注册来源提供者

        Args:
            source_type: 来源类型
            provider: 提供者函数，返回 (content, metadata) 列表
        """
        try:
            items = provider()
            for content, metadata in items:
                self.register_source(
                    source_type=source_type,
                    content=content,
                    **metadata,
                )
        except Exception:
            pass

    def clear_sources(self) -> None:
        """清空所有来源"""
        self._sources.clear()
        self._conflicts.clear()

    # -----------------------------------------------------------------------
    # 优先级管理
    # -----------------------------------------------------------------------

    def _adjust_priority(
        self,
        source_type: SourceType,
        relevance_score: float,
        freshness_score: float,
    ) -> None:
        """动态调整优先级"""
        if source_type not in self._priorities:
            return

        priority = self._priorities[source_type]
        
        # 基于相关性和新鲜度提升
        relevance_boost = relevance_score * self._config.relevance_boost_factor
        freshness_boost = freshness_score * self._config.freshness_boost_factor
        
        priority.dynamic_boost = relevance_boost + freshness_boost

    def set_priority(
        self,
        source_type: SourceType,
        base_priority: int,
    ) -> None:
        """设置来源优先级"""
        if source_type in self._priorities:
            self._priorities[source_type].base_priority = base_priority

    def get_priority(self, source_type: SourceType) -> int:
        """获取来源有效优先级"""
        if source_type in self._priorities:
            return self._priorities[source_type].effective_priority
        return 50

    # -----------------------------------------------------------------------
    # 冲突检测与解决
    # -----------------------------------------------------------------------

    def _detect_conflicts(self) -> list[ConflictRecord]:
        """检测来源冲突"""
        conflicts: list[ConflictRecord] = []

        if not self._config.enable_conflict_detection:
            return conflicts

        # 1. 优先级冲突检测
        conflicts.extend(self._detect_priority_conflicts())

        # 2. 内容矛盾检测
        conflicts.extend(self._detect_content_contradictions())

        # 3. 权限冲突检测
        conflicts.extend(self._detect_permission_conflicts())

        return conflicts

    def _detect_priority_conflicts(self) -> list[ConflictRecord]:
        """检测优先级冲突"""
        conflicts: list[ConflictRecord] = []

        # 检查相同优先级的来源
        priority_groups: dict[int, list[SourceType]] = {}
        for source_type, priority in self._priorities.items():
            p = priority.effective_priority
            if p not in priority_groups:
                priority_groups[p] = []
            priority_groups[p].append(source_type)

        for priority, sources in priority_groups.items():
            if len(sources) > 2:  # 允许少量同优先级
                conflicts.append(ConflictRecord(
                    conflict_type=ConflictType.PRIORITY_CONFLICT,
                    sources_involved=sources,
                    description=f"多个来源具有相同优先级 {priority}",
                    severity="low",
                    resolution=ResolutionStrategy.HIGHEST_PRIORITY,
                ))

        return conflicts

    def _detect_content_contradictions(self) -> list[ConflictRecord]:
        """检测内容矛盾"""
        conflicts: list[ConflictRecord] = []

        # 获取系统指令和用户查询
        system_contents = self._sources.get(SourceType.SYSTEM_INSTRUCTION, [])
        user_contents = self._sources.get(SourceType.USER_QUERY, [])

        # 简单的矛盾检测（关键词匹配）
        contradiction_keywords = [
            ("禁止", "允许"),
            ("不要", "要"),
            ("不能", "可以"),
            ("必须", "可选"),
        ]

        for neg, pos in contradiction_keywords:
            for sys_content in system_contents:
                if neg in sys_content.content:
                    for user_content in user_contents:
                        if pos in user_content.content:
                            conflicts.append(ConflictRecord(
                                conflict_type=ConflictType.CONTENT_CONTRADICTION,
                                sources_involved=[
                                    SourceType.SYSTEM_INSTRUCTION,
                                    SourceType.USER_QUERY,
                                ],
                                description=f"潜在矛盾: 系统指令包含'{neg}'，用户查询包含'{pos}'",
                                severity="medium",
                                resolution=ResolutionStrategy.SAFETY_FIRST,
                            ))

        return conflicts

    def _detect_permission_conflicts(self) -> list[ConflictRecord]:
        """检测权限冲突"""
        conflicts: list[ConflictRecord] = []

        # 检查权限约束与其他来源的冲突
        permission_contents = self._sources.get(SourceType.PERMISSION_CONSTRAINT, [])

        if not permission_contents:
            return conflicts

        # 检查是否有来源被权限约束限制
        for perm_content in permission_contents:
            restricted_keywords = ["禁止访问", "不可见", "敏感信息"]
            for keyword in restricted_keywords:
                if keyword in perm_content.content:
                    # 检查其他来源是否包含受限内容
                    for source_type, contents in self._sources.items():
                        if source_type == SourceType.PERMISSION_CONSTRAINT:
                            continue
                        for content in contents:
                            if keyword in content.content:
                                conflicts.append(ConflictRecord(
                                    conflict_type=ConflictType.PERMISSION_CONFLICT,
                                    sources_involved=[
                                        SourceType.PERMISSION_CONSTRAINT,
                                        source_type,
                                    ],
                                    description=f"权限冲突: 来源 {source_type.value} 可能包含受限内容",
                                    severity="high",
                                    resolution=ResolutionStrategy.SAFETY_FIRST,
                                ))

        return conflicts

    def _resolve_conflict(
        self,
        conflict: ConflictRecord,
    ) -> str:
        """解决冲突"""
        strategy = conflict.resolution

        if strategy == ResolutionStrategy.SAFETY_FIRST:
            # 安全优先：权限约束最高
            if SourceType.PERMISSION_CONSTRAINT in conflict.sources_involved:
                return "apply_permission_constraint"

        elif strategy == ResolutionStrategy.HIGHEST_PRIORITY:
            # 最高优先级优先
            max_priority = 0
            winner = None
            for source in conflict.sources_involved:
                priority = self.get_priority(source)
                if priority > max_priority:
                    max_priority = priority
                    winner = source
            return f"priority_winner:{winner.value}" if winner else "no_resolution"

        elif strategy == ResolutionStrategy.RECENCY:
            # 最新内容优先
            return "use_most_recent"

        elif strategy == ResolutionStrategy.USER_PREFERENCE:
            # 用户偏好优先
            if SourceType.USER_PREFERENCE in conflict.sources_involved:
                return "user_preference_wins"

        return "no_resolution"

    # -----------------------------------------------------------------------
    # 核心方法：协调上下文
    # -----------------------------------------------------------------------

    def coordinate(
        self,
        max_tokens: int = 32000,
        resolution_strategy: ResolutionStrategy | None = None,
    ) -> CoordinatedContext:
        """
        协调所有来源，生成最终上下文

        Args:
            max_tokens: 最大 Token 数
            resolution_strategy: 冲突解决策略（可选）

        Returns:
            CoordinatedContext 协调后的上下文
        """
        # 检测冲突
        conflicts = self._detect_conflicts()
        self._conflicts.extend(conflicts)

        # 解决冲突
        for conflict in conflicts:
            resolution = self._resolve_conflict(conflict)
            conflict.resolved_content = resolution

        # 收集所有内容
        all_contents: list[SourceContent] = []
        for contents in self._sources.values():
            all_contents.extend(contents)

        # 按优先级排序
        sorted_contents = sorted(
            all_contents,
            key=lambda c: (-c.priority, -c.relevance_score, -c.freshness_score),
        )

        # 应用 Token 预算
        selected_contents: list[SourceContent] = []
        excluded_sources: list[SourceType] = []
        current_tokens = 0

        for content in sorted_contents:
            if current_tokens + content.token_count <= max_tokens:
                selected_contents.append(content)
                current_tokens += content.token_count
            else:
                if content.source not in excluded_sources:
                    excluded_sources.append(content.source)

        # 组装最终内容
        final_content = self._assemble_content(selected_contents)

        # 统计
        stats = {
            "total_sources_registered": sum(len(c) for c in self._sources.values()),
            "sources_selected": len(selected_contents),
            "sources_excluded": len(excluded_sources),
            "conflicts_detected": len(conflicts),
            "token_usage": current_tokens,
            "token_budget": max_tokens,
        }

        return CoordinatedContext(
            content=final_content,
            token_count=current_tokens,
            sources_used=selected_contents,
            sources_excluded=excluded_sources,
            conflicts_detected=conflicts,
            stats=stats,
        )

    def _assemble_content(
        self,
        contents: list[SourceContent],
    ) -> str:
        """组装最终内容"""
        sections: list[str] = []

        # 按来源类型分组
        by_source: dict[SourceType, list[SourceContent]] = {}
        for content in contents:
            if content.source not in by_source:
                by_source[content.source] = []
            by_source[content.source].append(content)

        # 定义输出顺序
        order = [
            SourceType.SYSTEM_INSTRUCTION,
            SourceType.PERMISSION_CONSTRAINT,
            SourceType.USER_QUERY,
            SourceType.TASK_STATE,
            SourceType.CONVERSATION_HISTORY,
            SourceType.TOOL_OUTPUT,
            SourceType.RETRIEVAL_RESULT,
            SourceType.USER_PREFERENCE,
            SourceType.LONG_TERM_MEMORY,
        ]

        # 组装
        for source_type in order:
            if source_type in by_source:
                label = self._get_source_label(source_type)
                sections.append(f"\n[{label}]")
                for content in by_source[source_type]:
                    sections.append(content.content)

        return "\n".join(sections)

    def _get_source_label(self, source_type: SourceType) -> str:
        """获取来源显示标签"""
        labels = {
            SourceType.SYSTEM_INSTRUCTION: "系统指令",
            SourceType.USER_QUERY: "用户问题",
            SourceType.CONVERSATION_HISTORY: "对话历史",
            SourceType.RETRIEVAL_RESULT: "检索结果",
            SourceType.TOOL_OUTPUT: "工具返回",
            SourceType.TASK_STATE: "任务状态",
            SourceType.USER_PREFERENCE: "用户偏好",
            SourceType.LONG_TERM_MEMORY: "长期记忆",
            SourceType.PERMISSION_CONSTRAINT: "权限约束",
        }
        return labels.get(source_type, source_type.value)

    # -----------------------------------------------------------------------
    # 查询方法
    # -----------------------------------------------------------------------

    def get_conflicts(self) -> list[ConflictRecord]:
        """获取所有冲突记录"""
        return self._conflicts.copy()

    def get_source_stats(self) -> dict[str, Any]:
        """获取来源统计"""
        stats: dict[str, Any] = {}

        for source_type, contents in self._sources.items():
            stats[source_type.value] = {
                "count": len(contents),
                "total_tokens": sum(c.token_count for c in contents),
                "avg_relevance": (
                    sum(c.relevance_score for c in contents) / len(contents)
                    if contents else 0
                ),
                "priority": self.get_priority(source_type),
            }

        return stats


# ============================================================================
# 工厂函数
# ============================================================================


def create_coordinator(
    enable_conflict_detection: bool = True,
    enable_dynamic_priority: bool = True,
) -> MultiSourceCoordinator:
    """
    创建多源协调器

    Args:
        enable_conflict_detection: 启用冲突检测
        enable_dynamic_priority: 启用动态优先级

    Returns:
        MultiSourceCoordinator 实例
    """
    config = CoordinatorConfig(
        enable_conflict_detection=enable_conflict_detection,
        enable_dynamic_priority=enable_dynamic_priority,
    )

    return MultiSourceCoordinator(config=config)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "SourceType",
    "ConflictType",
    "ResolutionStrategy",
    "SourcePriority",
    "SourceContent",
    "ConflictRecord",
    "CoordinatorConfig",
    "CoordinatedContext",
    "MultiSourceCoordinator",
    "create_coordinator",
]

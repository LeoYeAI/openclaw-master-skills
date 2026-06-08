"""
Agent Memory System - Cross-Session Memory Linker（跨会话记忆关联器）

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
关联不同会话的记忆，构建持久化的知识图谱。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class LinkStrength(str, Enum):
    """关联强度"""

    STRONG = "strong"            # 强关联：同一任务、直接引用
    MEDIUM = "medium"            # 中关联：相同主题、相似上下文
    WEAK = "weak"                # 弱关联：共享实体、间接关联


class LinkType(str, Enum):
    """关联类型"""

    SAME_TASK = "same_task"              # 同一任务
    SAME_TOPIC = "same_topic"            # 同一主题
    SAME_ENTITY = "same_entity"          # 同一实体
    CONTINUATION = "continuation"        # 延续关系
    REFERENCE = "reference"              # 引用关系
    CONTRADICTION = "contradiction"      # 矛盾关系
    COMPLEMENT = "complement"            # 互补关系


class SessionStatus(str, Enum):
    """会话状态"""

    ACTIVE = "active"            # 活跃
    PAUSED = "paused"            # 暂停
    COMPLETED = "completed"      # 完成
    ARCHIVED = "archived"        # 归档


# ============================================================================
# 数据模型
# ============================================================================


class SessionNode(BaseModel):
    """会话节点"""

    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    ended_at: datetime | None = None
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)

    # 会话信息
    title: str = Field(default="")
    topics: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)

    # 统计
    memory_count: int = Field(default=0)
    decision_count: int = Field(default=0)

    # 元数据
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryLink(BaseModel):
    """记忆关联"""

    link_id: str = Field(
        default_factory=lambda: f"link_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )

    # 关联会话
    from_session: str
    to_session: str

    # 关联信息
    link_type: LinkType = Field(default=LinkType.SAME_TOPIC)
    link_strength: LinkStrength = Field(default=LinkStrength.MEDIUM)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    # 关联依据
    shared_topics: list[str] = Field(default_factory=list)
    shared_entities: list[str] = Field(default_factory=list)
    shared_goals: list[str] = Field(default_factory=list)

    # 备注
    note: str = Field(default="")

    created_at: datetime = Field(default_factory=datetime.now)


class KnowledgeTransfer(BaseModel):
    """知识迁移"""

    transfer_id: str = Field(
        default_factory=lambda: f"transfer_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )

    # 来源和目标
    source_session: str
    target_session: str

    # 迁移内容
    transferred_memories: list[str] = Field(default_factory=list)
    transferred_knowledge: list[str] = Field(default_factory=list)

    # 迁移统计
    total_items: int = Field(default=0)
    success_rate: float = Field(default=0.0)

    created_at: datetime = Field(default_factory=datetime.now)


class SessionGraph(BaseModel):
    """会话图谱"""

    sessions: dict[str, SessionNode] = Field(default_factory=dict)
    links: list[MemoryLink] = Field(default_factory=list)

    # 统计
    total_sessions: int = Field(default=0)
    total_links: int = Field(default=0)

    def add_session(self, session: SessionNode) -> None:
        """添加会话"""
        self.sessions[session.session_id] = session
        self.total_sessions = len(self.sessions)

    def add_link(self, link: MemoryLink) -> None:
        """添加关联"""
        self.links.append(link)
        self.total_links = len(self.links)

    def get_related_sessions(self, session_id: str) -> list[str]:
        """获取相关会话"""
        related: list[str] = []

        for link in self.links:
            if link.from_session == session_id:
                related.append(link.to_session)
            elif link.to_session == session_id:
                related.append(link.from_session)

        return list(set(related))


class LinkerConfig(BaseModel):
    """关联器配置"""

    # 关联阈值
    strong_link_threshold: float = Field(default=0.7)
    medium_link_threshold: float = Field(default=0.4)

    # 时间窗口
    max_session_age_days: int = Field(default=30)
    recent_session_priority: bool = Field(default=True)

    # 关联规则
    min_shared_topics: int = Field(default=1)
    min_shared_entities: int = Field(default=2)


# ============================================================================
# Cross-Session Memory Linker
# ============================================================================


class CrossSessionMemoryLinker:
    """
    跨会话记忆关联器

    职责：
    - 关联不同会话的记忆
    - 构建会话知识图谱
    - 支持知识迁移

    使用示例：
    ```python
    from scripts.cross_session_memory_linker import CrossSessionMemoryLinker

    linker = CrossSessionMemoryLinker()

    # 注册会话
    linker.register_session(
        session_id="session_1",
        topics=["Python优化", "性能"],
        entities=["Pandas", "NumPy"],
        goals=["提升数据处理速度"],
    )

    linker.register_session(
        session_id="session_2",
        topics=["Python优化", "缓存"],
        entities=["Redis"],
        goals=["减少数据库查询"],
    )

    # 发现关联
    links = linker.discover_links()
    print(f"发现 {len(links)} 个关联")

    # 查询相关会话
    related = linker.get_related_sessions("session_1")
    print(f"相关会话: {related}")
    ```
    """

    def __init__(self, config: LinkerConfig | None = None):
        """初始化跨会话记忆关联器"""
        self._config = config or LinkerConfig()
        self._graph = SessionGraph()

    # -----------------------------------------------------------------------
    # 会话管理
    # -----------------------------------------------------------------------

    def register_session(
        self,
        session_id: str,
        topics: list[str] | None = None,
        entities: list[str] | None = None,
        goals: list[str] | None = None,
        title: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """注册会话"""
        session = SessionNode(
            session_id=session_id,
            topics=topics or [],
            entities=entities or [],
            goals=goals or [],
            title=title,
            metadata=metadata or {},
        )
        self._graph.add_session(session)

    def update_session(
        self,
        session_id: str,
        updates: dict[str, Any],
    ) -> bool:
        """更新会话"""
        if session_id not in self._graph.sessions:
            return False

        session = self._graph.sessions[session_id]
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        return True

    def end_session(
        self,
        session_id: str,
        status: SessionStatus = SessionStatus.COMPLETED,
    ) -> bool:
        """结束会话"""
        if session_id not in self._graph.sessions:
            return False

        session = self._graph.sessions[session_id]
        session.ended_at = datetime.now()
        session.status = status

        return True

    # -----------------------------------------------------------------------
    # 关联发现
    # -----------------------------------------------------------------------

    def discover_links(self) -> list[MemoryLink]:
        """自动发现会话间的关联"""
        links: list[MemoryLink] = []
        sessions = list(self._graph.sessions.values())

        for i, session1 in enumerate(sessions):
            for session2 in sessions[i + 1:]:
                link = self._compute_link(session1, session2)
                if link:
                    links.append(link)
                    self._graph.add_link(link)

        return links

    def _compute_link(
        self,
        session1: SessionNode,
        session2: SessionNode,
    ) -> MemoryLink | None:
        """计算两个会话的关联"""
        # 计算共享内容
        shared_topics = list(set(session1.topics) & set(session2.topics))
        shared_entities = list(set(session1.entities) & set(session2.entities))
        shared_goals = list(set(session1.goals) & set(session2.goals))

        # 计算关联强度
        score = 0.0
        if shared_topics:
            score += len(shared_topics) * 0.3
        if shared_entities:
            score += len(shared_entities) * 0.2
        if shared_goals:
            score += len(shared_goals) * 0.5

        # 检查时间相近性
        time_diff = abs(
            (session1.created_at - session2.created_at).total_seconds()
        )
        if time_diff < 3600:  # 1小时内
            score += 0.1

        # 判断是否建立关联
        if score < self._config.medium_link_threshold:
            return None

        # 确定关联强度
        if score >= self._config.strong_link_threshold:
            strength = LinkStrength.STRONG
        else:
            strength = LinkStrength.MEDIUM

        # 确定关联类型
        if shared_goals:
            link_type = LinkType.SAME_TASK
        elif shared_topics:
            link_type = LinkType.SAME_TOPIC
        elif shared_entities:
            link_type = LinkType.SAME_ENTITY
        else:
            link_type = LinkType.REFERENCE

        return MemoryLink(
            from_session=session1.session_id,
            to_session=session2.session_id,
            link_type=link_type,
            link_strength=strength,
            confidence=min(1.0, score),
            shared_topics=shared_topics,
            shared_entities=shared_entities,
            shared_goals=shared_goals,
        )

    def create_explicit_link(
        self,
        from_session: str,
        to_session: str,
        link_type: LinkType,
        note: str = "",
    ) -> MemoryLink | None:
        """创建显式关联"""
        if from_session not in self._graph.sessions:
            return None
        if to_session not in self._graph.sessions:
            return None

        link = MemoryLink(
            from_session=from_session,
            to_session=to_session,
            link_type=link_type,
            link_strength=LinkStrength.STRONG,
            confidence=1.0,
            note=note,
        )
        self._graph.add_link(link)

        return link

    # -----------------------------------------------------------------------
    # 查询
    # -----------------------------------------------------------------------

    def get_related_sessions(
        self,
        session_id: str,
        min_strength: LinkStrength | None = None,
    ) -> list[dict[str, Any]]:
        """获取相关会话"""
        related: list[dict[str, Any]] = []

        for link in self._graph.links:
            if link.from_session == session_id or link.to_session == session_id:
                # 过滤强度
                if min_strength:
                    strength_order = {
                        LinkStrength.STRONG: 3,
                        LinkStrength.MEDIUM: 2,
                        LinkStrength.WEAK: 1,
                    }
                    if strength_order.get(link.link_strength, 0) < strength_order.get(min_strength, 0):
                        continue

                # 获取另一个会话
                other_id = (
                    link.to_session if link.from_session == session_id
                    else link.from_session
                )
                other_session = self._graph.sessions.get(other_id)

                if other_session:
                    related.append({
                        "session_id": other_id,
                        "title": other_session.title,
                        "topics": other_session.topics,
                        "link_type": link.link_type,
                        "link_strength": link.link_strength,
                        "confidence": link.confidence,
                    })

        # 按置信度排序
        related.sort(key=lambda x: x["confidence"], reverse=True)

        return related

    def find_sessions_by_topic(self, topic: str) -> list[SessionNode]:
        """按主题查找会话"""
        return [
            s for s in self._graph.sessions.values()
            if topic.lower() in [t.lower() for t in s.topics]
        ]

    def find_sessions_by_entity(self, entity: str) -> list[SessionNode]:
        """按实体查找会话"""
        return [
            s for s in self._graph.sessions.values()
            if entity.lower() in [e.lower() for e in s.entities]
        ]

    # -----------------------------------------------------------------------
    # 知识迁移
    # -----------------------------------------------------------------------

    def transfer_knowledge(
        self,
        from_session: str,
        to_session: str,
        knowledge_ids: list[str],
    ) -> KnowledgeTransfer:
        """迁移知识"""
        transfer = KnowledgeTransfer(
            source_session=from_session,
            target_session=to_session,
            transferred_memories=knowledge_ids,
            transferred_knowledge=knowledge_ids,
            total_items=len(knowledge_ids),
            success_rate=1.0,
        )

        return transfer

    def suggest_relevant_memories(
        self,
        current_session: str,
        query: str,
    ) -> list[dict[str, Any]]:
        """建议相关记忆"""
        suggestions: list[dict[str, Any]] = []

        # 获取相关会话
        related = self.get_related_sessions(current_session)

        for rel in related[:5]:  # 限制数量
            suggestions.append({
                "session_id": rel["session_id"],
                "session_title": rel["title"],
                "relevance": rel["confidence"],
                "topics": rel["topics"],
            })

        return suggestions

    # -----------------------------------------------------------------------
    # 图谱操作
    # -----------------------------------------------------------------------

    def get_session_graph(self) -> SessionGraph:
        """获取会话图谱"""
        return self._graph

    def export_graph(self) -> dict[str, Any]:
        """导出图谱"""
        return {
            "sessions": {
                sid: session.model_dump()
                for sid, session in self._graph.sessions.items()
            },
            "links": [link.model_dump() for link in self._graph.links],
            "statistics": {
                "total_sessions": self._graph.total_sessions,
                "total_links": self._graph.total_links,
            },
        }

    def clear_old_sessions(self, max_age_days: int | None = None) -> int:
        """清理旧会话"""
        max_age = max_age_days or self._config.max_session_age_days
        cutoff = datetime.now() - timedelta(days=max_age)

        to_remove = [
            sid for sid, session in self._graph.sessions.items()
            if session.created_at < cutoff and session.status != SessionStatus.ACTIVE
        ]

        for sid in to_remove:
            del self._graph.sessions[sid]

        # 清理关联
        self._graph.links = [
            link for link in self._graph.links
            if link.from_session not in to_remove and link.to_session not in to_remove
        ]

        self._graph.total_sessions = len(self._graph.sessions)
        self._graph.total_links = len(self._graph.links)

        return len(to_remove)


# ============================================================================
# 工厂函数
# ============================================================================


def create_session_linker() -> CrossSessionMemoryLinker:
    """创建跨会话记忆关联器"""
    return CrossSessionMemoryLinker()


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "LinkStrength",
    "LinkType",
    "SessionStatus",
    "SessionNode",
    "MemoryLink",
    "KnowledgeTransfer",
    "SessionGraph",
    "LinkerConfig",
    "CrossSessionMemoryLinker",
    "create_session_linker",
]

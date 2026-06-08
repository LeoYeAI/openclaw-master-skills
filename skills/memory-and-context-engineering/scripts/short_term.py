"""
Agent Memory System - 短期记忆模块

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
    ShortTermMemoryItem,
    ShortTermMemoryBucket,
    SemanticBucketType,
    ExtractionTrigger,
    MemoryCategory,
    MemoryType,
    LongTermMemoryContainer,
    ExtractionMapping,
    StateEventType,
)

# 避免循环导入
if TYPE_CHECKING:
    from .state_capture import GlobalStateCapture, StateChangeEvent


class SemanticBucket:
    """
    语义分类桶

    按语义类别存储和管理短期记忆项
    """

    def __init__(
        self,
        bucket_type: SemanticBucketType,
        capacity: int = 20,
        priority: float = 0.5,
        ttl_minutes: int = 30,
    ) -> None:
        """
        初始化语义分类桶

        Args:
            bucket_type: 语义分类桶类型
            capacity: 容量上限
            priority: 优先级权重
            ttl_minutes: 默认过期时间（分钟）
        """
        self._bucket = ShortTermMemoryBucket(
            bucket_type=bucket_type,
            capacity=capacity,
            priority=priority,
        )
        self._ttl_minutes: int = ttl_minutes

    def add_item(
        self,
        content: str,
        relevance_score: float = 0.5,
        source_turn: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        添加记忆项

        Args:
            content: 记忆内容
            relevance_score: 相关性分数
            source_turn: 来源对话轮次
            metadata: 元数据

        Returns:
            记忆项ID
        """
        item_id: str = f"item_{uuid.uuid4().hex[:8]}"

        item: ShortTermMemoryItem = ShortTermMemoryItem(
            item_id=item_id,
            content=content,
            bucket_type=self._bucket.bucket_type,
            relevance_score=relevance_score,
            source_turn=source_turn,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=self._ttl_minutes),
            metadata=metadata or {},
        )

        # 添加到桶中
        self._bucket.items.append(item)
        self._bucket.last_updated = datetime.now()

        # 检查容量，移除过期或低优先级的项
        self._enforce_capacity()

        return item_id

    def _enforce_capacity(self) -> None:
        """强制执行容量限制"""
        # 先清理过期项
        now: datetime = datetime.now()
        self._bucket.items = [
            item for item in self._bucket.items
            if item.expires_at is None or item.expires_at > now
        ]

        # 如果仍然超容量，按相关性移除最低的
        if len(self._bucket.items) > self._bucket.capacity:
            self._bucket.items.sort(
                key=lambda x: x.relevance_score, reverse=True
            )
            self._bucket.items = self._bucket.items[: self._bucket.capacity]

    def get_items(self, limit: int | None = None) -> list[ShortTermMemoryItem]:
        """
        获取记忆项

        Args:
            limit: 返回数量限制

        Returns:
            记忆项列表
        """
        self._enforce_capacity()
        items: list[ShortTermMemoryItem] = sorted(
            self._bucket.items, key=lambda x: x.relevance_score, reverse=True
        )
        if limit is not None:
            return items[:limit]
        return items

    def get_content_list(self, limit: int | None = None) -> list[str]:
        """
        获取内容列表

        Args:
            limit: 返回数量限制

        Returns:
            内容字符串列表
        """
        items: list[ShortTermMemoryItem] = self.get_items(limit)
        return [item.content for item in items]

    def clear(self) -> int:
        """
        清空桶

        Returns:
            清除的项数量
        """
        count: int = len(self._bucket.items)
        self._bucket.items = []
        return count

    def get_fill_ratio(self) -> float:
        """
        获取填充率

        Returns:
            填充率 (0.0-1.0)
        """
        return len(self._bucket.items) / max(self._bucket.capacity, 1)

    @property
    def bucket_type(self) -> SemanticBucketType:
        """获取桶类型"""
        return self._bucket.bucket_type

    @property
    def size(self) -> int:
        """获取当前项数"""
        return len(self._bucket.items)

    @property
    def capacity(self) -> int:
        """获取容量"""
        return self._bucket.capacity


class ShortTermMemoryManager:
    """
    短期记忆管理器

    管理5种语义分类桶，提供统一的存储和查询接口
    """

    def __init__(
        self,
        user_id: str = "default_user",
        bucket_capacity: int = 20,
        ttl_minutes: int = 30,
    ) -> None:
        """
        初始化短期记忆管理器

        Args:
            user_id: 用户ID
            bucket_capacity: 桶容量
            ttl_minutes: 默认过期时间（分钟）
        """
        self.user_id: str = user_id

        # 初始化5种语义分类桶
        self._buckets: dict[SemanticBucketType, SemanticBucket] = {
            SemanticBucketType.TASK_CONTEXT: SemanticBucket(
                SemanticBucketType.TASK_CONTEXT,
                capacity=bucket_capacity,
                priority=0.9,  # 任务上下文优先级最高
                ttl_minutes=ttl_minutes,
            ),
            SemanticBucketType.USER_INTENT: SemanticBucket(
                SemanticBucketType.USER_INTENT,
                capacity=bucket_capacity,
                priority=0.85,
                ttl_minutes=ttl_minutes,
            ),
            SemanticBucketType.KNOWLEDGE_GAP: SemanticBucket(
                SemanticBucketType.KNOWLEDGE_GAP,
                capacity=bucket_capacity,
                priority=0.7,
                ttl_minutes=ttl_minutes,
            ),
            SemanticBucketType.EMOTIONAL_TRACE: SemanticBucket(
                SemanticBucketType.EMOTIONAL_TRACE,
                capacity=bucket_capacity,
                priority=0.6,
                ttl_minutes=ttl_minutes,
            ),
            SemanticBucketType.DECISION_CONTEXT: SemanticBucket(
                SemanticBucketType.DECISION_CONTEXT,
                capacity=bucket_capacity,
                priority=0.8,
                ttl_minutes=ttl_minutes,
            ),
        }

        # 会话信息
        self._session_id: str = ""
        self._turn_count: int = 0
        
        # 【新增】跨层关联索引
        # 短期记忆项ID → 相关长期记忆ID列表
        self._stm_to_ltm_links: dict[str, list[str]] = {}
        # 长期记忆ID → 短期记忆项ID列表（反向索引）
        self._ltm_to_stm_links: dict[str, list[str]] = {}
        
        # 【新增】外部索引器引用（可选）
        self._memory_indexer: Any | None = None
        
        # 【新增】动态阈值参数
        self._similarity_threshold: float = 0.25
        self._recent_match_count: int = 0
        self._threshold_adjustment_factor: float = 0.1
        
        # 【新增】时序洞察数据
        self._topic_history: dict[str, list[datetime]] = {}  # topic -> [timestamps]
        self._topic_stats_window_hours: int = 24

        # P1: 状态捕捉器集成
        self._state_capture: GlobalStateCapture | None = None
        self._state_subscription_id: str | None = None
        self._auto_store_enabled: bool = True  # 自动存储开关
        self._last_state_hash: str = ""  # 防重复存储

    # ========== P1: 状态集成方法 ==========

    def bind_state_capture(
        self,
        state_capture: GlobalStateCapture,
        auto_store: bool = True,
        subscribe_events: bool = True,
    ) -> None:
        """
        绑定状态捕捉器，启用事件驱动存储

        Args:
            state_capture: 全局状态捕捉器实例
            auto_store: 是否自动存储状态变化
            subscribe_events: 是否订阅状态变化事件
        """
        self._state_capture = state_capture
        self._auto_store_enabled = auto_store

        if subscribe_events:
            self._state_subscription_id = state_capture.subscribe(
                event_types=[
                    StateEventType.PHASE_CHANGE,
                    StateEventType.TASK_SWITCH,
                    StateEventType.TASK_COMPLETE,
                    StateEventType.USER_STATE_CHANGE,
                ],
                callback=self._on_state_change,
            )

    def unbind_state_capture(self) -> None:
        """解绑状态捕捉器"""
        if self._state_capture and self._state_subscription_id:
            self._state_capture.unsubscribe(self._state_subscription_id)
            self._state_subscription_id = None
        self._state_capture = None

    def _on_state_change(self, event: StateChangeEvent) -> None:
        """
        状态变化事件回调 - 自动存储到短期记忆

        Args:
            event: 状态变化事件
        """
        if not self._auto_store_enabled:
            return

        # 防重复存储：计算事件哈希
        event_hash: str = self._compute_event_hash(event)
        if event_hash == self._last_state_hash:
            return
        self._last_state_hash = event_hash

        # 映射到语义桶
        bucket_type: SemanticBucketType = self._map_event_to_bucket(event)
        content: str = self._generate_event_content(event)
        topic_label: str = self._extract_topic_from_event(event)

        # 存储到短期记忆
        self.store_with_semantics(
            content=content,
            bucket_type=bucket_type,
            topic_label=topic_label,
            relevance_score=0.7,  # 状态事件默认相关性
            metadata={
                "event_type": event.event_type.value,
                "checkpoint_id": event.checkpoint_id,
                "thread_id": event.thread_id,
                "auto_stored": True,
                "changes": event.changes,
            },
        )

    def _compute_event_hash(self, event: StateChangeEvent) -> str:
        """计算事件哈希，用于防重复"""
        import hashlib
        hash_content: str = f"{event.event_type.value}_{event.checkpoint_id}_{str(event.changes)[:100]}"
        return hashlib.md5(hash_content.encode()).hexdigest()[:16]

    def _map_event_to_bucket(self, event: StateChangeEvent) -> SemanticBucketType:
        """
        将事件类型映射到语义桶类型

        Args:
            event: 状态变化事件

        Returns:
            语义桶类型
        """
        mapping: dict[StateEventType, SemanticBucketType] = {
            StateEventType.PHASE_CHANGE: SemanticBucketType.TASK_CONTEXT,
            StateEventType.TASK_SWITCH: SemanticBucketType.USER_INTENT,
            StateEventType.TASK_COMPLETE: SemanticBucketType.DECISION_CONTEXT,
            StateEventType.USER_STATE_CHANGE: SemanticBucketType.EMOTIONAL_TRACE,
            StateEventType.STATE_CHANGE: SemanticBucketType.TASK_CONTEXT,
            StateEventType.CHECKPOINT_CREATED: SemanticBucketType.TASK_CONTEXT,
            StateEventType.CHECKPOINT_RESTORED: SemanticBucketType.TASK_CONTEXT,
        }
        return mapping.get(event.event_type, SemanticBucketType.TASK_CONTEXT)

    def _generate_event_content(self, event: StateChangeEvent) -> str:
        """
        生成事件的内容描述

        Args:
            event: 状态变化事件

        Returns:
            内容字符串
        """
        event_type: StateEventType = event.event_type
        changes: dict[str, Any] = event.changes

        if event_type == StateEventType.PHASE_CHANGE:
            old_phase: str = changes.get("modified", {}).get("phase", {}).get("old", "unknown")
            new_phase: str = changes.get("modified", {}).get("phase", {}).get("new", "unknown")
            return f"阶段变化: {old_phase} → {new_phase}"

        elif event_type == StateEventType.TASK_SWITCH:
            new_task: str = event.current_state.get("current_task", "unknown")
            return f"任务切换: 开始新任务 '{new_task}'"

        elif event_type == StateEventType.TASK_COMPLETE:
            task: str = event.current_state.get("current_task", "unknown")
            return f"任务完成: '{task}'"

        elif event_type == StateEventType.USER_STATE_CHANGE:
            old_state: str = changes.get("modified", {}).get("user_state", {}).get("old", "unknown")
            new_state: str = changes.get("modified", {}).get("user_state", {}).get("new", "unknown")
            return f"用户状态变化: {old_state} → {new_state}"

        else:
            return f"状态变化: {event_type.value}"

    def _extract_topic_from_event(self, event: StateChangeEvent) -> str:
        """
        从事件中提取话题标签

        Args:
            event: 状态变化事件

        Returns:
            话题标签
        """
        if event.event_type == StateEventType.PHASE_CHANGE:
            new_phase: str = event.changes.get("modified", {}).get("phase", {}).get("new", "")
            return f"阶段-{new_phase}" if new_phase else "状态变化"

        elif event.event_type == StateEventType.TASK_SWITCH:
            task: str = event.current_state.get("current_task", "")
            return task if task else "任务切换"

        elif event.event_type == StateEventType.TASK_COMPLETE:
            return "任务完成"

        elif event.event_type == StateEventType.USER_STATE_CHANGE:
            new_state: str = event.changes.get("modified", {}).get("user_state", {}).get("new", "")
            return f"用户状态-{new_state}" if new_state else "用户状态"

        return "状态事件"

    def get_auto_store_status(self) -> dict[str, Any]:
        """
        获取自动存储状态

        Returns:
            状态信息
        """
        return {
            "enabled": self._auto_store_enabled,
            "bound": self._state_capture is not None,
            "subscribed": self._state_subscription_id is not None,
        }

    def set_auto_store(self, enabled: bool) -> None:
        """
        设置自动存储开关

        Args:
            enabled: 是否启用
        """
        self._auto_store_enabled = enabled

    # ========== 核心方法 ==========

    def start_session(self) -> str:
        """
        开始新会话

        Returns:
            会话ID
        """
        self._session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self._turn_count = 0
        return self._session_id

    def store(
        self,
        content: str,
        bucket_type: SemanticBucketType,
        relevance_score: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        存储记忆项

        Args:
            content: 记忆内容
            bucket_type: 目标桶类型
            relevance_score: 相关性分数
            metadata: 元数据

        Returns:
            记忆项ID
        """
        bucket: SemanticBucket | None = self._buckets.get(bucket_type)
        if bucket is None:
            raise ValueError(f"Unknown bucket type: {bucket_type}")

        return bucket.add_item(
            content=content,
            relevance_score=relevance_score,
            source_turn=self._turn_count,
            metadata=metadata,
        )

    def store_multi(
        self,
        items: list[tuple[str, SemanticBucketType, float]],
    ) -> list[str]:
        """
        批量存储记忆项

        Args:
            items: (内容, 桶类型, 相关性分数) 列表

        Returns:
            记忆项ID列表
        """
        ids: list[str] = []
        for content, bucket_type, score in items:
            item_id: str = self.store(content, bucket_type, score)
            ids.append(item_id)
        return ids

    def classify_and_store(
        self,
        content: str,
        relevance_score: float = 0.5,
    ) -> tuple[str, SemanticBucketType]:
        """
        自动分类并存储

        Args:
            content: 记忆内容
            relevance_score: 相关性分数

        Returns:
            (记忆项ID, 分类桶类型)
        """
        # 自动分类逻辑
        bucket_type: SemanticBucketType = self._classify_content(content)

        item_id: str = self.store(content, bucket_type, relevance_score)
        return item_id, bucket_type

    def _classify_content(self, content: str) -> SemanticBucketType:
        """
        【已废弃】关键词匹配分类
        
        警告：此方法已废弃，保留仅用于向后兼容。
        请使用 store_with_semantics() 方法，由智能体指定语义分类。
        
        Args:
            content: 内容

        Returns:
            分类桶类型（默认返回 TASK_CONTEXT）
        """
        # 直接返回默认值，不再使用关键词匹配
        # 智能体应使用 store_with_semantics() 显式指定分类
        return SemanticBucketType.TASK_CONTEXT

    def store_with_semantics(
        self,
        content: str,
        bucket_type: SemanticBucketType,
        topic_label: str,
        relevance_score: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        存储记忆项（智能体指定语义分类和话题标签）
        
        这是推荐的存储方式。智能体根据对话内容判断：
        - bucket_type: 语义桶类型（5种之一）
        - topic_label: 话题标签（用于聚合相同话题的内容）
        
        Args:
            content: 记忆内容
            bucket_type: 语义桶类型（智能体判断）
            topic_label: 话题标签（智能体判断，用于聚合）
            relevance_score: 相关性分数
            metadata: 元数据
            
        Returns:
            记忆项ID
        """
        bucket: SemanticBucket | None = self._buckets.get(bucket_type)
        if bucket is None:
            raise ValueError(f"Unknown bucket type: {bucket_type}")
        
        item_id: str = f"item_{uuid.uuid4().hex[:8]}"
        
        item: ShortTermMemoryItem = ShortTermMemoryItem(
            item_id=item_id,
            content=content,
            bucket_type=bucket_type,
            topic_label=topic_label,
            relevance_score=relevance_score,
            source_turn=self._turn_count,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=30),
            metadata=metadata or {},
        )
        
        bucket._bucket.items.append(item)
        bucket._bucket.last_updated = datetime.now()
        bucket._enforce_capacity()
        
        # 更新话题统计（用于时序洞察）
        self._update_topic_stats(topic_label)
        
        return item_id

    def store_multi_with_semantics(
        self,
        items: list[tuple[str, SemanticBucketType, str, float]],
    ) -> list[str]:
        """
        批量存储记忆项（智能体指定语义分类和话题标签）
        
        Args:
            items: (内容, 桶类型, 话题标签, 相关性分数) 列表
            
        Returns:
            记忆项ID列表
        """
        ids: list[str] = []
        for content, bucket_type, topic_label, score in items:
            item_id: str = self.store_with_semantics(
                content, bucket_type, topic_label, score
            )
            ids.append(item_id)
        return ids

    # ========================================================================
    # 【新增】话题聚合方法
    # ========================================================================

    def get_items_by_topic(
        self,
        topic_label: str,
        limit: int = 20,
    ) -> list[ShortTermMemoryItem]:
        """
        按话题标签获取记忆项
        
        Args:
            topic_label: 话题标签
            limit: 返回数量限制
            
        Returns:
            该话题的记忆项列表
        """
        items: list[ShortTermMemoryItem] = []
        for bucket in self._buckets.values():
            for item in bucket.get_items():
                if item.topic_label == topic_label:
                    items.append(item)
        
        items.sort(key=lambda x: x.relevance_score, reverse=True)
        return items[:limit]

    def get_items_by_bucket(
        self,
        bucket_type: SemanticBucketType,
        limit: int = 20,
    ) -> list[ShortTermMemoryItem]:
        """
        按语义桶类型获取记忆项
        
        Args:
            bucket_type: 语义桶类型
            limit: 返回数量限制
            
        Returns:
            该语义桶的记忆项列表
        """
        if bucket_type not in self._buckets:
            return []
        
        bucket = self._buckets[bucket_type]
        items = bucket.get_items()
        items.sort(key=lambda x: x.relevance_score, reverse=True)
        return items[:limit]

    def get_topic_summary(self) -> dict[str, dict[str, Any]]:
        """
        获取话题聚合摘要
        
        Returns:
            {topic_label: {count, bucket_distribution, avg_relevance, item_ids}}
        """
        topic_stats: dict[str, dict[str, Any]] = {}
        
        for bucket in self._buckets.values():
            for item in bucket.get_items():
                if not item.topic_label:
                    continue
                    
                if item.topic_label not in topic_stats:
                    topic_stats[item.topic_label] = {
                        "count": 0,
                        "bucket_distribution": {},
                        "total_relevance": 0.0,
                        "item_ids": [],
                    }
                
                stats = topic_stats[item.topic_label]
                stats["count"] += 1
                stats["total_relevance"] += item.relevance_score
                stats["item_ids"].append(item.item_id)
                
                bucket_key = item.bucket_type.value
                stats["bucket_distribution"][bucket_key] = (
                    stats["bucket_distribution"].get(bucket_key, 0) + 1
                )
        
        # 计算平均相关性
        for stats in topic_stats.values():
            if stats["count"] > 0:
                stats["avg_relevance"] = stats["total_relevance"] / stats["count"]
            del stats["total_relevance"]
        
        return topic_stats

    def get_active_topics(self, min_count: int = 2) -> list[str]:
        """
        获取活跃话题标签列表
        
        Args:
            min_count: 最小出现次数
            
        Returns:
            活跃话题标签列表（按数量降序）
        """
        summary = self.get_topic_summary()
        active = [
            topic for topic, stats in summary.items()
            if stats["count"] >= min_count
        ]
        active.sort(key=lambda t: summary[t]["count"], reverse=True)
        return active

    # ========================================================================
    # 【新增】动态阈值
    # ========================================================================

    def _update_topic_stats(self, topic_label: str) -> None:
        """
        更新话题统计（用于时序洞察）
        
        Args:
            topic_label: 话题标签
        """
        if not topic_label:
            return
            
        now = datetime.now()
        if topic_label not in self._topic_history:
            self._topic_history[topic_label] = []
        
        self._topic_history[topic_label].append(now)
        
        # 清理过期记录（超过24小时）
        window = timedelta(hours=self._topic_stats_window_hours)
        self._topic_history[topic_label] = [
            ts for ts in self._topic_history[topic_label]
            if now - ts < window
        ]

    def adjust_threshold(self, match_count: int) -> None:
        """
        动态调整相似度阈值
        
        基于最近匹配数量调整阈值：
        - 匹配过多 → 提高阈值，减少误聚类
        - 匹配过少 → 降低阈值，增加召回
        
        Args:
            match_count: 最近一次分析的匹配数量
        """
        self._recent_match_count = match_count
        
        # 高匹配率：提高阈值
        if match_count > 15:
            self._similarity_threshold = min(
                0.5, self._similarity_threshold * (1 + self._threshold_adjustment_factor)
            )
        # 低匹配率：降低阈值
        elif match_count < 3:
            self._similarity_threshold = max(
                0.1, self._similarity_threshold * (1 - self._threshold_adjustment_factor)
            )

    def get_threshold(self) -> float:
        """获取当前相似度阈值"""
        return self._similarity_threshold

    # ========================================================================
    # 【新增】时序洞察数据接口
    # ========================================================================

    def get_topic_persistence(self, topic_label: str) -> dict[str, Any]:
        """
        获取话题持续性数据（供智能体判断）
        
        Args:
            topic_label: 话题标签
            
        Returns:
            {
                "occurrence_count": 出现次数,
                "first_seen": 首次出现时间,
                "last_seen": 最后出现时间,
                "persistence_score": 持续性分数 (0-1),
            }
        """
        history = self._topic_history.get(topic_label, [])
        
        if not history:
            return {
                "occurrence_count": 0,
                "first_seen": None,
                "last_seen": None,
                "persistence_score": 0.0,
            }
        
        now = datetime.now()
        first_seen = min(history)
        last_seen = max(history)
        
        # 持续性分数：基于出现频率和时间跨度
        time_span_hours = (now - first_seen).total_seconds() / 3600
        frequency = len(history) / max(time_span_hours, 1)  # 每小时出现次数
        persistence_score = min(1.0, frequency / 2)  # 标准化到0-1
        
        return {
            "occurrence_count": len(history),
            "first_seen": first_seen.isoformat(),
            "last_seen": last_seen.isoformat(),
            "persistence_score": persistence_score,
        }

    def get_all_topic_persistence(self) -> dict[str, dict[str, Any]]:
        """
        获取所有话题的持续性数据
        
        Returns:
            {topic_label: persistence_data}
        """
        result: dict[str, dict[str, Any]] = {}
        for topic in self._topic_history:
            result[topic] = self.get_topic_persistence(topic)
        return result

    def get_temporal_insight_data(self) -> dict[str, Any]:
        """
        获取时序洞察数据（供智能体使用）
        
        Returns:
            {
                "active_topics": 活跃话题列表,
                "topic_summary": 话题聚合摘要,
                "persistence_data": 所有话题持续性数据,
                "current_threshold": 当前相似度阈值,
            }
        """
        return {
            "active_topics": self.get_active_topics(),
            "topic_summary": self.get_topic_summary(),
            "persistence_data": self.get_all_topic_persistence(),
            "current_threshold": self._similarity_threshold,
        }

    def increment_turn(self) -> int:
        """
        增加对话轮次

        Returns:
            当前轮次
        """
        self._turn_count += 1
        return self._turn_count

    def get_bucket(self, bucket_type: SemanticBucketType) -> SemanticBucket | None:
        """
        获取指定桶

        Args:
            bucket_type: 桶类型

        Returns:
            语义分类桶
        """
        return self._buckets.get(bucket_type)

    def get_all_items(self, limit_per_bucket: int = 5) -> list[ShortTermMemoryItem]:
        """
        获取所有桶的记忆项

        Args:
            limit_per_bucket: 每个桶的返回数量限制

        Returns:
            记忆项列表
        """
        all_items: list[ShortTermMemoryItem] = []
        for bucket in self._buckets.values():
            items: list[ShortTermMemoryItem] = bucket.get_items(limit_per_bucket)
            all_items.extend(items)

        # 按相关性排序
        all_items.sort(key=lambda x: x.relevance_score, reverse=True)
        return all_items

    def search(
        self,
        query: str,
        bucket_types: list[SemanticBucketType] | None = None,
        limit: int = 10,
    ) -> list[ShortTermMemoryItem]:
        """
        搜索记忆项

        Args:
            query: 搜索关键词
            bucket_types: 限定桶类型列表（可选）
            limit: 返回数量限制

        Returns:
            匹配的记忆项列表
        """
        results: list[ShortTermMemoryItem] = []
        query_lower: str = query.lower()

        buckets_to_search: list[SemanticBucket] = (
            [self._buckets[bt] for bt in bucket_types if bt in self._buckets]
            if bucket_types
            else list(self._buckets.values())
        )

        for bucket in buckets_to_search:
            for item in bucket.get_items():
                if query_lower in item.content.lower():
                    results.append(item)

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def get_extraction_triggers(self) -> list[ExtractionTrigger]:
        """
        获取提炼触发条件

        Returns:
            触发条件列表
        """
        triggers: list[ExtractionTrigger] = []

        # 容量触发
        for bucket in self._buckets.values():
            fill_ratio: float = bucket.get_fill_ratio()
            triggers.append(
                ExtractionTrigger(
                    trigger_type="capacity",
                    threshold=0.8,
                    current_value=fill_ratio,
                    triggered=fill_ratio >= 0.8,
                )
            )

        # 时间间隔触发（每10轮）
        triggers.append(
            ExtractionTrigger(
                trigger_type="time_interval",
                threshold=10.0,
                current_value=float(self._turn_count),
                triggered=self._turn_count > 0 and self._turn_count % 10 == 0,
            )
        )

        return triggers

    def should_extract(self) -> bool:
        """
        判断是否应该触发提炼

        Returns:
            是否应该提炼
        """
        triggers: list[ExtractionTrigger] = self.get_extraction_triggers()
        return any(t.triggered for t in triggers)

    def clear_all(self) -> dict[str, int]:
        """
        清空所有桶

        Returns:
            各桶清除的数量
        """
        counts: dict[str, int] = {}
        for bucket_type, bucket in self._buckets.items():
            counts[bucket_type.value] = bucket.clear()
        return counts

    # ========================================================================
    # 【新增】跨层关联索引方法
    # ========================================================================

    def set_memory_indexer(self, indexer: Any) -> None:
        """
        设置记忆索引器
        
        Args:
            indexer: MemoryIndexer 实例
        """
        self._memory_indexer = indexer

    def link_to_long_term(
        self,
        stm_item_id: str,
        ltm_memory_id: str,
    ) -> None:
        """
        建立短期记忆与长期记忆的关联
        
        Args:
            stm_item_id: 短期记忆项ID
            ltm_memory_id: 长期记忆ID
        """
        # 正向索引
        if stm_item_id not in self._stm_to_ltm_links:
            self._stm_to_ltm_links[stm_item_id] = []
        if ltm_memory_id not in self._stm_to_ltm_links[stm_item_id]:
            self._stm_to_ltm_links[stm_item_id].append(ltm_memory_id)
        
        # 反向索引
        if ltm_memory_id not in self._ltm_to_stm_links:
            self._ltm_to_stm_links[ltm_memory_id] = []
        if stm_item_id not in self._ltm_to_stm_links[ltm_memory_id]:
            self._ltm_to_stm_links[ltm_memory_id].append(stm_item_id)

    def get_related_long_term_memories(
        self,
        stm_item_id: str,
    ) -> list[str]:
        """
        获取短期记忆项关联的长期记忆
        
        Args:
            stm_item_id: 短期记忆项ID
            
        Returns:
            关联的长期记忆ID列表
        """
        return self._stm_to_ltm_links.get(stm_item_id, [])

    def get_related_short_term_items(
        self,
        ltm_memory_id: str,
    ) -> list[str]:
        """
        获取长期记忆关联的短期记忆项
        
        Args:
            ltm_memory_id: 长期记忆ID
            
        Returns:
            关联的短期记忆项ID列表
        """
        return self._ltm_to_stm_links.get(ltm_memory_id, [])

    def search_long_term_memory(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        从短期记忆管理器检索相关长期记忆
        
        Args:
            query: 搜索查询
            top_k: 返回数量
            
        Returns:
            检索结果列表
        """
        if self._memory_indexer is None:
            return []
        
        # 使用索引器检索
        results = self._memory_indexer.search(query, top_k=top_k)
        
        return [
            {
                "memory_id": r.memory_id,
                "score": r.score,
                "matched_keywords": r.matched_keywords,
            }
            for r in results
        ]

    def auto_link_by_similarity(
        self,
        item_id: str,
        content: str,
        threshold: float = 0.3,
    ) -> list[str]:
        """
        自动关联：根据内容相似度自动建立与长期记忆的关联
        
        Args:
            item_id: 短期记忆项ID
            content: 记忆内容
            threshold: 相似度阈值
            
        Returns:
            关联的长期记忆ID列表
        """
        if self._memory_indexer is None:
            return []
        
        # 检索相关长期记忆
        results = self._memory_indexer.search(content, top_k=10)
        
        linked_ids: list[str] = []
        for result in results:
            # 只有高分才建立关联
            if result.score >= threshold:
                self.link_to_long_term(item_id, result.memory_id)
                linked_ids.append(result.memory_id)
        
        return linked_ids

    def store_with_auto_link(
        self,
        content: str,
        bucket_type: SemanticBucketType,
        relevance_score: float = 0.5,
        metadata: dict[str, Any] | None = None,
        auto_link_threshold: float = 0.3,
    ) -> tuple[str, list[str]]:
        """
        存储记忆项并自动关联长期记忆
        
        Args:
            content: 记忆内容
            bucket_type: 目标桶类型
            relevance_score: 相关性分数
            metadata: 元数据
            auto_link_threshold: 自动关联阈值
            
        Returns:
            (记忆项ID, 关联的长期记忆ID列表)
        """
        # 先存储
        item_id = self.store(content, bucket_type, relevance_score, metadata)
        
        # 自动关联
        linked_ids = self.auto_link_by_similarity(
            item_id, content, auto_link_threshold
        )
        
        return item_id, linked_ids

    def get_cross_layer_stats(self) -> dict[str, Any]:
        """
        获取跨层关联统计
        
        Returns:
            统计信息
        """
        return {
            "total_stm_items": sum(
                bucket.size for bucket in self._buckets.values()
            ),
            "total_links": sum(
                len(links) for links in self._stm_to_ltm_links.values()
            ),
            "unique_ltm_linked": len(self._ltm_to_stm_links),
            "indexer_enabled": self._memory_indexer is not None,
        }

    def get_stats(self) -> dict[str, Any]:
        """
        获取短期记忆管理器统计信息
        
        Returns:
            统计信息字典，包含：
            - total_items: 总记忆项数
            - items_by_bucket: 各桶的记忆项数
            - total_topics: 话题总数
            - active_topics: 活跃话题列表
            - turn_count: 对话轮次
            - session_id: 会话ID
            - cross_layer: 跨层关联统计
        """
        # 统计各桶项数
        items_by_bucket: dict[str, int] = {}
        total_items: int = 0
        
        for bucket_type, bucket in self._buckets.items():
            count = bucket.size
            items_by_bucket[bucket_type.value] = count
            total_items += count
        
        # 获取活跃话题
        topic_summary = self.get_topic_summary()
        active_topics = [
            topic for topic, stats in topic_summary.items()
            if stats["count"] >= 2
        ]
        
        return {
            "total_items": total_items,
            "items_by_bucket": items_by_bucket,
            "total_topics": len(topic_summary),
            "active_topics": active_topics[:10],  # 最多返回10个
            "turn_count": self._turn_count,
            "session_id": self._session_id,
            "cross_layer": self.get_cross_layer_stats(),
            "similarity_threshold": self._similarity_threshold,
        }


class AsynchronousExtractor:
    """
    异步提炼器（洞察驱动版）

    核心升级：集成短期记忆洞察分析器，实现精准提炼
    
    流程：
    1. 短期洞察分析 → 话题聚类、优先级评估、关联发现
    2. 按决策提炼 → 高质量长期记忆
    """

    def __init__(
        self,
        short_term_manager: ShortTermMemoryManager,
        long_term_manager: Any,  # LongTermMemoryManager
        insight_analyzer: Any | None = None,  # ShortTermInsightAnalyzer
    ) -> None:
        """
        初始化异步提炼器

        Args:
            short_term_manager: 短期记忆管理器
            long_term_manager: 长期记忆管理器
            insight_analyzer: 短期记忆洞察分析器（可选，默认自动创建）
        """
        self._short_term: ShortTermMemoryManager = short_term_manager
        self._long_term: Any = long_term_manager
        
        # 延迟导入避免循环依赖
        if insight_analyzer is None:
            from .short_term_insight import ShortTermInsightAnalyzer
            insight_analyzer = ShortTermInsightAnalyzer()
        self._insight_analyzer: Any = insight_analyzer

        # 提炼统计
        self._extraction_count: int = 0
        self._last_extraction_time: datetime | None = None
        
        # 最近洞察结果（供查询）
        self._last_insight: Any | None = None

    def extract(self, force: bool = False) -> dict[str, Any]:
        """
        执行提炼（洞察驱动版）

        Args:
            force: 是否强制执行

        Returns:
            提炼结果
        """
        # 检查触发条件
        if not force and not self._short_term.should_extract():
            return {
                "extracted": False,
                "reason": "No extraction triggers met",
            }

        # 收集待提炼的项
        items: list[ShortTermMemoryItem] = self._short_term.get_all_items(
            limit_per_bucket=10
        )

        if not items:
            return {
                "extracted": False,
                "reason": "No items to extract",
            }

        # 【核心升级】短期洞察分析
        insight = self._insight_analyzer.analyze(items)
        self._last_insight = insight
        decision = insight.decision
        
        # 检查是否有值得提炼的内容
        if decision.items_to_extract == 0:
            return {
                "extracted": False,
                "reason": "No valuable items to extract (insight analysis)",
                "insight": insight.format_for_extractor(),
                "summary": insight.summary,
            }

        # 【核心升级】按洞察决策提炼
        extractions: dict[str, Any] = {}
        processed_clusters: set[str] = set()
        
        for cluster_id in decision.extraction_order:
            if cluster_id in processed_clusters:
                continue
                
            # 获取话题簇
            cluster = next(
                (c for c in decision.clusters if c.cluster_id == cluster_id),
                None
            )
            if cluster is None or not cluster.should_extract:
                continue
            
            # 检查是否需要合并
            if cluster.should_merge:
                # 合并相关簇
                merged_items = list(cluster.items)
                for merge_id in cluster.merge_with:
                    merge_cluster = next(
                        (c for c in decision.clusters if c.cluster_id == merge_id),
                        None
                    )
                    if merge_cluster and merge_cluster.should_extract:
                        merged_items.extend(merge_cluster.items)
                        processed_clusters.add(merge_id)
                
                # 提炼合并后的簇
                cluster_extraction = self._extract_cluster(
                    merged_items, cluster.topic_label
                )
            else:
                # 提炼单个簇
                cluster_extraction = self._extract_cluster(
                    cluster.items, cluster.topic_label
                )
            
            extractions[cluster.topic_label] = cluster_extraction
            processed_clusters.add(cluster_id)

        # 更新长期记忆
        if self._long_term is not None and extractions:
            self._long_term.update_from_extractions(extractions)

        # 更新统计
        self._extraction_count += 1
        self._last_extraction_time = datetime.now()

        return {
            "extracted": True,
            "clusters_processed": len(processed_clusters),
            "items_extracted": decision.items_to_extract,
            "items_skipped": decision.items_to_skip,
            "extractions": extractions,
            "extraction_count": self._extraction_count,
            "insight": insight.format_for_extractor(),
            "summary": insight.summary,
        }
    
    def _extract_cluster(
        self,
        items: list[ShortTermMemoryItem],
        topic_label: str,
    ) -> dict[str, Any]:
        """
        提炼单个话题簇
        
        短期记忆语义桶 → 长期记忆7分类映射：
        
        | 短期记忆桶        | 长期记忆分类                  |
        |------------------|------------------------------|
        | USER_INTENT      | CORE_PREFERENCE / CORE_IDENTITY |
        | DECISION_CONTEXT | CORE_SKILL / EXTENDED_BEHAVIOR   |
        | TASK_CONTEXT     | EXTENDED_NARRATIVE               |
        | KNOWLEDGE_GAP    | EXTENDED_KNOWLEDGE               |
        | EMOTIONAL_TRACE  | EXTENDED_EMOTION                |
        
        Args:
            items: 记忆项列表
            topic_label: 话题标签
            
        Returns:
            提炼结果（包含分类信息）
        """
        # 统计桶类型分布
        bucket_counts: dict[SemanticBucketType, int] = {}
        for item in items:
            bucket_counts[item.bucket_type] = bucket_counts.get(item.bucket_type, 0) + 1
        
        # 确定主导桶类型
        dominant_bucket = max(bucket_counts, key=bucket_counts.get)
        
        # 【修复】按桶类型映射到正确的长期记忆分类
        extraction_result: dict[str, Any] = {
            "source_topic": topic_label,
            "source_bucket": dominant_bucket.value,
        }
        
        if dominant_bucket == SemanticBucketType.USER_INTENT:
            # 用户意图 → 核心偏好 / 核心身份
            result = self._extract_to_profile(items, topic_label)
            result["target_category"] = MemoryCategory.CORE_PREFERENCE.value
            result["alternative_category"] = MemoryCategory.CORE_IDENTITY.value
            extraction_result.update(result)
            
        elif dominant_bucket == SemanticBucketType.DECISION_CONTEXT:
            # 【关键修正】决策上下文 → 上下文重构器（非线性激活）
            # 决策上下文是当前会话的决策情境，不应直接提炼到长期记忆
            # 而是传递给上下文重构器进行六维激活
            result = self._extract_to_context_activation(items, topic_label)
            result["target_category"] = "CONTEXT_ACTIVATION"  # 特殊标记
            result["description"] = "决策上下文传递给上下文重构器进行非线性激活"
            extraction_result.update(result)
            
        elif dominant_bucket == SemanticBucketType.TASK_CONTEXT:
            # 任务上下文 → 扩展叙事 + 上下文重构器
            # 任务上下文同样需要传递给上下文重构器
            result = self._extract_to_narrative(items, topic_label)
            result["target_category"] = MemoryCategory.EXTENDED_NARRATIVE.value
            result["also_for_context"] = True  # 同时用于上下文激活
            extraction_result.update(result)
            
        elif dominant_bucket == SemanticBucketType.KNOWLEDGE_GAP:
            # 知识缺口 → 扩展知识
            result = self._extract_to_semantic(items, topic_label)
            result["target_category"] = MemoryCategory.EXTENDED_KNOWLEDGE.value
            extraction_result.update(result)
            
        else:  # EMOTIONAL_TRACE
            # 情感痕迹 → 扩展情感
            result = self._extract_to_emotional(items, topic_label)
            result["target_category"] = MemoryCategory.EXTENDED_EMOTION.value
            extraction_result.update(result)
        
        return extraction_result

    def _extract_to_context_activation(
        self,
        items: list[ShortTermMemoryItem],
        topic_label: str = "",
    ) -> dict[str, Any]:
        """
        提炼决策上下文为上下文激活输入
        
        决策上下文不存储到长期记忆，而是传递给上下文重构器
        用于六维激活（时间/语义/情境/情感/因果/身份）
        
        Args:
            items: 记忆项列表
            topic_label: 话题标签
            
        Returns:
            上下文激活输入
        """
        return {
            "context_type": "decision_context",
            "topic": topic_label,
            "decision_points": [
                {
                    "content": item.content,
                    "relevance": item.relevance_score,
                    "turn": item.source_turn,
                }
                for item in items[:5]
            ],
            "activation_hints": {
                # 决策上下文主要激活的维度
                "primary_dimensions": [
                    "contextual",   # 情境维度
                    "causal",       # 因果维度
                    "temporal",     # 时间维度
                ],
                "secondary_dimensions": [
                    "semantic",     # 语义维度
                    "identity",     # 身份维度
                ],
            },
            "for_reconstructor": True,  # 标记：传递给上下文重构器
        }

    def _extract_to_profile(
        self, 
        items: list[ShortTermMemoryItem],
        topic_label: str = "",
    ) -> dict[str, Any]:
        """
        提炼为用户画像
        
        Args:
            items: 记忆项列表
            topic_label: 话题标签
        """
        return {
            "identity": [],
            "preferences": [item.content for item in items[:3]],
            "source_topic": topic_label,
        }

    def _extract_to_procedural(
        self, 
        items: list[ShortTermMemoryItem],
        topic_label: str = "",
    ) -> dict[str, Any]:
        """
        提炼为程序性记忆
        
        Args:
            items: 记忆项列表
            topic_label: 话题标签
        """
        return {
            "decision_patterns": [
                {
                    "pattern_id": f"dp_{uuid.uuid4().hex[:8]}",
                    "trigger_condition": item.content[:50],
                    "workflow": [],
                    "confidence": item.relevance_score,
                    "usage_count": 1,
                }
                for item in items[:5]
            ],
            "source_topic": topic_label,
        }

    def _extract_to_narrative(
        self, 
        items: list[ShortTermMemoryItem],
        topic_label: str = "",
    ) -> dict[str, Any]:
        """
        提炼为叙事记忆
        
        Args:
            items: 记忆项列表
            topic_label: 话题标签
        """
        return {
            "growth_milestones": [
                {
                    "timestamp": item.created_at.isoformat(),
                    "event": item.content,
                    "significance": f"话题: {topic_label}" if topic_label else "从短期记忆提炼",
                    "importance_score": item.relevance_score,
                }
                for item in items[:3]
            ],
            "source_topic": topic_label,
        }

    def _extract_to_semantic(
        self, 
        items: list[ShortTermMemoryItem],
        topic_label: str = "",
    ) -> dict[str, Any]:
        """
        提炼为语义记忆
        
        Args:
            items: 记忆项列表
            topic_label: 话题标签
        """
        return {
            "core_concepts": [
                {
                    "concept": item.content[:30],
                    "definition": item.content,
                    "usage_count": 1,
                    "confidence": item.relevance_score,
                }
                for item in items[:5]
            ],
            "source_topic": topic_label,
        }

    def _extract_to_emotional(
        self, 
        items: list[ShortTermMemoryItem],
        topic_label: str = "",
    ) -> dict[str, Any]:
        """
        提炼为情感记忆
        
        Args:
            items: 记忆项列表
            topic_label: 话题标签
        """
        return {
            "emotion_states": [
                {
                    "timestamp": item.created_at.isoformat(),
                    "emotion_type": "derived",
                    "intensity": item.relevance_score,
                    "trigger_context": item.content,
                    "topic": topic_label,
                }
                for item in items[:5]
            ],
            "source_topic": topic_label,
        }
    
    def get_last_insight(self) -> Any | None:
        """
        获取最近的洞察结果
        
        Returns:
            最近一次提炼的洞察结果
        """
        return self._last_insight

    def get_stats(self) -> dict[str, Any]:
        """
        获取提炼统计

        Returns:
            统计信息
        """
        return {
            "extraction_count": self._extraction_count,
            "last_extraction_time": (
                self._last_extraction_time.isoformat()
                if self._last_extraction_time
                else None
            ),
            "last_insight_available": self._last_insight is not None,
        }


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "SemanticBucket",
    "ShortTermMemoryManager",
    "AsynchronousExtractor",
]

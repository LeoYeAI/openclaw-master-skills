"""
Agent Memory System - 短期记忆 Redis 存储

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * redis: >=4.5.0
    - 用途：Redis 客户端
  * pydantic: >=2.0.0
    - 用途：数据模型验证
- 标准配置文件:
  ```text
  # requirements.txt
  redis>=4.5.0
  pydantic>=2.0.0
  ```
=== 声明结束 ===

安全提醒：短期记忆可能包含用户对话内容，请确保 Redis 访问安全
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .types import SemanticBucketType
from .redis_adapter import RedisAdapter, RedisConfig, create_redis_adapter, REDIS_AVAILABLE


# ============================================================================
# 数据模型
# ============================================================================


class ShortTermMemoryItemRedis(BaseModel):
    """
    短期记忆项（Redis 存储格式）

    设计考虑：
    - 所有字段都是字符串或基本类型，便于 Redis Hash 存储
    - 包含 TTL 相关字段，支持动态过期
    """

    item_id: str = Field(description="记忆项 ID")
    content: str = Field(description="内容")
    bucket_type: str = Field(description="语义桶类型")
    topic_label: str | None = Field(default=None, description="话题标签")
    relevance_score: float = Field(default=0.5, description="相关性分数")
    created_at: str = Field(description="创建时间（ISO 格式）")
    accessed_at: str = Field(description="最后访问时间（ISO 格式）")
    access_count: int = Field(default=0, description="访问次数")

    def to_hash(self) -> dict[str, str]:
        """转换为 Redis Hash 格式"""
        return {
            "item_id": self.item_id,
            "content": self.content,
            "bucket_type": self.bucket_type,
            "topic_label": self.topic_label or "",
            "relevance_score": str(self.relevance_score),
            "created_at": self.created_at,
            "accessed_at": self.accessed_at,
            "access_count": str(self.access_count),
        }

    @classmethod
    def from_hash(cls, data: dict[str, str]) -> "ShortTermMemoryItemRedis":
        """从 Redis Hash 格式创建"""
        return cls(
            item_id=data["item_id"],
            content=data["content"],
            bucket_type=data["bucket_type"],
            topic_label=data.get("topic_label") or None,
            relevance_score=float(data.get("relevance_score", 0.5)),
            created_at=data["created_at"],
            accessed_at=data["accessed_at"],
            access_count=int(data.get("access_count", 0)),
        )


# ============================================================================
# 配置模型
# ============================================================================


class ShortTermRedisConfig(BaseModel):
    """
    短期记忆 Redis 配置

    使用示例：
    ```python
    config = ShortTermRedisConfig(
        default_ttl=3600,  # 1 小时
        max_items=1000,
    )
    ```
    """

    # TTL 配置
    default_ttl: int = Field(default=3600, description="默认过期时间（秒）")
    ttl_extend_on_access: bool = Field(default=True, description="访问时是否续期")
    ttl_extend_ratio: float = Field(default=0.5, description="续期比例（相对于默认 TTL）")

    # 容量配置
    max_items: int = Field(default=1000, description="每个用户最大记忆项数")

    # 热度配置
    heat_decay_factor: float = Field(default=0.98, description="热度衰减因子")
    heat_access_boost: float = Field(default=1.0, description="访问热度增量")


# ============================================================================
# 短期记忆 Redis 存储
# ============================================================================


class ShortTermMemoryRedis:
    """
    短期记忆 Redis 存储

    特性：
    - 基于 Redis Hash 存储，支持 TTL 自动过期
    - 与热度管理集成，自动更新热度分数
    - 支持按语义桶类型分类存储
    - 支持批量操作

    数据结构：
    - 记忆项: `memory:short:{user_id}:{item_id}` (Hash)
    - 用户记忆列表: `memory:short:{user_id}:list` (Set)
    - 热度排序: `memory:heat:{user_id}` (Sorted Set)

    使用示例：
    ```python
    from scripts.redis_adapter import create_redis_adapter
    from scripts.short_term_redis import ShortTermMemoryRedis

    # 初始化
    redis_adapter = create_redis_adapter(host="localhost", port=6379)
    short_term = ShortTermMemoryRedis(
        redis_adapter=redis_adapter,
        user_id="user123",
    )

    # 存储记忆
    item_id = short_term.store(
        content="用户想要实现登录功能",
        bucket_type=SemanticBucketType.USER_INTENT,
        topic_label="用户登录",
        relevance_score=0.85,
    )

    # 获取记忆
    item = short_term.get(item_id)

    # 按类型获取
    intents = short_term.get_by_bucket(SemanticBucketType.USER_INTENT)

    # 获取热数据
    hot_items = short_term.get_hot_items(limit=10)

    # 获取所有记忆
    all_items = short_term.get_all()

    # 清理过期记忆（手动触发，Redis TTL 自动清理）
    short_term.cleanup_expired()
    ```
    """

    def __init__(
        self,
        redis_adapter: RedisAdapter,
        user_id: str,
        config: ShortTermRedisConfig | None = None,
    ) -> None:
        """
        初始化短期记忆 Redis 存储

        Args:
            redis_adapter: Redis 适配器
            user_id: 用户 ID
            config: 配置参数
        """
        self._redis = redis_adapter
        self._user_id = user_id
        self._config = config or ShortTermRedisConfig()

    # -----------------------------------------------------------------------
    # 内部方法
    # -----------------------------------------------------------------------

    def _item_key(self, item_id: str) -> str:
        """获取记忆项 Key"""
        return self._redis.keys.short_term(self._user_id, item_id)

    def _list_key(self) -> str:
        """获取用户记忆列表 Key"""
        return self._redis.keys.short_term_list(self._user_id)

    def _heat_key(self) -> str:
        """获取热度排序 Key"""
        return self._redis.keys.heat_index(self._user_id)

    def _update_heat(self, item_id: str, score: float) -> None:
        """更新热度分数"""
        heat_key = self._heat_key()
        self._redis.zadd(heat_key, {item_id: score})

    def _calculate_ttl(self) -> int:
        """计算 TTL"""
        return self._config.default_ttl

    # -----------------------------------------------------------------------
    # 存储操作
    # -----------------------------------------------------------------------

    def store(
        self,
        content: str,
        bucket_type: SemanticBucketType,
        topic_label: str | None = None,
        relevance_score: float = 0.5,
        item_id: str | None = None,
    ) -> str:
        """
        存储记忆项

        Args:
            content: 内容
            bucket_type: 语义桶类型
            topic_label: 话题标签
            relevance_score: 相关性分数
            item_id: 指定 ID（可选）

        Returns:
            记忆项 ID
        """
        # 生成 ID
        if item_id is None:
            item_id = f"stm_{uuid.uuid4().hex[:12]}"

        now = datetime.now().isoformat()

        # 创建记忆项
        item = ShortTermMemoryItemRedis(
            item_id=item_id,
            content=content,
            bucket_type=bucket_type.value,
            topic_label=topic_label,
            relevance_score=relevance_score,
            created_at=now,
            accessed_at=now,
            access_count=1,
        )

        # 存储到 Redis Hash
        item_key = self._item_key(item_id)
        self._redis.hset_multi(item_key, item.to_hash())

        # 设置 TTL
        ttl = self._calculate_ttl()
        self._redis.expire(item_key, ttl)

        # 添加到用户记忆列表
        list_key = self._list_key()
        self._redis.hset(list_key, item_id, bucket_type.value)

        # 更新热度（初始热度 = 相关性分数 * 100）
        initial_heat = relevance_score * 100
        self._update_heat(item_id, initial_heat)

        return item_id

    def store_batch(
        self,
        items: list[dict[str, Any]],
    ) -> list[str]:
        """
        批量存储记忆项

        Args:
            items: 记忆项列表，每个项包含 content, bucket_type, topic_label, relevance_score

        Returns:
            记忆项 ID 列表
        """
        item_ids: list[str] = []

        for item in items:
            item_id = self.store(
                content=item.get("content", ""),
                bucket_type=item.get("bucket_type", SemanticBucketType.TASK_CONTEXT),
                topic_label=item.get("topic_label"),
                relevance_score=item.get("relevance_score", 0.5),
            )
            item_ids.append(item_id)

        return item_ids

    # -----------------------------------------------------------------------
    # 读取操作
    # -----------------------------------------------------------------------

    def get(self, item_id: str, update_access: bool = True) -> ShortTermMemoryItemRedis | None:
        """
        获取记忆项

        Args:
            item_id: 记忆项 ID
            update_access: 是否更新访问信息

        Returns:
            记忆项，不存在返回 None
        """
        item_key = self._item_key(item_id)
        data = self._redis.hgetall(item_key)

        if not data:
            return None

        item = ShortTermMemoryItemRedis.from_hash(data)

        # 更新访问信息
        if update_access:
            item.accessed_at = datetime.now().isoformat()
            item.access_count += 1
            self._redis.hset_multi(item_key, item.to_hash())

            # 更新热度
            self._redis.zincrby(
                self._heat_key(),
                self._config.heat_access_boost,
                item_id,
            )

            # 续期 TTL
            if self._config.ttl_extend_on_access:
                extend_ttl = int(self._config.default_ttl * self._config.ttl_extend_ratio)
                self._redis.expire(item_key, extend_ttl)

        return item

    def get_by_bucket(
        self,
        bucket_type: SemanticBucketType,
        limit: int = 100,
    ) -> list[ShortTermMemoryItemRedis]:
        """
        按语义桶类型获取记忆

        Args:
            bucket_type: 语义桶类型
            limit: 最大数量

        Returns:
            记忆项列表
        """
        list_key = self._list_key()
        all_items = self._redis.hgetall(list_key)

        items: list[ShortTermMemoryItemRedis] = []
        count = 0

        for item_id, bt in all_items.items():
            if bt == bucket_type.value:
                item = self.get(item_id, update_access=False)
                if item:
                    items.append(item)
                    count += 1
                    if count >= limit:
                        break

        return items

    def get_hot_items(
        self,
        limit: int = 10,
    ) -> list[ShortTermMemoryItemRedis]:
        """
        获取热度最高的记忆

        Args:
            limit: 最大数量

        Returns:
            记忆项列表（按热度降序）
        """
        heat_key = self._heat_key()
        hot_ids = self._redis.zrange_desc(heat_key, 0, limit - 1)

        items: list[ShortTermMemoryItemRedis] = []
        for item_id in hot_ids:
            if isinstance(item_id, tuple):
                item_id = item_id[0]

            item = self.get(item_id, update_access=False)
            if item:
                items.append(item)

        return items

    def get_all(
        self,
        limit: int = 100,
    ) -> list[ShortTermMemoryItemRedis]:
        """
        获取所有记忆

        Args:
            limit: 最大数量

        Returns:
            记忆项列表
        """
        list_key = self._list_key()
        all_ids = self._redis.hgetall(list_key)

        items: list[ShortTermMemoryItemRedis] = []
        count = 0

        for item_id in all_ids.keys():
            item = self.get(item_id, update_access=False)
            if item:
                items.append(item)
                count += 1
                if count >= limit:
                    break

        return items

    def get_topic_summary(self) -> dict[str, int]:
        """
        获取话题摘要

        Returns:
            话题标签 -> 数量
        """
        items = self.get_all(limit=1000)

        summary: dict[str, int] = {}
        for item in items:
            topic = item.topic_label or "未分类"
            summary[topic] = summary.get(topic, 0) + 1

        # 按数量排序
        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))

    # -----------------------------------------------------------------------
    # 删除操作
    # -----------------------------------------------------------------------

    def delete(self, item_id: str) -> bool:
        """
        删除记忆项

        Args:
            item_id: 记忆项 ID

        Returns:
            是否成功
        """
        # 删除记忆项
        item_key = self._item_key(item_id)
        self._redis.delete(item_key)

        # 从列表中移除
        list_key = self._list_key()
        self._redis.hdel(list_key, item_id)

        # 从热度排序中移除
        heat_key = self._heat_key()
        self._redis.zrem(heat_key, item_id)

        return True

    def clear_all(self) -> int:
        """
        清除所有记忆

        Returns:
            删除的数量
        """
        list_key = self._list_key()
        all_ids = self._redis.hgetall(list_key)

        count = 0
        for item_id in all_ids.keys():
            if self.delete(item_id):
                count += 1

        return count

    # -----------------------------------------------------------------------
    # 统计信息
    # -----------------------------------------------------------------------

    def count(self) -> int:
        """
        获取记忆项数量

        Returns:
            记忆项数量
        """
        list_key = self._list_key()
        all_items = self._redis.hgetall(list_key)
        return len(all_items)

    def count_by_bucket(self) -> dict[str, int]:
        """
        按语义桶类型统计

        Returns:
            桶类型 -> 数量
        """
        list_key = self._list_key()
        all_items = self._redis.hgetall(list_key)

        count: dict[str, int] = {}
        for bucket_type in all_items.values():
            count[bucket_type] = count.get(bucket_type, 0) + 1

        return count

    # -----------------------------------------------------------------------
    # 维护操作
    # -----------------------------------------------------------------------

    def cleanup_expired(self) -> int:
        """
        清理过期记忆（手动触发）

        注意：Redis TTL 会自动清理，此方法用于额外清理热度排序中的过期项

        Returns:
            清理的数量
        """
        list_key = self._list_key()
        all_ids = self._redis.hgetall(list_key)

        cleaned = 0
        for item_id in list(all_ids.keys()):
            item_key = self._item_key(item_id)
            if not self._redis.exists(item_key):
                # 记忆项已过期，从列表和热度中移除
                self._redis.hdel(list_key, item_id)
                self._redis.zrem(self._heat_key(), item_id)
                cleaned += 1

        return cleaned

    def decay_heat(self, factor: float | None = None) -> None:
        """
        热度衰减

        Args:
            factor: 衰减因子（使用配置值）
        """
        if factor is None:
            factor = self._config.heat_decay_factor

        heat_key = self._heat_key()
        items = self._redis.zrange_desc(heat_key, 0, -1, with_scores=True)

        for item in items:
            if isinstance(item, tuple):
                item_id, score = item
                new_score = score * factor
                self._redis.zadd(heat_key, {item_id: new_score})

    def enforce_max_items(self) -> int:
        """
        强制限制记忆项数量

        Returns:
            删除的数量
        """
        current_count = self.count()
        if current_count <= self._config.max_items:
            return 0

        # 按热度排序，删除最低热度的项
        to_remove = current_count - self._config.max_items
        heat_key = self._heat_key()

        # 获取最低热度的项
        cold_items = self._redis.zrange_asc(heat_key, 0, to_remove - 1)

        removed = 0
        for item_id in cold_items:
            if isinstance(item_id, tuple):
                item_id = item_id[0]
            if self.delete(item_id):
                removed += 1

        return removed


# ============================================================================
# 工厂函数
# ============================================================================


def create_short_term_redis(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    user_id: str = "default_user",
    default_ttl: int = 3600,
    max_items: int = 1000,
) -> ShortTermMemoryRedis:
    """
    创建短期记忆 Redis 存储

    Args:
        redis_host: Redis 主机
        redis_port: Redis 端口
        user_id: 用户 ID
        default_ttl: 默认过期时间（秒）
        max_items: 最大记忆项数

    Returns:
        ShortTermMemoryRedis 实例
    """
    redis_adapter = create_redis_adapter(host=redis_host, port=redis_port)
    config = ShortTermRedisConfig(default_ttl=default_ttl, max_items=max_items)

    return ShortTermMemoryRedis(
        redis_adapter=redis_adapter,
        user_id=user_id,
        config=config,
    )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "ShortTermMemoryItemRedis",
    "ShortTermRedisConfig",
    "ShortTermMemoryRedis",
    "create_short_term_redis",
]

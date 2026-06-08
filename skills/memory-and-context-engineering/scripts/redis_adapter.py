"""
Agent Memory System - Redis 适配器

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * redis: >=4.5.0
    - 用途：Redis 客户端连接与操作
  * pydantic: >=2.0.0
    - 用途：配置模型验证
- 标准配置文件:
  ```text
  # requirements.txt
  redis>=4.5.0
  pydantic>=2.0.0
  ```
=== 声明结束 ===

安全提醒：生产环境请使用 Redis 密码认证，并考虑 TLS 加密
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Callable

from pydantic import BaseModel, Field

# 延迟导入 redis，支持无 Redis 环境运行
try:
    import redis
    from redis import Redis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None  # type: ignore
    RedisError = Exception  # type: ignore
    RedisConnectionError = Exception  # type: ignore


# ============================================================================
# 配置模型
# ============================================================================


class RedisConfig(BaseModel):
    """
    Redis 连接配置

    支持单机模式，集群模式可后续扩展。

    使用示例：
    ```python
    config = RedisConfig(
        host="localhost",
        port=6379,
        password="your_password",
        db=0,
    )
    adapter = RedisAdapter(config)
    ```
    """

    host: str = Field(default="localhost", description="Redis 主机地址")
    port: int = Field(default=6379, description="Redis 端口")
    password: str | None = Field(default=None, description="Redis 密码")
    db: int = Field(default=0, description="Redis 数据库编号")

    # 连接池配置
    max_connections: int = Field(default=10, description="最大连接数")
    socket_timeout: float = Field(default=5.0, description="Socket 超时（秒）")
    socket_connect_timeout: float = Field(default=5.0, description="连接超时（秒）")
    retry_on_timeout: bool = Field(default=True, description="超时是否重试")
    retry_on_error: int = Field(default=3, description="错误重试次数")

    # 健康检查配置
    health_check_interval: int = Field(default=30, description="健康检查间隔（秒）")

    # Key 前缀
    key_prefix: str = Field(default="memory", description="所有 Key 的前缀")


# ============================================================================
# Key 命名工具
# ============================================================================


class RedisKeyBuilder:
    """
    Redis Key 命名工具

    命名规范：
    - 前缀: {key_prefix}
    - 格式: {prefix}:{type}:{user_id}:{item_id}
    - 示例: memory:short:user123:item456

    使用示例：
    ```python
    builder = RedisKeyBuilder("memory")

    # 短期记忆
    key = builder.short_term("user123", "item456")
    # → "memory:short:user123:item456"

    # 热度排序
    key = builder.heat_index("user123")
    # → "memory:heat:user123"

    # Token 计数
    key = builder.token_counter("session789")
    # → "memory:token:session789"
    ```
    """

    def __init__(self, prefix: str = "memory") -> None:
        """
        初始化 Key 构建器

        Args:
            prefix: Key 前缀
        """
        self._prefix = prefix

    def _build(self, *parts: str) -> str:
        """构建完整 Key"""
        return ":".join([self._prefix] + list(parts))

    # -----------------------------------------------------------------------
    # 短期记忆相关
    # -----------------------------------------------------------------------

    def short_term(self, user_id: str, item_id: str) -> str:
        """短期记忆项 Key"""
        return self._build("short", user_id, item_id)

    def short_term_list(self, user_id: str) -> str:
        """短期记忆列表 Key（用于存储所有 item_id）"""
        return self._build("short", user_id, "list")

    # -----------------------------------------------------------------------
    # 热度管理相关
    # -----------------------------------------------------------------------

    def heat_index(self, user_id: str) -> str:
        """热度排序 Key（Sorted Set）"""
        return self._build("heat", user_id)

    # -----------------------------------------------------------------------
    # Token 预算相关
    # -----------------------------------------------------------------------

    def token_counter(self, session_id: str) -> str:
        """Token 计数器 Key"""
        return self._build("token", session_id)

    def token_budget(self, session_id: str) -> str:
        """Token 预算配置 Key"""
        return self._build("token", session_id, "budget")

    # -----------------------------------------------------------------------
    # 长期记忆相关
    # -----------------------------------------------------------------------

    def long_term_profile(self, user_id: str) -> str:
        """用户画像 Key"""
        return self._build("long", "profile", user_id)

    def long_term_procedural(self, user_id: str) -> str:
        """程序性记忆 Key"""
        return self._build("long", "procedural", user_id)

    def long_term_reflection(self, user_id: str) -> str:
        """反思记忆列表 Key"""
        return self._build("long", "reflection", user_id)

    # -----------------------------------------------------------------------
    # 检索缓存相关
    # -----------------------------------------------------------------------

    def retrieval_cache(self, query_hash: str) -> str:
        """检索结果缓存 Key"""
        return self._build("cache", "retrieval", query_hash)

    # -----------------------------------------------------------------------
    # 状态相关
    # -----------------------------------------------------------------------

    def state_checkpoint(self, user_id: str, checkpoint_id: str) -> str:
        """状态检查点 Key"""
        return self._build("state", user_id, checkpoint_id)

    def state_current(self, user_id: str) -> str:
        """当前状态 Key"""
        return self._build("state", user_id, "current")


# ============================================================================
# Redis 适配器
# ============================================================================


class RedisAdapter:
    """
    Redis 适配器

    提供 Redis 连接管理和基础操作封装。

    特性：
    - 连接池管理
    - 健康检查
    - 断线重连
    - 操作重试
    - Key 命名工具集成

    使用示例：
    ```python
    from scripts.redis_adapter import RedisConfig, RedisAdapter

    # 初始化
    config = RedisConfig(host="localhost", port=6379)
    adapter = RedisAdapter(config)

    # 检查连接
    if adapter.is_available():
        # 基础操作
        adapter.set("test_key", "test_value", ttl=60)
        value = adapter.get("test_key")

        # Hash 操作
        adapter.hset("hash_key", "field1", "value1")
        data = adapter.hgetall("hash_key")

        # Sorted Set 操作
        adapter.zadd("sorted_key", {"member1": 100, "member2": 50})
        top_items = adapter.zrange_desc("sorted_key", 0, 9)

    # 上下文管理器
    with adapter.pipeline() as pipe:
        pipe.set("key1", "value1")
        pipe.set("key2", "value2")
        pipe.execute()
    ```
    """

    def __init__(self, config: RedisConfig) -> None:
        """
        初始化 Redis 适配器

        Args:
            config: Redis 配置
        """
        self._config = config
        self._client: Redis | None = None
        self._key_builder = RedisKeyBuilder(config.key_prefix)
        self._last_health_check: float = 0.0
        self._is_available = False

        # 尝试初始化连接
        if REDIS_AVAILABLE:
            self._connect()
        else:
            self._is_available = False

    # -----------------------------------------------------------------------
    # 连接管理
    # -----------------------------------------------------------------------

    def _connect(self) -> bool:
        """
        建立 Redis 连接（内部方法）

        Returns:
            是否连接成功
        """
        if not REDIS_AVAILABLE:
            return False

        try:
            self._client = Redis(
                host=self._config.host,
                port=self._config.port,
                password=self._config.password,
                db=self._config.db,
                max_connections=self._config.max_connections,
                socket_timeout=self._config.socket_timeout,
                socket_connect_timeout=self._config.socket_connect_timeout,
                retry_on_timeout=self._config.retry_on_timeout,
                decode_responses=True,  # 自动解码为字符串
            )

            # 测试连接
            self._client.ping()
            self._is_available = True
            return True

        except (RedisError, OSError) as e:
            self._client = None
            self._is_available = False
            return False

    def _ensure_connection(self) -> bool:
        """
        确保连接可用（内部方法）

        Returns:
            连接是否可用
        """
        if self._client is None:
            return self._connect()

        # 检查是否需要健康检查
        now = time.time()
        if now - self._last_health_check > self._config.health_check_interval:
            if not self._health_check():
                # 健康检查失败，尝试重连
                return self._connect()

        return True

    def _health_check(self) -> bool:
        """
        健康检查（内部方法）

        Returns:
            健康状态
        """
        if self._client is None:
            return False

        try:
            self._client.ping()
            self._last_health_check = time.time()
            self._is_available = True
            return True
        except (RedisError, OSError):
            self._is_available = False
            return False

    def is_available(self) -> bool:
        """
        检查 Redis 是否可用

        Returns:
            是否可用
        """
        return self._ensure_connection()

    def close(self) -> None:
        """关闭连接"""
        if self._client is not None:
            try:
                self._client.close()
            except RedisError:
                pass
            finally:
                self._client = None
                self._is_available = False

    # -----------------------------------------------------------------------
    # Key 构建器
    # -----------------------------------------------------------------------

    @property
    def keys(self) -> RedisKeyBuilder:
        """获取 Key 构建器"""
        return self._key_builder

    # -----------------------------------------------------------------------
    # 基础操作
    # -----------------------------------------------------------------------

    def get(self, key: str) -> str | None:
        """
        获取值

        Args:
            key: Key

        Returns:
            值，不存在返回 None
        """
        if not self._ensure_connection() or self._client is None:
            return None

        try:
            return self._client.get(key)
        except RedisError:
            return None

    def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """
        设置值

        Args:
            key: Key
            value: 值
            ttl: 过期时间（秒）
            nx: 仅当 Key 不存在时设置
            xx: 仅当 Key 存在时设置

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            result = self._client.set(key, value, ex=ttl, nx=nx, xx=xx)
            return result is not False
        except RedisError:
            return False

    def delete(self, key: str) -> bool:
        """
        删除 Key

        Args:
            key: Key

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            self._client.delete(key)
            return True
        except RedisError:
            return False

    def exists(self, key: str) -> bool:
        """
        检查 Key 是否存在

        Args:
            key: Key

        Returns:
            是否存在
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            return self._client.exists(key) > 0
        except RedisError:
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置过期时间

        Args:
            key: Key
            ttl: 过期时间（秒）

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            return self._client.expire(key, ttl)
        except RedisError:
            return False

    def ttl(self, key: str) -> int:
        """
        获取剩余过期时间

        Args:
            key: Key

        Returns:
            剩余秒数，-1 表示永不过期，-2 表示不存在
        """
        if not self._ensure_connection() or self._client is None:
            return -2

        try:
            return self._client.ttl(key)
        except RedisError:
            return -2

    # -----------------------------------------------------------------------
    # Hash 操作
    # -----------------------------------------------------------------------

    def hset(self, key: str, field: str, value: str) -> bool:
        """
        设置 Hash 字段

        Args:
            key: Key
            field: 字段名
            value: 值

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            self._client.hset(key, field, value)
            return True
        except RedisError:
            return False

    def hset_multi(self, key: str, mapping: dict[str, str]) -> bool:
        """
        批量设置 Hash 字段

        Args:
            key: Key
            mapping: 字段-值映射

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            self._client.hset(key, mapping=mapping)
            return True
        except RedisError:
            return False

    def hget(self, key: str, field: str) -> str | None:
        """
        获取 Hash 字段值

        Args:
            key: Key
            field: 字段名

        Returns:
            值，不存在返回 None
        """
        if not self._ensure_connection() or self._client is None:
            return None

        try:
            return self._client.hget(key, field)
        except RedisError:
            return None

    def hgetall(self, key: str) -> dict[str, str]:
        """
        获取 Hash 所有字段

        Args:
            key: Key

        Returns:
            字段-值映射
        """
        if not self._ensure_connection() or self._client is None:
            return {}

        try:
            result = self._client.hgetall(key)
            return result if result else {}
        except RedisError:
            return {}

    def hdel(self, key: str, field: str) -> bool:
        """
        删除 Hash 字段

        Args:
            key: Key
            field: 字段名

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            self._client.hdel(key, field)
            return True
        except RedisError:
            return False

    def hexists(self, key: str, field: str) -> bool:
        """
        检查 Hash 字段是否存在

        Args:
            key: Key
            field: 字段名

        Returns:
            是否存在
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            return self._client.hexists(key, field)
        except RedisError:
            return False

    # -----------------------------------------------------------------------
    # Sorted Set 操作
    # -----------------------------------------------------------------------

    def zadd(self, key: str, mapping: dict[str, float]) -> bool:
        """
        添加 Sorted Set 成员

        Args:
            key: Key
            mapping: 成员-分数映射

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            self._client.zadd(key, mapping)
            return True
        except RedisError:
            return False

    def zincrby(self, key: str, amount: float, member: str) -> float | None:
        """
        增加 Sorted Set 成员分数

        Args:
            key: Key
            amount: 增量
            member: 成员

        Returns:
            新分数，失败返回 None
        """
        if not self._ensure_connection() or self._client is None:
            return None

        try:
            return self._client.zincrby(key, amount, member)
        except RedisError:
            return None

    def zscore(self, key: str, member: str) -> float | None:
        """
        获取 Sorted Set 成员分数

        Args:
            key: Key
            member: 成员

        Returns:
            分数，不存在返回 None
        """
        if not self._ensure_connection() or self._client is None:
            return None

        try:
            return self._client.zscore(key, member)
        except RedisError:
            return None

    def zrange_desc(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
        with_scores: bool = False,
    ) -> list[str] | list[tuple[str, float]]:
        """
        按分数降序获取 Sorted Set 成员

        Args:
            key: Key
            start: 起始位置
            end: 结束位置
            with_scores: 是否返回分数

        Returns:
            成员列表，或 (成员, 分数) 列表
        """
        if not self._ensure_connection() or self._client is None:
            return []

        try:
            result = self._client.zrange(
                key, start, end, desc=True, withscores=with_scores
            )
            return result if result else []
        except RedisError:
            return []

    def zrange_asc(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
        with_scores: bool = False,
    ) -> list[str] | list[tuple[str, float]]:
        """
        按分数升序获取 Sorted Set 成员

        Args:
            key: Key
            start: 起始位置
            end: 结束位置
            with_scores: 是否返回分数

        Returns:
            成员列表，或 (成员, 分数) 列表
        """
        if not self._ensure_connection() or self._client is None:
            return []

        try:
            result = self._client.zrange(
                key, start, end, desc=False, withscores=with_scores
            )
            return result if result else []
        except RedisError:
            return []

    def zrem(self, key: str, member: str) -> bool:
        """
        删除 Sorted Set 成员

        Args:
            key: Key
            member: 成员

        Returns:
            是否成功
        """
        if not self._ensure_connection() or self._client is None:
            return False

        try:
            self._client.zrem(key, member)
            return True
        except RedisError:
            return False

    def zremrangebyrank(self, key: str, start: int, end: int) -> int:
        """
        按排名范围删除 Sorted Set 成员

        Args:
            key: Key
            start: 起始排名
            end: 结束排名

        Returns:
            删除的数量
        """
        if not self._ensure_connection() or self._client is None:
            return 0

        try:
            return self._client.zremrangebyrank(key, start, end)
        except RedisError:
            return 0

    def zcard(self, key: str) -> int:
        """
        获取 Sorted Set 成员数量

        Args:
            key: Key

        Returns:
            成员数量
        """
        if not self._ensure_connection() or self._client is None:
            return 0

        try:
            return self._client.zcard(key)
        except RedisError:
            return 0

    # -----------------------------------------------------------------------
    # 计数器操作
    # -----------------------------------------------------------------------

    def incr(self, key: str, amount: int = 1) -> int | None:
        """
        增加计数器

        Args:
            key: Key
            amount: 增量

        Returns:
            新值，失败返回 None
        """
        if not self._ensure_connection() or self._client is None:
            return None

        try:
            return self._client.incrby(key, amount)
        except RedisError:
            return None

    def decr(self, key: str, amount: int = 1) -> int | None:
        """
        减少计数器

        Args:
            key: Key
            amount: 减量

        Returns:
            新值，失败返回 None
        """
        if not self._ensure_connection() or self._client is None:
            return None

        try:
            return self._client.decrby(key, amount)
        except RedisError:
            return None

    # -----------------------------------------------------------------------
    # Pipeline
    # -----------------------------------------------------------------------

    @contextmanager
    def pipeline(self):
        """
        获取 Pipeline 上下文管理器

        使用示例：
        ```python
        with adapter.pipeline() as pipe:
            pipe.set("key1", "value1")
            pipe.set("key2", "value2")
            pipe.execute()
        ```
        """
        if not self._ensure_connection() or self._client is None:
            yield None
            return

        pipe = self._client.pipeline()
        try:
            yield pipe
        finally:
            try:
                pipe.reset()
            except RedisError:
                pass

    # -----------------------------------------------------------------------
    # 批量操作
    # -----------------------------------------------------------------------

    def delete_pattern(self, pattern: str) -> int:
        """
        按模式删除 Key

        注意：生产环境慎用，SCAN 可能阻塞

        Args:
            pattern: Key 模式（如 "memory:short:user123:*"）

        Returns:
            删除的数量
        """
        if not self._ensure_connection() or self._client is None:
            return 0

        try:
            keys = []
            for key in self._client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return self._client.delete(*keys)
            return 0
        except RedisError:
            return 0


# ============================================================================
# 工厂函数
# ============================================================================


def create_redis_adapter(
    host: str = "localhost",
    port: int = 6379,
    password: str | None = None,
    db: int = 0,
    key_prefix: str = "memory",
) -> RedisAdapter:
    """
    创建 Redis 适配器

    Args:
        host: Redis 主机地址
        port: Redis 端口
        password: Redis 密码
        db: Redis 数据库编号
        key_prefix: Key 前缀

    Returns:
        RedisAdapter 实例
    """
    config = RedisConfig(
        host=host,
        port=port,
        password=password,
        db=db,
        key_prefix=key_prefix,
    )
    return RedisAdapter(config)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "REDIS_AVAILABLE",
    "RedisConfig",
    "RedisKeyBuilder",
    "RedisAdapter",
    "create_redis_adapter",
]

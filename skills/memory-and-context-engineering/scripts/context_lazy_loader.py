"""
Agent Memory System - Context Lazy Loader（上下文懒加载器）

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * redis: >=4.5.0
    - 用途：缓存和状态存储
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  redis>=4.5.0
  ```
=== 声明结束 ===

安全提醒：懒加载需确保数据完整性和一致性
"""

from __future__ import annotations

import time
from collections import OrderedDict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

from pydantic import BaseModel, Field

from .redis_adapter import RedisAdapter


# ============================================================================
# 枚举类型
# ============================================================================


class LoadPriority(str, Enum):
    """加载优先级"""

    CRITICAL = "critical"  # 必须立即加载
    HIGH = "high"          # 高优先级
    MEDIUM = "medium"      # 中优先级
    LOW = "low"            # 低优先级
    BACKGROUND = "background"  # 后台加载


class LoadStatus(str, Enum):
    """加载状态"""

    PENDING = "pending"      # 待加载
    LOADING = "loading"      # 加载中
    LOADED = "loaded"        # 已加载
    FAILED = "failed"        # 加载失败
    CACHED = "cached"        # 已缓存


class PredictStrategy(str, Enum):
    """预加载策略"""

    NONE = "none"                # 不预测
    SEQUENTIAL = "sequential"    # 顺序预测
    PATTERN = "pattern"          # 模式预测
    ML_BASED = "ml_based"        # 机器学习预测


# ============================================================================
# 数据模型
# ============================================================================


T = TypeVar("T")


class LoadRequest(BaseModel, Generic[T]):
    """加载请求"""

    request_id: str = Field(
        default_factory=lambda: f"req_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    key: str                                      # 数据键
    loader: Callable[[], T] | None = None        # 加载函数（无法序列化，运行时设置）
    priority: LoadPriority = LoadPriority.MEDIUM
    dependencies: list[str] = Field(default_factory=list)  # 依赖的键
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class LoadResult(BaseModel, Generic[T]):
    """加载结果"""

    request_id: str
    key: str
    status: LoadStatus
    data: Any | None = None
    error: str | None = None
    load_time_ms: float = Field(default=0.0)
    cache_hit: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)


class CacheEntry(BaseModel, Generic[T]):
    """缓存条目"""

    key: str
    data: Any
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0)
    ttl_seconds: int | None = None  # Time to live
    size_bytes: int = Field(default=0)


class LoaderConfig(BaseModel):
    """懒加载器配置"""

    # 缓存配置
    enable_cache: bool = Field(default=True)
    max_cache_size: int = Field(default=1000)          # 最大缓存条目数
    max_cache_bytes: int = Field(default=100 * 1024 * 1024)  # 最大缓存大小（100MB）
    default_ttl: int = Field(default=3600)            # 默认 TTL（秒）

    # 预加载配置
    enable_preload: bool = Field(default=True)
    preload_strategy: PredictStrategy = Field(default=PredictStrategy.SEQUENTIAL)
    preload_concurrency: int = Field(default=3)       # 并发预加载数

    # 加载配置
    load_timeout: int = Field(default=30)             # 加载超时（秒）
    retry_count: int = Field(default=3)               # 重试次数
    retry_delay: float = Field(default=0.5)           # 重试延迟（秒）

    # 优先级队列配置
    priority_queue_size: int = Field(default=100)     # 优先级队列大小


class LoaderStats(BaseModel):
    """加载器统计"""

    total_requests: int = Field(default=0)
    cache_hits: int = Field(default=0)
    cache_misses: int = Field(default=0)
    preload_hits: int = Field(default=0)
    preload_misses: int = Field(default=0)
    total_load_time_ms: float = Field(default=0.0)
    errors: int = Field(default=0)

    @property
    def cache_hit_rate(self) -> float:
        """缓存命中率"""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    @property
    def avg_load_time_ms(self) -> float:
        """平均加载时间"""
        if self.total_requests == 0:
            return 0.0
        return self.total_load_time_ms / self.total_requests


# ============================================================================
# LRUCache
# ============================================================================


class LRUCache(Generic[T]):
    """
    LRU 缓存实现
    
    线程安全的 LRU 缓存，支持 TTL 和大小限制
    """

    def __init__(
        self,
        max_size: int = 1000,
        max_bytes: int = 100 * 1024 * 1024,
        default_ttl: int = 3600,
    ):
        """初始化 LRU 缓存"""
        self._max_size = max_size
        self._max_bytes = max_bytes
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._current_bytes = 0

    def get(self, key: str) -> T | None:
        """获取缓存值"""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # 检查 TTL
        if entry.ttl_seconds is not None:
            age = (datetime.now() - entry.created_at).total_seconds()
            if age > entry.ttl_seconds:
                self.delete(key)
                return None

        # 更新访问信息
        entry.last_accessed = datetime.now()
        entry.access_count += 1

        # 移动到末尾（最近使用）
        self._cache.move_to_end(key)

        return entry.data

    def set(
        self,
        key: str,
        value: T,
        ttl_seconds: int | None = None,
        size_bytes: int = 0,
    ) -> None:
        """设置缓存值"""
        # 如果已存在，先删除
        if key in self._cache:
            self.delete(key)

        # 检查是否需要淘汰
        while (
            len(self._cache) >= self._max_size
            or self._current_bytes + size_bytes > self._max_bytes
        ):
            if not self._evict_one():
                break

        # 创建条目
        entry = CacheEntry(
            key=key,
            data=value,
            ttl_seconds=ttl_seconds or self._default_ttl,
            size_bytes=size_bytes,
        )

        self._cache[key] = entry
        self._current_bytes += size_bytes

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        if key not in self._cache:
            return False

        entry = self._cache[key]
        self._current_bytes -= entry.size_bytes
        del self._cache[key]
        return True

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._current_bytes = 0

    def _evict_one(self) -> bool:
        """淘汰一个条目"""
        if not self._cache:
            return False

        # 淘汰最旧的（LRU）
        oldest_key = next(iter(self._cache))
        self.delete(oldest_key)
        return True

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "bytes": self._current_bytes,
            "max_bytes": self._max_bytes,
            "utilization": len(self._cache) / self._max_size if self._max_size > 0 else 0,
        }


# ============================================================================
# Priority Queue
# ============================================================================


class PriorityQueue:
    """
    优先级队列
    
    按优先级排序的加载请求队列
    """

    def __init__(self, max_size: int = 100):
        """初始化优先级队列"""
        self._max_size = max_size
        self._queues: dict[LoadPriority, list[LoadRequest]] = {
            LoadPriority.CRITICAL: [],
            LoadPriority.HIGH: [],
            LoadPriority.MEDIUM: [],
            LoadPriority.LOW: [],
            LoadPriority.BACKGROUND: [],
        }

    def push(self, request: LoadRequest) -> bool:
        """添加请求"""
        total = sum(len(q) for q in self._queues.values())
        if total >= self._max_size:
            return False

        self._queues[request.priority].append(request)
        return True

    def pop(self) -> LoadRequest | None:
        """取出最高优先级请求"""
        for priority in [
            LoadPriority.CRITICAL,
            LoadPriority.HIGH,
            LoadPriority.MEDIUM,
            LoadPriority.LOW,
            LoadPriority.BACKGROUND,
        ]:
            if self._queues[priority]:
                return self._queues[priority].pop(0)
        return None

    def peek(self) -> LoadRequest | None:
        """查看最高优先级请求"""
        for priority in [
            LoadPriority.CRITICAL,
            LoadPriority.HIGH,
            LoadPriority.MEDIUM,
            LoadPriority.LOW,
            LoadPriority.BACKGROUND,
        ]:
            if self._queues[priority]:
                return self._queues[priority][0]
        return None

    def clear(self) -> None:
        """清空队列"""
        for queue in self._queues.values():
            queue.clear()

    def size(self) -> int:
        """获取队列大小"""
        return sum(len(q) for q in self._queues.values())


# ============================================================================
# Context Lazy Loader
# ============================================================================


class ContextLazyLoader:
    """
    上下文懒加载器
    
    职责：
    - 按需加载上下文数据
    - 智能预加载预测需要的数据
    - 管理加载优先级队列
    - 缓存管理
    
    使用示例：
    ```python
    from scripts.context_lazy_loader import ContextLazyLoader, LoadPriority

    loader = ContextLazyLoader()

    # 注册加载器
    loader.register_loader("user_profile", lambda: fetch_user_profile())

    # 请求数据
    result = loader.load("user_profile", priority=LoadPriority.HIGH)
    print(result.data)

    # 预加载
    loader.preload(["user_settings", "recent_tasks"])
    ```
    """

    def __init__(
        self,
        config: LoaderConfig | None = None,
        redis_adapter: RedisAdapter | None = None,
    ):
        """初始化懒加载器"""
        self._config = config or LoaderConfig()
        self._redis = redis_adapter

        # 缓存
        self._cache = LRUCache(
            max_size=self._config.max_cache_size,
            max_bytes=self._config.max_cache_bytes,
            default_ttl=self._config.default_ttl,
        )

        # 优先级队列
        self._queue = PriorityQueue(max_size=self._config.priority_queue_size)

        # 注册的加载器
        self._loaders: dict[str, Callable[[], Any]] = {}

        # 加载结果缓存
        self._results: dict[str, LoadResult] = {}

        # 统计
        self._stats = LoaderStats()

        # 访问模式追踪（用于预测）
        self._access_patterns: dict[str, list[str]] = {}

    # -----------------------------------------------------------------------
    # 加载器注册
    # -----------------------------------------------------------------------

    def register_loader(
        self,
        key: str,
        loader: Callable[[], Any],
    ) -> None:
        """
        注册数据加载器

        Args:
            key: 数据键
            loader: 加载函数
        """
        self._loaders[key] = loader

    def unregister_loader(self, key: str) -> None:
        """注销数据加载器"""
        self._loaders.pop(key, None)

    # -----------------------------------------------------------------------
    # 核心方法：加载数据
    # -----------------------------------------------------------------------

    def load(
        self,
        key: str,
        priority: LoadPriority = LoadPriority.MEDIUM,
        use_cache: bool = True,
    ) -> LoadResult:
        """
        加载数据

        Args:
            key: 数据键
            priority: 加载优先级
            use_cache: 是否使用缓存

        Returns:
            LoadResult 加载结果
        """
        start_time = time.time()
        self._stats.total_requests += 1

        # 检查缓存
        if use_cache and self._config.enable_cache:
            cached = self._cache.get(key)
            if cached is not None:
                self._stats.cache_hits += 1
                return LoadResult(
                    request_id=f"cached_{key}",
                    key=key,
                    status=LoadStatus.CACHED,
                    data=cached,
                    cache_hit=True,
                    load_time_ms=(time.time() - start_time) * 1000,
                )

        self._stats.cache_misses += 1

        # 检查是否已注册加载器
        if key not in self._loaders:
            self._stats.errors += 1
            return LoadResult(
                request_id=f"error_{key}",
                key=key,
                status=LoadStatus.FAILED,
                error=f"No loader registered for key: {key}",
            )

        # 执行加载
        result = self._execute_load(key)

        # 更新缓存
        if (
            result.status == LoadStatus.LOADED
            and use_cache
            and self._config.enable_cache
        ):
            self._cache.set(key, result.data)

        # 更新访问模式
        self._update_access_pattern(key)

        result.load_time_ms = (time.time() - start_time) * 1000
        self._stats.total_load_time_ms += result.load_time_ms

        return result

    def _execute_load(self, key: str) -> LoadResult:
        """执行加载"""
        loader = self._loaders[key]

        for attempt in range(self._config.retry_count):
            try:
                data = loader()
                return LoadResult(
                    request_id=f"load_{key}",
                    key=key,
                    status=LoadStatus.LOADED,
                    data=data,
                )
            except Exception as e:
                if attempt == self._config.retry_count - 1:
                    self._stats.errors += 1
                    return LoadResult(
                        request_id=f"error_{key}",
                        key=key,
                        status=LoadStatus.FAILED,
                        error=str(e),
                    )
                time.sleep(self._config.retry_delay)

        return LoadResult(
            request_id=f"error_{key}",
            key=key,
            status=LoadStatus.FAILED,
            error="Unknown error",
        )

    def load_batch(
        self,
        keys: list[str],
        priority: LoadPriority = LoadPriority.MEDIUM,
    ) -> dict[str, LoadResult]:
        """
        批量加载

        Args:
            keys: 数据键列表
            priority: 加载优先级

        Returns:
            字典 {key: LoadResult}
        """
        results: dict[str, LoadResult] = {}

        for key in keys:
            results[key] = self.load(key, priority=priority)

        return results

    # -----------------------------------------------------------------------
    # 预加载
    # -----------------------------------------------------------------------

    def preload(
        self,
        keys: list[str],
        priority: LoadPriority = LoadPriority.LOW,
    ) -> None:
        """
        预加载数据

        Args:
            keys: 数据键列表
            priority: 加载优先级
        """
        if not self._config.enable_preload:
            return

        for key in keys:
            # 检查是否已缓存
            if self._cache.get(key) is not None:
                continue

            # 添加到队列
            request = LoadRequest(
                key=key,
                priority=priority,
            )
            self._queue.push(request)

        # 处理队列
        self._process_preload_queue()

    def predict_and_preload(self, current_key: str) -> list[str]:
        """
        基于访问模式预测并预加载

        Args:
            current_key: 当前访问的键

        Returns:
            预加载的键列表
        """
        if self._config.preload_strategy == PredictStrategy.NONE:
            return []

        predicted = self._predict_next_keys(current_key)

        if predicted:
            self.preload(predicted, priority=LoadPriority.BACKGROUND)

        return predicted

    def _predict_next_keys(self, current_key: str) -> list[str]:
        """预测下一个可能访问的键"""
        if current_key not in self._access_patterns:
            return []

        # 简单的顺序预测：取最近访问模式中的后续键
        patterns = self._access_patterns[current_key]
        if not patterns:
            return []

        # 统计频率，返回最常见的
        freq: dict[str, int] = {}
        for key in patterns[-10:]:  # 最近10次
            freq[key] = freq.get(key, 0) + 1

        sorted_keys = sorted(freq.items(), key=lambda x: -x[1])
        return [k for k, _ in sorted_keys[:3]]

    def _update_access_pattern(self, key: str) -> None:
        """更新访问模式"""
        # 记录从上一个键到当前键的转移
        if hasattr(self, "_last_key") and self._last_key:
            if self._last_key not in self._access_patterns:
                self._access_patterns[self._last_key] = []
            self._access_patterns[self._last_key].append(key)

        self._last_key = key

    def _process_preload_queue(self) -> None:
        """处理预加载队列"""
        processed = 0
        max_concurrent = self._config.preload_concurrency

        while processed < max_concurrent:
            request = self._queue.pop()
            if request is None:
                break

            # 异步加载（简化实现，实际可用线程池）
            result = self.load(request.key, priority=request.priority)

            if result.status == LoadStatus.LOADED:
                self._stats.preload_hits += 1
            else:
                self._stats.preload_misses += 1

            processed += 1

    # -----------------------------------------------------------------------
    # 缓存管理
    # -----------------------------------------------------------------------

    def invalidate(self, key: str) -> bool:
        """使缓存失效"""
        return self._cache.delete(key)

    def invalidate_all(self) -> None:
        """清空所有缓存"""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        return self._cache.get_stats()

    # -----------------------------------------------------------------------
    # 统计与监控
    # -----------------------------------------------------------------------

    def get_stats(self) -> LoaderStats:
        """获取加载器统计"""
        return self._stats

    def reset_stats(self) -> None:
        """重置统计"""
        self._stats = LoaderStats()


# ============================================================================
# 工厂函数
# ============================================================================


def create_lazy_loader(
    max_cache_size: int = 1000,
    enable_preload: bool = True,
    redis_adapter: RedisAdapter | None = None,
) -> ContextLazyLoader:
    """
    创建懒加载器

    Args:
        max_cache_size: 最大缓存大小
        enable_preload: 启用预加载
        redis_adapter: Redis 适配器（可选）

    Returns:
        ContextLazyLoader 实例
    """
    config = LoaderConfig(
        max_cache_size=max_cache_size,
        enable_preload=enable_preload,
    )

    return ContextLazyLoader(config=config, redis_adapter=redis_adapter)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "LoadPriority",
    "LoadStatus",
    "PredictStrategy",
    "LoadRequest",
    "LoadResult",
    "CacheEntry",
    "LoaderConfig",
    "LoaderStats",
    "LRUCache",
    "PriorityQueue",
    "ContextLazyLoader",
    "create_lazy_loader",
]

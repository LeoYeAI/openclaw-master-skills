"""
Agent Memory System - Batched Writer（批量写入器）

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

设计说明：
批量写入器通过延迟写入和合并策略，减少文件 I/O 次数。
适用于高频更新但可以容忍短暂延迟的场景。

核心特性：
1. 相同文件的多次写入自动合并
2. 延迟写入，减少 I/O 次数
3. 可配置延迟时间和最大批次
"""

from __future__ import annotations

import json
import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 数据模型
# ============================================================================


class BatchedWriterConfig(BaseModel):
    """批量写入器配置"""

    # 延迟写入
    delay_seconds: float = Field(default=0.5, ge=0.1, le=10.0, description="延迟写入时间（秒）")

    # 批量配置
    max_batch_size: int = Field(default=50, ge=1, le=500, description="最大批次大小")

    # 合并策略
    deep_merge: bool = Field(default=True, description="是否深度合并嵌套字典")

    # 统计
    track_stats: bool = Field(default=True, description="是否追踪统计")


class BatchedWriterStats(BaseModel):
    """批量写入器统计"""

    total_requests: int = Field(default=0)
    merged_requests: int = Field(default=0)
    actual_writes: int = Field(default=0)
    failed_writes: int = Field(default=0)
    current_pending: int = Field(default=0)


# ============================================================================
# Batched Writer
# ============================================================================


class BatchedWriter:
    """
    批量写入器

    特性：
    - 相同文件的多次写入自动合并
    - 延迟写入，减少 I/O 次数
    - 可配置延迟时间和最大批次

    使用示例：
    ```python
    from scripts.batched_writer import BatchedWriter

    writer = BatchedWriter(delay_seconds=0.5)

    # 多次写入同一文件会被合并
    writer.write("./data/memory.json", {"key1": "value1"})
    writer.write("./data/memory.json", {"key2": "value2"})
    writer.write("./data/memory.json", {"key3": "value3"})

    # 0.5秒后只会写入一次，内容为合并后的数据

    # 强制立即写入
    writer.flush_all()
    ```
    """

    def __init__(self, config: BatchedWriterConfig | None = None) -> None:
        """
        初始化批量写入器

        Args:
            config: 配置
        """
        self._config = config or BatchedWriterConfig()

        # 缓冲区
        self._buffer: dict[str, dict[str, Any]] = defaultdict(dict)
        self._pending_count: dict[str, int] = defaultdict(int)

        # 定时器
        self._timers: dict[str, threading.Timer] = {}

        # 锁
        self._lock = threading.Lock()

        # 统计
        self._stats = BatchedWriterStats()

    # -----------------------------------------------------------------------
    # 写入接口
    # -----------------------------------------------------------------------

    def write(self, file_path: str, data: dict[str, Any]) -> None:
        """
        写入数据（合并到缓冲区）

        Args:
            file_path: 目标文件路径
            data: 要写入的数据
        """
        with self._lock:
            # 更新统计
            if self._config.track_stats:
                self._stats.total_requests += 1

            # 合并数据
            if self._config.deep_merge:
                self._deep_merge(self._buffer[file_path], data)
            else:
                self._buffer[file_path].update(data)

            self._pending_count[file_path] += 1

            if self._config.track_stats:
                self._stats.merged_requests += 1
                self._stats.current_pending = sum(self._pending_count.values())

            # 检查是否达到批次上限
            if self._pending_count[file_path] >= self._config.max_batch_size:
                self._flush_unlocked(file_path)
                return

            # 设置延迟定时器
            if file_path not in self._timers:
                timer = threading.Timer(
                    self._config.delay_seconds,
                    self._flush,
                    args=[file_path]
                )
                timer.daemon = True
                timer.start()
                self._timers[file_path] = timer

    def flush(self, file_path: str) -> None:
        """将指定文件的缓冲区写入"""
        with self._lock:
            self._flush_unlocked(file_path)

    def flush_all(self) -> None:
        """强制写入所有缓冲数据"""
        with self._lock:
            file_paths = list(self._buffer.keys())
        for fp in file_paths:
            self._flush(fp)

    def get_pending_count(self, file_path: str | None = None) -> int:
        """
        获取待写入请求数

        Args:
            file_path: 文件路径，None 表示所有文件

        Returns:
            待写入请求数
        """
        with self._lock:
            if file_path:
                return self._pending_count.get(file_path, 0)
            return sum(self._pending_count.values())

    def get_stats(self) -> BatchedWriterStats:
        """获取统计信息"""
        with self._lock:
            self._stats.current_pending = sum(self._pending_count.values())
        return self._stats

    # -----------------------------------------------------------------------
    # 内部方法
    # -----------------------------------------------------------------------

    def _flush_unlocked(self, file_path: str) -> None:
        """将缓冲区写入文件（不加锁版本）"""
        if file_path not in self._buffer:
            return

        data = self._buffer.pop(file_path, {})
        self._pending_count.pop(file_path, 0)

        # 取消定时器
        timer = self._timers.pop(file_path, None)
        if timer:
            timer.cancel()

        # 执行写入（不加锁）
        self._do_write(file_path, data)

    def _flush(self, file_path: str) -> None:
        """将缓冲区写入文件（加锁版本）"""
        with self._lock:
            self._flush_unlocked(file_path)

    def _do_write(self, file_path: str, data: dict[str, Any]) -> bool:
        """执行实际写入"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            if self._config.track_stats:
                self._stats.actual_writes += 1

            return True

        except Exception as e:
            if self._config.track_stats:
                self._stats.failed_writes += 1
            print(f"BatchedWriter write error: {e}")
            return False

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """
        深度合并字典

        Args:
            target: 目标字典（会被修改）
            source: 源字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value


# ============================================================================
# 预配置实例
# ============================================================================

# 长期记忆写入器（延迟 0.5 秒）
_long_term_writer: BatchedWriter | None = None

# 状态同步写入器（延迟 1 秒）
_state_sync_writer: BatchedWriter | None = None


def get_long_term_writer() -> BatchedWriter:
    """获取长期记忆批量写入器"""
    global _long_term_writer
    if _long_term_writer is None:
        _long_term_writer = BatchedWriter(
            BatchedWriterConfig(
                delay_seconds=0.5,
                max_batch_size=20,
                deep_merge=True,
            )
        )
    return _long_term_writer


def get_state_sync_writer() -> BatchedWriter:
    """获取状态同步批量写入器"""
    global _state_sync_writer
    if _state_sync_writer is None:
        _state_sync_writer = BatchedWriter(
            BatchedWriterConfig(
                delay_seconds=1.0,
                max_batch_size=50,
                deep_merge=True,
            )
        )
    return _state_sync_writer

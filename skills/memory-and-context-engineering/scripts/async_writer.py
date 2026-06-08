"""
Agent Memory System - Async Writer（异步写入器）

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
异步写入器的核心目的是将阻塞的文件 I/O 操作转移到后台线程，
主线程立即返回，减少卡顿感。

核心特性：
1. 写入请求立即返回，不阻塞主线程
2. 后台线程批量合并写入
3. 支持写入完成回调
4. 优雅关闭保证数据持久化
"""

from __future__ import annotations

import json
import queue
import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field


# ============================================================================
# 数据模型
# ============================================================================


class WriteRequest(BaseModel):
    """写入请求"""

    request_id: str = Field(
        default_factory=lambda: f"write_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    file_path: str
    data: dict[str, Any] = Field(default_factory=dict)
    callback_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=0, ge=0, le=10, description="优先级，0最低")


class WriterStats(BaseModel):
    """写入器统计"""

    total_requests: int = Field(default=0)
    successful_writes: int = Field(default=0)
    failed_writes: int = Field(default=0)
    merged_writes: int = Field(default=0)
    total_write_time_ms: float = Field(default=0.0)
    queue_size: int = Field(default=0)
    buffer_size: int = Field(default=0)


class WriterConfig(BaseModel):
    """写入器配置"""

    # 批量处理
    batch_size: int = Field(default=10, ge=1, le=100, description="每批次最大请求数")
    batch_timeout: float = Field(default=1.0, ge=0.1, le=10.0, description="批次超时（秒）")

    # 队列配置
    max_queue_size: int = Field(default=1000, ge=100, le=10000, description="队列最大大小")

    # 合并策略
    enable_merge: bool = Field(default=True, description="是否启用写入合并")
    merge_same_file: bool = Field(default=True, description="是否合并同一文件的写入")

    # 重试配置
    retry_count: int = Field(default=3, ge=0, le=10, description="重试次数")
    retry_delay: float = Field(default=0.5, ge=0.1, le=5.0, description="重试延迟（秒）")

    # 优雅关闭
    shutdown_timeout: float = Field(default=5.0, ge=1.0, le=30.0, description="关闭超时（秒）")


# ============================================================================
# Async Writer
# ============================================================================


class AsyncWriter:
    """
    异步写入器

    特性：
    - 写入请求立即返回，不阻塞主线程
    - 后台线程批量合并写入
    - 支持写入完成回调
    - 优雅关闭保证数据持久化

    使用示例：
    ```python
    from scripts.async_writer import get_async_writer

    # 获取全局实例
    writer = get_async_writer()

    # 提交写入请求（非阻塞）
    writer.write(
        file_path="./data/memory.json",
        data={"key": "value"},
        callback_id="my_callback",
    )

    # 注册回调
    writer.register_callback("my_callback", lambda rid, success, err: print(f"Done: {success}"))

    # 关闭时确保数据写入
    writer.stop()
    ```
    """

    def __init__(self, config: WriterConfig | None = None) -> None:
        """
        初始化异步写入器

        Args:
            config: 写入器配置
        """
        self._config = config or WriterConfig()
        self._queue: queue.Queue[WriteRequest | None] = queue.Queue(
            maxsize=self._config.max_queue_size
        )
        self._running = False
        self._worker: threading.Thread | None = None
        self._callbacks: dict[str, Callable[[str, bool, str | None], None]] = {}
        self._stats = WriterStats()

        # 合并缓冲区
        self._buffer: dict[str, dict[str, Any]] = defaultdict(dict)
        self._buffer_meta: dict[str, dict[str, Any]] = defaultdict(dict)

        # 锁
        self._buffer_lock = threading.Lock()

    # -----------------------------------------------------------------------
    # 生命周期管理
    # -----------------------------------------------------------------------

    def start(self) -> None:
        """启动后台写入线程"""
        if self._running:
            return
        self._running = True
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def stop(self, timeout: float | None = None) -> None:
        """
        停止后台线程，确保所有数据写入

        Args:
            timeout: 超时时间，默认使用配置值
        """
        self._running = False
        if self._worker:
            # 放入结束信号
            self._queue.put(None)
            self._worker.join(timeout=timeout or self._config.shutdown_timeout)

            # 强制写入缓冲区剩余数据
            self._flush_buffer()

    def is_running(self) -> bool:
        """检查是否运行中"""
        return self._running and (self._worker is not None and self._worker.is_alive())

    # -----------------------------------------------------------------------
    # 写入接口
    # -----------------------------------------------------------------------

    def write(
        self,
        file_path: str,
        data: dict[str, Any],
        callback_id: str | None = None,
        priority: int = 0,
    ) -> str:
        """
        提交写入请求（非阻塞）

        Args:
            file_path: 目标文件路径
            data: 要写入的数据
            callback_id: 可选的回调标识
            priority: 优先级（0最低，10最高）

        Returns:
            请求ID
        """
        request = WriteRequest(
            file_path=file_path,
            data=data,
            callback_id=callback_id,
            priority=priority,
        )

        try:
            self._queue.put(request, timeout=0.1)
            self._stats.total_requests += 1
            self._stats.queue_size = self._queue.qsize()
        except queue.Full:
            # 队列满，直接同步写入
            self._sync_write(request)

        return request.request_id

    def write_sync(self, file_path: str, data: dict[str, Any]) -> bool:
        """
        同步写入（阻塞，用于关键数据）

        Args:
            file_path: 目标文件路径
            data: 要写入的数据

        Returns:
            是否成功
        """
        request = WriteRequest(file_path=file_path, data=data)
        return self._sync_write(request)

    def register_callback(
        self,
        callback_id: str,
        callback: Callable[[str, bool, str | None], None],
    ) -> None:
        """
        注册写入完成回调

        Args:
            callback_id: 回调标识
            callback: 回调函数 (request_id, success, error_message)
        """
        self._callbacks[callback_id] = callback

    def unregister_callback(self, callback_id: str) -> None:
        """注销回调"""
        self._callbacks.pop(callback_id, None)

    def flush(self) -> None:
        """强制写入所有缓冲数据"""
        self._flush_buffer()

    # -----------------------------------------------------------------------
    # 状态查询
    # -----------------------------------------------------------------------

    def get_stats(self) -> WriterStats:
        """获取统计信息"""
        with self._buffer_lock:
            self._stats.buffer_size = len(self._buffer)
        self._stats.queue_size = self._queue.qsize()
        return self._stats

    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self._queue.qsize()

    # -----------------------------------------------------------------------
    # 内部方法
    # -----------------------------------------------------------------------

    def _worker_loop(self) -> None:
        """后台工作线程"""
        while self._running:
            try:
                # 批量获取任务
                batch: list[WriteRequest] = []

                # 阻塞等待第一个任务
                try:
                    item = self._queue.get(timeout=self._config.batch_timeout)
                    if item is None:
                        break
                    batch.append(item)
                except queue.Empty:
                    # 超时，检查缓冲区
                    if self._buffer:
                        self._flush_buffer()
                    continue

                # 尝试获取更多任务（非阻塞）
                while len(batch) < self._config.batch_size:
                    try:
                        item = self._queue.get_nowait()
                        if item:
                            batch.append(item)
                    except queue.Empty:
                        break

                # 处理批次
                self._process_batch(batch)

            except Exception as e:
                self._stats.failed_writes += 1
                print(f"AsyncWriter worker error: {e}")

    def _process_batch(self, batch: list[WriteRequest]) -> None:
        """处理批次"""
        if not batch:
            return

        with self._buffer_lock:
            for request in batch:
                file_path = request.file_path

                if self._config.merge_same_file:
                    # 合并同一文件的写入
                    self._buffer[file_path].update(request.data)
                    self._buffer_meta[file_path] = {
                        "request_id": request.request_id,
                        "callback_id": request.callback_id,
                        "priority": request.priority,
                    }
                    self._stats.merged_writes += 1
                else:
                    # 不合并，直接写入
                    self._sync_write(request)

            # 执行写入
            if self._buffer:
                self._flush_buffer_unlocked()

    def _flush_buffer(self) -> None:
        """将缓冲区写入文件"""
        with self._buffer_lock:
            self._flush_buffer_unlocked()

    def _flush_buffer_unlocked(self) -> None:
        """将缓冲区写入文件（不加锁版本）"""
        for file_path, data in list(self._buffer.items()):
            meta = self._buffer_meta.get(file_path, {})
            request_id = meta.get("request_id", "")
            callback_id = meta.get("callback_id")

            success, error = self._do_write(file_path, data)

            if success:
                self._stats.successful_writes += 1
            else:
                self._stats.failed_writes += 1

            # 触发回调
            if callback_id and callback_id in self._callbacks:
                try:
                    self._callbacks[callback_id](request_id, success, error)
                except Exception as e:
                    print(f"Callback error: {e}")

            # 清理缓冲区
            del self._buffer[file_path]
            if file_path in self._buffer_meta:
                del self._buffer_meta[file_path]

    def _sync_write(self, request: WriteRequest) -> bool:
        """同步写入"""
        success, error = self._do_write(request.file_path, request.data)

        if success:
            self._stats.successful_writes += 1
        else:
            self._stats.failed_writes += 1

        # 触发回调
        if request.callback_id and request.callback_id in self._callbacks:
            try:
                self._callbacks[request.callback_id](request.request_id, success, error)
            except Exception as e:
                print(f"Callback error: {e}")

        return success

    def _do_write(self, file_path: str, data: dict[str, Any]) -> tuple[bool, str | None]:
        """
        执行实际写入

        Args:
            file_path: 文件路径
            data: 数据

        Returns:
            (success, error_message)
        """
        for attempt in range(self._config.retry_count + 1):
            try:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)

                start_time = datetime.now()

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                self._stats.total_write_time_ms += elapsed

                return True, None

            except Exception as e:
                if attempt < self._config.retry_count:
                    import time
                    time.sleep(self._config.retry_delay)
                else:
                    return False, str(e)

        return False, "Unknown error"


# ============================================================================
# 全局实例
# ============================================================================

_async_writer: AsyncWriter | None = None
_async_writer_lock = threading.Lock()


def get_async_writer(config: WriterConfig | None = None) -> AsyncWriter:
    """
    获取全局异步写入器

    Args:
        config: 配置（仅首次调用有效）

    Returns:
        AsyncWriter 实例
    """
    global _async_writer
    with _async_writer_lock:
        if _async_writer is None:
            _async_writer = AsyncWriter(config)
            _async_writer.start()
        return _async_writer


def shutdown_async_writer(timeout: float = 5.0) -> None:
    """
    关闭全局异步写入器

    Args:
        timeout: 超时时间
    """
    global _async_writer
    with _async_writer_lock:
        if _async_writer is not None:
            _async_writer.stop(timeout=timeout)
            _async_writer = None

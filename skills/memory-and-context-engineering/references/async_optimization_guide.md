# Agent Memory System 异步优化方案

## 概述

本文档分析 Agent Memory System 的性能瓶颈，提出异步化优化方案，减少卡顿感，提升系统流畅性。

---

## 一、性能瓶颈分析

### 1.1 主要阻塞点

| 操作 | 位置 | 调用频率 | 阻塞类型 | 影响程度 |
|------|------|----------|----------|----------|
| **长期记忆持久化** | `long_term.py::_save_to_storage()` | 12+ 次/会话 | 文件 I/O | 🔴 高 |
| **状态同步保存** | `incremental_sync.py::_save_state()` | 每次变更 | 文件 I/O | 🟡 中 |
| **检查点创建** | `state_capture.py::create_checkpoint()` | 每次状态变化 | 文件 I/O | 🟡 中 |
| **热度计算** | `heat_manager.py` | 每次访问 | CPU 计算 | 🟢 低 |
| **冲突检测** | `conflict_resolver.py` | 每次记忆更新 | CPU 计算 | 🟢 低 |

### 1.2 当前架构问题

```
用户请求 → 同步处理 → 同步写入 → 返回响应
           ↓          ↓
         阻塞等待    阻塞等待
```

**问题**：
1. 每次更新都触发同步文件写入
2. 写入操作串行执行，无法合并
3. 内存中数据与持久化数据强绑定
4. 无后台任务处理机制

---

## 二、异步优化方案

### 2.1 方案一：异步写入队列（推荐）

#### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        主线程                                │
├─────────────────────────────────────────────────────────────┤
│  API 调用 → 内存更新 → 写入请求入队 → 立即返回              │
│                           ↓                                 │
│                    写入队列 (Queue)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      后台写入线程                            │
├─────────────────────────────────────────────────────────────┤
│  从队列取任务 → 批量合并 → 写入文件 → 完成回调              │
└─────────────────────────────────────────────────────────────┘
```

#### 核心组件

```python
# scripts/async_writer.py

import threading
import queue
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Callable
from collections import defaultdict


class AsyncWriter:
    """
    异步写入器
    
    特性：
    - 写入请求立即返回，不阻塞主线程
    - 后台线程批量合并写入
    - 支持写入完成回调
    - 优雅关闭保证数据持久化
    """
    
    def __init__(
        self,
        batch_size: int = 10,
        batch_timeout: float = 1.0,
        max_queue_size: int = 1000,
    ):
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._batch_size = batch_size
        self._batch_timeout = batch_timeout
        self._running = False
        self._worker: threading.Thread | None = None
        self._callbacks: dict[str, Callable] = {}
        
        # 合并缓冲区
        self._buffer: dict[str, dict[str, Any]] = defaultdict(dict)
        
    def start(self) -> None:
        """启动后台写入线程"""
        if self._running:
            return
        self._running = True
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()
    
    def stop(self, timeout: float = 5.0) -> None:
        """停止后台线程，确保所有数据写入"""
        self._running = False
        if self._worker:
            # 放入结束信号
            self._queue.put(None)
            self._worker.join(timeout=timeout)
            # 强制写入缓冲区剩余数据
            self._flush_buffer()
    
    def write(
        self,
        file_path: str,
        data: dict[str, Any],
        callback_id: str | None = None,
    ) -> str:
        """
        提交写入请求（非阻塞）
        
        Args:
            file_path: 目标文件路径
            data: 要写入的数据
            callback_id: 可选的回调标识
            
        Returns:
            请求ID
        """
        request_id = f"write_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self._queue.put({
            "request_id": request_id,
            "file_path": file_path,
            "data": data,
            "callback_id": callback_id,
            "timestamp": datetime.now(),
        })
        return request_id
    
    def register_callback(self, callback_id: str, callback: Callable) -> None:
        """注册写入完成回调"""
        self._callbacks[callback_id] = callback
    
    def _worker_loop(self) -> None:
        """后台工作线程"""
        while self._running:
            try:
                # 批量获取任务
                batch = []
                try:
                    item = self._queue.get(timeout=self._batch_timeout)
                    if item is None:
                        break
                    batch.append(item)
                    
                    # 尝试获取更多任务（非阻塞）
                    while len(batch) < self._batch_size:
                        try:
                            item = self._queue.get_nowait()
                            if item:
                                batch.append(item)
                        except queue.Empty:
                            break
                            
                except queue.Empty:
                    continue
                
                # 合并同一文件的写入
                for item in batch:
                    file_path = item["file_path"]
                    self._buffer[file_path].update(item["data"])
                    self._buffer[file_path]["_last_request_id"] = item["request_id"]
                    self._buffer[file_path]["_callback_id"] = item.get("callback_id")
                
                # 执行写入
                self._flush_buffer()
                
            except Exception as e:
                # 记录错误，继续处理
                print(f"AsyncWriter error: {e}")
    
    def _flush_buffer(self) -> None:
        """将缓冲区写入文件"""
        for file_path, data in self._buffer.items():
            try:
                # 提取元数据
                request_id = data.pop("_last_request_id", None)
                callback_id = data.pop("_callback_id", None)
                
                # 写入文件
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
                # 触发回调
                if callback_id and callback_id in self._callbacks:
                    self._callbacks[callback_id](request_id, True, None)
                    
            except Exception as e:
                if callback_id and callback_id in self._callbacks:
                    self._callbacks[callback_id](request_id, False, str(e))
        
        self._buffer.clear()


# 全局实例
_async_writer: AsyncWriter | None = None


def get_async_writer() -> AsyncWriter:
    """获取全局异步写入器"""
    global _async_writer
    if _async_writer is None:
        _async_writer = AsyncWriter()
        _async_writer.start()
    return _async_writer
```

#### 使用方式

```python
# 修改 long_term.py

from .async_writer import get_async_writer

class LongTermMemoryManager:
    def _save_to_storage(self) -> None:
        """保存记忆到存储（异步版本）"""
        storage_file = self.storage_path / f"{self.user_id}_memory.json"
        self._container.last_updated = datetime.now()
        
        # 异步写入（非阻塞）
        writer = get_async_writer()
        writer.write(
            file_path=str(storage_file),
            data=self._container.model_dump(mode="json"),
            callback_id=f"ltm_{self.user_id}",
        )
        # 立即返回，不阻塞
```

---

### 2.2 方案二：写入合并与延迟写入

#### 设计思路

```
写入请求 → 内存缓冲区 → 延迟计时器 → 批量写入
    ↓           ↑
 立即返回    可追加更新
```

#### 核心组件

```python
# scripts/batched_writer.py

import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from collections import defaultdict


class BatchedWriter:
    """
    批量写入器
    
    特性：
    - 相同文件的多次写入自动合并
    - 延迟写入，减少 I/O 次数
    - 可配置延迟时间和最大批次
    """
    
    def __init__(
        self,
        delay_seconds: float = 0.5,
        max_batch_size: int = 50,
    ):
        self._delay_seconds = delay_seconds
        self._max_batch_size = max_batch_size
        
        # 缓冲区
        self._buffer: dict[str, dict[str, Any]] = defaultdict(dict)
        self._pending_count: dict[str, int] = defaultdict(int)
        
        # 定时器
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()
    
    def write(self, file_path: str, data: dict[str, Any]) -> None:
        """
        写入数据（合并到缓冲区）
        
        Args:
            file_path: 目标文件路径
            data: 要写入的数据
        """
        with self._lock:
            # 合并数据
            self._buffer[file_path].update(data)
            self._pending_count[file_path] += 1
            
            # 检查是否达到批次上限
            if self._pending_count[file_path] >= self._max_batch_size:
                self._flush(file_path)
                return
            
            # 设置延迟定时器
            if file_path not in self._timers:
                timer = threading.Timer(
                    self._delay_seconds,
                    self._flush,
                    args=[file_path]
                )
                timer.daemon = True
                timer.start()
                self._timers[file_path] = timer
    
    def _flush(self, file_path: str) -> None:
        """将缓冲区写入文件"""
        with self._lock:
            if file_path not in self._buffer:
                return
            
            data = self._buffer.pop(file_path, {})
            self._pending_count.pop(file_path, 0)
            
            # 取消定时器
            timer = self._timers.pop(file_path, None)
            if timer:
                timer.cancel()
        
        # 执行写入（不加锁）
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"BatchedWriter flush error: {e}")
    
    def flush_all(self) -> None:
        """强制写入所有缓冲数据"""
        with self._lock:
            file_paths = list(self._buffer.keys())
        for fp in file_paths:
            self._flush(fp)
```

---

### 2.3 方案三：分层缓存架构

#### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      访问层                                  │
├─────────────────────────────────────────────────────────────┤
│  get() → L1缓存(内存) → L2缓存(Redis) → 持久化(文件)       │
│  set() → L1缓存(内存) → 异步写入队列 → 持久化(文件)        │
└─────────────────────────────────────────────────────────────┘

数据分层：
┌─────────────────────────────────────────────────────────────┐
│ L1 缓存（内存）- 热数据                                      │
│   • 当前会话数据                                             │
│   • 最近访问的记忆                                           │
│   • TTL: 5分钟                                               │
├─────────────────────────────────────────────────────────────┤
│ L2 缓存（Redis）- 温数据                                     │
│   • 用户画像                                                 │
│   • 近期记忆                                                 │
│   • TTL: 24小时                                              │
├─────────────────────────────────────────────────────────────┤
│ 持久化（文件）- 冷数据                                       │
│   • 全量长期记忆                                             │
│   • 历史会话                                                 │
│   • 永久存储                                                 │
└─────────────────────────────────────────────────────────────┘
```

#### 核心组件

```python
# scripts/layered_cache.py

from datetime import datetime
from typing import Any, Optional
from collections import OrderedDict


class LayeredCache:
    """
    分层缓存
    
    L1: 内存缓存（LRU）
    L2: Redis 缓存
    L3: 文件持久化
    """
    
    def __init__(
        self,
        l1_size: int = 100,
        l1_ttl_seconds: int = 300,  # 5分钟
        l2_ttl_seconds: int = 86400,  # 24小时
    ):
        self._l1_size = l1_size
        self._l1_ttl = l1_ttl_seconds
        self._l2_ttl = l2_ttl_seconds
        
        # L1 缓存（LRU）
        self._l1_cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        
        # L2 Redis（可选）
        self._redis = None  # 延迟初始化
        
        # L3 持久化处理器
        self._persistence: Any = None  # 由调用方设置
    
    def get(self, key: str) -> Optional[Any]:
        """获取数据（优先从高速缓存）"""
        # L1 检查
        if key in self._l1_cache:
            value, expire_at = self._l1_cache[key]
            if datetime.now().timestamp() < expire_at:
                # 命中，移到队尾
                self._l1_cache.move_to_end(key)
                return value
            else:
                # 过期，删除
                del self._l1_cache[key]
        
        # L2 检查
        if self._redis:
            value = self._redis.get(key)
            if value:
                # 回填 L1
                self._set_l1(key, value)
                return value
        
        # L3 检查
        if self._persistence:
            value = self._persistence.load(key)
            if value:
                # 回填 L1, L2
                self._set_l1(key, value)
                if self._redis:
                    self._redis.setex(key, self._l2_ttl, value)
                return value
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """设置数据（写入所有层）"""
        # L1 写入
        self._set_l1(key, value)
        
        # L2 异步写入
        if self._redis:
            self._redis.setex(key, self._l2_ttl, value)
        
        # L3 异步写入
        if self._persistence:
            self._persistence.save_async(key, value)
    
    def _set_l1(self, key: str, value: Any) -> None:
        """设置 L1 缓存"""
        expire_at = datetime.now().timestamp() + self._l1_ttl
        
        # LRU 淘汰
        while len(self._l1_cache) >= self._l1_size:
            self._l1_cache.popitem(last=False)
        
        self._l1_cache[key] = (value, expire_at)
```

---

## 三、其他优化技巧

### 3.1 预加载优化

```python
# 智能预加载：根据访问模式预测下一步需要的数据

class PredictivePreloader:
    """预测性预加载器"""
    
    def __init__(self):
        self._access_patterns: dict[str, list[str]] = {}
        self._preload_queue: queue.Queue = queue.Queue()
    
    def record_access(self, current_key: str, next_keys: list[str]) -> None:
        """记录访问模式"""
        if current_key not in self._access_patterns:
            self._access_patterns[current_key] = []
        self._access_patterns[current_key].extend(next_keys)
    
    def predict_next(self, current_key: str) -> list[str]:
        """预测下一步需要的数据"""
        return self._access_patterns.get(current_key, [])
    
    def preload(self, keys: list[str]) -> None:
        """后台预加载"""
        for key in keys:
            self._preload_queue.put(key)
```

### 3.2 写入合并策略

```python
# 策略配置
WRITE_MERGE_CONFIG = {
    # 长期记忆：延迟 0.5 秒合并
    "long_term": {
        "delay_seconds": 0.5,
        "max_batch": 20,
    },
    # 状态同步：延迟 1 秒合并
    "state_sync": {
        "delay_seconds": 1.0,
        "max_batch": 50,
    },
    # 检查点：立即写入（不合并）
    "checkpoint": {
        "delay_seconds": 0,
        "max_batch": 1,
    },
}
```

### 3.3 内存池优化

```python
# 对象池：减少内存分配开销

from queue import Queue
from typing import TypeVar, Generic

T = TypeVar("T")


class ObjectPool(Generic[T]):
    """对象池"""
    
    def __init__(self, factory: callable, max_size: int = 100):
        self._pool: Queue = Queue(maxsize=max_size)
        self._factory = factory
    
    def acquire(self) -> T:
        """获取对象"""
        try:
            return self._pool.get_nowait()
        except:
            return self._factory()
    
    def release(self, obj: T) -> None:
        """释放对象"""
        try:
            self._pool.put_nowait(obj)
        except:
            pass  # 池满，丢弃
```

### 3.4 懒计算优化

```python
# 延迟计算：只在需要时才计算

class LazyEvaluator:
    """懒计算器"""
    
    def __init__(self):
        self._cache: dict[str, Any] = {}
        self._computing: set[str] = set()
    
    def get_or_compute(self, key: str, compute_fn: callable) -> Any:
        """获取或计算"""
        if key in self._cache:
            return self._cache[key]
        
        if key in self._computing:
            # 正在计算，返回默认值
            return None
        
        self._computing.add(key)
        try:
            result = compute_fn()
            self._cache[key] = result
            return result
        finally:
            self._computing.discard(key)
```

---

## 四、实施优先级

### 4.1 高优先级（立即实施）

| 优化项 | 影响 | 实施难度 | 预期收益 |
|--------|------|----------|----------|
| 异步写入队列 | 🔴 高 | 中 | 减少 80% I/O 阻塞 |
| 写入合并 | 🔴 高 | 低 | 减少 50% 写入次数 |

### 4.2 中优先级（短期实施）

| 优化项 | 影响 | 实施难度 | 预期收益 |
|--------|------|----------|----------|
| L1 内存缓存 | 🟡 中 | 中 | 减少 60% L2/L3 访问 |
| 预加载优化 | 🟡 中 | 中 | 减少 30% 等待时间 |

### 4.3 低优先级（长期实施）

| 优化项 | 影响 | 实施难度 | 预期收益 |
|--------|------|----------|----------|
| 对象池 | 🟢 低 | 低 | 减少内存碎片 |
| 懒计算 | 🟢 低 | 低 | 减少不必要的计算 |

---

## 五、实施路线图

```
Phase 1: 异步写入基础（1-2天）
├── 实现 AsyncWriter 类
├── 修改 LongTermMemoryManager
└── 添加优雅关闭机制

Phase 2: 写入合并（1天）
├── 实现 BatchedWriter 类
├── 配置各模块合并策略
└── 测试合并效果

Phase 3: 缓存层（2-3天）
├── 实现 LayeredCache 类
├── 集成到核心模块
└── 缓存一致性保证

Phase 4: 高级优化（可选）
├── 预加载机制
├── 对象池
└── 性能监控
```

---

## 六、注意事项

### 6.1 数据一致性

- 异步写入可能导致短暂的数据不一致
- 关键操作（如用户确认）应强制同步写入
- 提供显式的 `flush()` 接口

### 6.2 错误处理

- 后台线程异常不应影响主流程
- 写入失败应有重试机制
- 提供错误回调通知

### 6.3 资源管理

- 限制队列大小，防止内存溢出
- 定期清理过期缓存
- 监控后台线程状态

---

## 七、总结

通过实施异步写入队列和写入合并，可以将 I/O 阻塞减少 **80% 以上**，显著提升系统流畅性。

**推荐实施顺序**：
1. **AsyncWriter** - 核心异步写入
2. **BatchedWriter** - 写入合并
3. **LayeredCache** - 分层缓存（可选）

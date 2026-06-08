"""
Agent Memory System - 增量同步模块

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

设计说明：
增量同步的核心目的是避免重复读取已提炼进入长期记忆的内容。
每个短期记忆项都有一个同步状态，标记是否已被提炼。
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class SyncStatus(str, Enum):
    """同步状态"""

    PENDING = "pending"  # 待提炼
    EXTRACTING = "extracting"  # 提炼中
    EXTRACTED = "extracted"  # 已提炼
    SKIPPED = "skipped"  # 已跳过（不需要提炼）
    FAILED = "failed"  # 提炼失败


# ============================================================================
# 数据模型
# ============================================================================


class ExtractionRecord(BaseModel):
    """提炼记录"""

    memory_id: str
    target_category: str  # 提炼到的长期记忆类型
    extracted_at: datetime = Field(default_factory=datetime.now)
    extraction_quality: float = 0.8  # 提炼质量评估
    notes: str = ""


class SyncState(BaseModel):
    """同步状态"""

    memory_id: str
    status: SyncStatus = SyncStatus.PENDING
    extraction_history: list[ExtractionRecord] = Field(default_factory=list)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    priority: float = 0.5  # 提炼优先级
    retry_count: int = 0  # 重试次数
    error_message: str = ""


class SyncStats(BaseModel):
    """同步统计"""

    total_memories: int = 0
    pending_count: int = 0
    extracted_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    last_sync: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 增量同步器
# ============================================================================


class IncrementalSync:
    """
    增量同步器

    追踪短期记忆的提炼状态，避免重复读取已提炼内容
    """

    def __init__(
        self,
        storage_path: str,
    ) -> None:
        """
        初始化增量同步器

        Args:
            storage_path: 同步状态存储路径（由调用方指定，无默认值）
        """
        self.storage_path: Path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 同步状态缓存
        self._sync_states: dict[str, SyncState] = {}

        # 统计
        self._stats: SyncStats = SyncStats()

        # 加载已有状态
        self._load_state()

    def _load_state(self) -> None:
        """加载已有状态"""
        state_file: Path = self.storage_path / "sync_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            for mem_id, state_data in data.get("sync_states", {}).items():
                self._sync_states[mem_id] = SyncState.model_validate(state_data)

            # 更新统计
            self._update_stats()

        except (json.JSONDecodeError, ValueError):
            pass

    def _save_state(self) -> None:
        """保存状态"""
        state_file: Path = self.storage_path / "sync_state.json"

        data: dict[str, Any] = {
            "sync_states": {
                k: v.model_dump(mode="json") for k, v in self._sync_states.items()
            },
            "stats": self._stats.model_dump(mode="json"),
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _update_stats(self) -> None:
        """更新统计"""
        self._stats.total_memories = len(self._sync_states)
        self._stats.pending_count = sum(
            1 for s in self._sync_states.values()
            if s.status == SyncStatus.PENDING
        )
        self._stats.extracted_count = sum(
            1 for s in self._sync_states.values()
            if s.status == SyncStatus.EXTRACTED
        )
        self._stats.skipped_count = sum(
            1 for s in self._sync_states.values()
            if s.status == SyncStatus.SKIPPED
        )
        self._stats.failed_count = sum(
            1 for s in self._sync_states.values()
            if s.status == SyncStatus.FAILED
        )
        self._stats.last_sync = datetime.now()

    def register(
        self,
        memory_id: str,
        priority: float = 0.5,
    ) -> None:
        """
        注册新的短期记忆

        Args:
            memory_id: 记忆ID
            priority: 提炼优先级
        """
        if memory_id not in self._sync_states:
            self._sync_states[memory_id] = SyncState(
                memory_id=memory_id,
                status=SyncStatus.PENDING,
                priority=priority,
            )
        else:
            # 更新访问
            self._sync_states[memory_id].last_accessed = datetime.now()
            self._sync_states[memory_id].access_count += 1

        self._update_stats()
        self._save_state()

    def mark_extracting(self, memory_id: str) -> bool:
        """
        标记为提炼中

        Args:
            memory_id: 记忆ID

        Returns:
            是否成功
        """
        if memory_id not in self._sync_states:
            return False

        state: SyncState = self._sync_states[memory_id]
        if state.status != SyncStatus.PENDING:
            return False

        state.status = SyncStatus.EXTRACTING
        self._save_state()
        return True

    def mark_extracted(
        self,
        memory_id: str,
        target_category: str,
        quality: float = 0.8,
        notes: str = "",
    ) -> bool:
        """
        标记为已提炼

        Args:
            memory_id: 记忆ID
            target_category: 目标长期记忆类型
            quality: 提炼质量
            notes: 备注

        Returns:
            是否成功
        """
        if memory_id not in self._sync_states:
            return False

        state_ext: SyncState = self._sync_states[memory_id]

        # 添加提炼记录
        record: ExtractionRecord = ExtractionRecord(
            memory_id=memory_id,
            target_category=target_category,
            extraction_quality=quality,
            notes=notes,
        )
        state_ext.extraction_history.append(record)

        # 更新状态
        state_ext.status = SyncStatus.EXTRACTED
        state_ext.last_accessed = datetime.now()

        self._update_stats()
        self._save_state()
        return True

    def mark_skipped(
        self,
        memory_id: str,
        reason: str = "",
    ) -> bool:
        """
        标记为已跳过

        Args:
            memory_id: 记忆ID
            reason: 跳过原因

        Returns:
            是否成功
        """
        if memory_id not in self._sync_states:
            return False

        state_skip: SyncState = self._sync_states[memory_id]
        state_skip.status = SyncStatus.SKIPPED
        state_skip.error_message = reason

        self._update_stats()
        self._save_state()
        return True

    def mark_failed(
        self,
        memory_id: str,
        error: str = "",
    ) -> bool:
        """
        标记为提炼失败

        Args:
            memory_id: 记忆ID
            error: 错误信息

        Returns:
            是否成功
        """
        if memory_id not in self._sync_states:
            return False

        state_fail: SyncState = self._sync_states[memory_id]
        state_fail.status = SyncStatus.FAILED
        state_fail.error_message = error
        state_fail.retry_count += 1

        self._update_stats()
        self._save_state()
        return True

    def reset_for_retry(self, memory_id: str) -> bool:
        """
        重置为待提炼（用于重试）

        Args:
            memory_id: 记忆ID

        Returns:
            是否成功
        """
        if memory_id not in self._sync_states:
            return False

        state_retry: SyncState = self._sync_states[memory_id]
        if state_retry.status not in [SyncStatus.FAILED, SyncStatus.EXTRACTING]:
            return False

        state_retry.status = SyncStatus.PENDING
        state_retry.error_message = ""

        self._update_stats()
        self._save_state()
        return True

    def should_skip(self, memory_id: str) -> bool:
        """
        是否应该跳过（已提炼或已跳过）

        Args:
            memory_id: 记忆ID

        Returns:
            是否跳过
        """
        state_should: SyncState | None = self._sync_states.get(memory_id)
        if state_should is None:
            return False

        return state_should.status in [
            SyncStatus.EXTRACTED,
            SyncStatus.SKIPPED,
        ]

    def is_pending(self, memory_id: str) -> bool:
        """
        是否待提炼

        Args:
            memory_id: 记忆ID

        Returns:
            是否待提炼
        """
        state_pending: SyncState | None = self._sync_states.get(memory_id)
        return state_pending is not None and state_pending.status == SyncStatus.PENDING

    def get_unextracted(self, limit: int = 100) -> list[str]:
        """
        获取未提炼的记忆ID列表

        按优先级和访问时间排序

        Args:
            limit: 返回数量限制

        Returns:
            记忆ID列表
        """
        pending: list[tuple[str, SyncState]] = [
            (mem_id, state)
            for mem_id, state in self._sync_states.items()
            if state.status == SyncStatus.PENDING
        ]

        # 按优先级降序、访问时间升序排序
        pending.sort(key=lambda x: (-x[1].priority, x[1].last_accessed))

        return [mem_id for mem_id, _ in pending[:limit]]

    def get_extracted(self) -> list[str]:
        """
        获取已提炼的记忆ID列表

        Returns:
            记忆ID列表
        """
        return [
            mem_id
            for mem_id, state in self._sync_states.items()
            if state.status == SyncStatus.EXTRACTED
        ]

    def get_failed(self, max_retry: int = 3) -> list[str]:
        """
        获取失败但可重试的记忆ID列表

        Args:
            max_retry: 最大重试次数

        Returns:
            记忆ID列表
        """
        return [
            mem_id
            for mem_id, state in self._sync_states.items()
            if state.status == SyncStatus.FAILED and state.retry_count < max_retry
        ]

    def get_extraction_history(self, memory_id: str) -> list[ExtractionRecord]:
        """
        获取提炼历史

        Args:
            memory_id: 记忆ID

        Returns:
            提炼记录列表
        """
        state_hist: SyncState | None = self._sync_states.get(memory_id)
        return state_hist.extraction_history if state_hist else []

    def get_state(self, memory_id: str) -> Optional[SyncState]:
        """
        获取同步状态

        Args:
            memory_id: 记忆ID

        Returns:
            同步状态
        """
        return self._sync_states.get(memory_id)

    def get_stats(self) -> SyncStats:
        """
        获取同步统计

        Returns:
            同步统计
        """
        return self._stats

    def set_priority(self, memory_id: str, priority: float) -> bool:
        """
        设置提炼优先级

        Args:
            memory_id: 记忆ID
            priority: 优先级 (0.0 - 1.0)

        Returns:
            是否成功
        """
        if memory_id not in self._sync_states:
            return False

        self._sync_states[memory_id].priority = max(0.0, min(1.0, priority))
        self._save_state()
        return True

    def remove(self, memory_id: str) -> bool:
        """
        移除同步状态

        Args:
            memory_id: 记忆ID

        Returns:
            是否成功
        """
        if memory_id not in self._sync_states:
            return False

        del self._sync_states[memory_id]
        self._update_stats()
        self._save_state()
        return True

    def clear(self) -> None:
        """
        清空所有状态
        """
        self._sync_states.clear()
        self._stats = SyncStats()
        self._save_state()

    def get_pending_count(self) -> int:
        """
        获取待提炼数量

        Returns:
            待提炼数量
        """
        return self._stats.pending_count

    def get_extraction_progress(self) -> float:
        """
        获取提炼进度

        Returns:
            进度百分比 (0.0 - 1.0)
        """
        if self._stats.total_memories == 0:
            return 1.0

        processed: int = self._stats.extracted_count + self._stats.skipped_count
        return processed / self._stats.total_memories


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "SyncStatus",
    "SyncState",
    "ExtractionRecord",
    "SyncStats",
    "IncrementalSync",
]

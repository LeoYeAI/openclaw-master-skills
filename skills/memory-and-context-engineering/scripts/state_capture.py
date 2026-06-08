"""
Agent Memory System - 全局状态捕捉器（LangGraph集成版）

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

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from .types import (
    CheckpointRecord,
    StateChangeEvent,
    StateEventType,
    StateSubscription,
    PhaseType,
    ScenarioType,
    UserStateType,
)


# ============================================================================
# 状态归约器
# ============================================================================


class StateReducer:
    """
    状态归约器

    负责：
    - 计算状态差异（增量更新）
    - 应用差异恢复状态
    - 状态哈希计算
    """

    @staticmethod
    def compute_hash(state: dict[str, Any]) -> str:
        """
        计算状态哈希

        Args:
            state: 状态字典

        Returns:
            状态哈希值
        """
        state_str: str = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]

    @staticmethod
    def compute_diff(
        previous: dict[str, Any],
        current: dict[str, Any],
    ) -> dict[str, Any]:
        """
        计算两个状态之间的差异

        Args:
            previous: 前一个状态
            current: 当前状态

        Returns:
            差异字典，包含 added、modified、removed
        """
        diff: dict[str, Any] = {
            "added": {},
            "modified": {},
            "removed": [],
        }

        # 所有键
        all_keys: set[str] = set(previous.keys()) | set(current.keys())

        for key in all_keys:
            if key not in previous:
                # 新增的键
                diff["added"][key] = current[key]
            elif key not in current:
                # 删除的键
                diff["removed"].append(key)
            elif previous[key] != current[key]:
                # 修改的键
                diff["modified"][key] = {
                    "old": previous[key],
                    "new": current[key],
                }

        return diff

    @staticmethod
    def apply_diff(
        base: dict[str, Any],
        diff: dict[str, Any],
    ) -> dict[str, Any]:
        """
        应用差异恢复状态

        Args:
            base: 基础状态
            diff: 差异字典

        Returns:
            恢复后的状态
        """
        result: dict[str, Any] = dict(base)

        # 应用新增
        for key, value in diff.get("added", {}).items():
            result[key] = value

        # 应用修改
        for key, changes in diff.get("modified", {}).items():
            result[key] = changes["new"]

        # 应用删除
        for key in diff.get("removed", []):
            result.pop(key, None)

        return result


# ============================================================================
# 事件总线
# ============================================================================


class StateEventBus:
    """
    状态事件总线

    负责：
    - 事件发布/订阅
    - 回调管理
    - 事件分发
    """

    def __init__(self) -> None:
        """初始化事件总线"""
        self._subscriptions: dict[str, StateSubscription] = {}
        self._callbacks: dict[str, Callable[[StateChangeEvent], None]] = {}

    def subscribe(
        self,
        event_types: list[StateEventType],
        callback: Callable[[StateChangeEvent], None],
        subscription_id: str | None = None,
    ) -> str:
        """
        订阅状态事件

        Args:
            event_types: 订阅的事件类型列表
            callback: 回调函数
            subscription_id: 订阅ID（可选）

        Returns:
            订阅ID
        """
        sub_id: str = subscription_id or f"sub_{uuid.uuid4().hex[:8]}"

        subscription: StateSubscription = StateSubscription(
            subscription_id=sub_id,
            event_types=event_types,
            callback_name=callback.__name__,
        )

        self._subscriptions[sub_id] = subscription
        self._callbacks[sub_id] = callback

        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        取消订阅

        Args:
            subscription_id: 订阅ID

        Returns:
            是否成功取消
        """
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            del self._callbacks[subscription_id]
            return True
        return False

    def emit(self, event: StateChangeEvent) -> int:
        """
        发布事件

        Args:
            event: 状态变化事件

        Returns:
            触发的回调数量
        """
        triggered: int = 0

        for sub_id, subscription in self._subscriptions.items():
            if not subscription.active:
                continue

            if event.event_type in subscription.event_types:
                callback: Callable[[StateChangeEvent], None] | None = self._callbacks.get(sub_id)
                if callback:
                    try:
                        callback(event)
                        triggered += 1
                    except Exception:
                        # 回调执行失败，记录但不中断
                        pass

        return triggered

    def get_subscriptions(self) -> list[dict[str, Any]]:
        """
        获取所有订阅

        Returns:
            订阅列表
        """
        return [
            {
                "subscription_id": sub.subscription_id,
                "event_types": [et.value for et in sub.event_types],
                "callback_name": sub.callback_name,
                "active": sub.active,
            }
            for sub in self._subscriptions.values()
        ]


# ============================================================================
# 检查点管理器
# ============================================================================


class CheckpointManager:
    """
    检查点管理器

    负责：
    - 创建和存储检查点
    - 恢复检查点
    - 列出和管理检查点
    - 过期检查点清理
    """

    def __init__(
        self,
        storage_path: str,
        default_ttl_hours: int = 168,
    ) -> None:
        """
        初始化检查点管理器

        Args:
            storage_path: 存储路径
            default_ttl_hours: 默认TTL（小时）
        """
        self.storage_path: Path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.default_ttl_hours: int = default_ttl_hours
        self._reducer: StateReducer = StateReducer()

    def create(
        self,
        state: dict[str, Any],
        thread_id: str,
        node_name: str,
        previous_state: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CheckpointRecord:
        """
        创建检查点

        Args:
            state: 当前状态
            thread_id: 线程ID
            node_name: 节点名称
            previous_state: 前一个状态（用于计算差异）
            metadata: 元数据

        Returns:
            检查点记录
        """
        checkpoint_id: str = f"cp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        state_hash: str = self._reducer.compute_hash(state)

        # 计算差异
        state_diff: dict[str, Any] = {}
        if previous_state is not None:
            state_diff = self._reducer.compute_diff(previous_state, state)

        record: CheckpointRecord = CheckpointRecord(
            checkpoint_id=checkpoint_id,
            thread_id=thread_id,
            node_name=node_name,
            state_hash=state_hash,
            state_diff=state_diff,
            metadata=metadata or {},
            ttl_hours=self.default_ttl_hours,
        )

        # 存储检查点
        self._save_checkpoint(record, state)

        return record

    def restore(
        self,
        checkpoint_id: str,
    ) -> dict[str, Any] | None:
        """
        恢复检查点

        Args:
            checkpoint_id: 检查点ID

        Returns:
            恢复的状态，如果不存在则返回None
        """
        state_file: Path = self.storage_path / f"{checkpoint_id}_state.json"

        if not state_file.exists():
            return None

        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def list(
        self,
        thread_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        列出检查点

        Args:
            thread_id: 线程ID（可选）
            limit: 最大数量

        Returns:
            检查点列表
        """
        checkpoints: list[dict[str, Any]] = []

        for record_file in sorted(
            self.storage_path.glob("cp_*_record.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ):
            with open(record_file, "r", encoding="utf-8") as f:
                record: dict[str, Any] = json.load(f)

            if thread_id and record.get("thread_id") != thread_id:
                continue

            checkpoints.append(record)

            if len(checkpoints) >= limit:
                break

        return checkpoints

    def garbage_collect(
        self,
        ttl_hours: int | None = None,
    ) -> int:
        """
        清理过期检查点

        Args:
            ttl_hours: TTL（小时），不指定则使用记录中的TTL

        Returns:
            清理的检查点数量
        """
        cleaned: int = 0
        now: datetime = datetime.now()

        for record_file in self.storage_path.glob("cp_*_record.json"):
            with open(record_file, "r", encoding="utf-8") as f:
                record: dict[str, Any] = json.load(f)

            timestamp_str: str = record.get("timestamp", "")
            try:
                timestamp: datetime = datetime.fromisoformat(timestamp_str)
            except ValueError:
                continue

            record_ttl: int = ttl_hours or record.get("ttl_hours", self.default_ttl_hours)
            expiry: datetime = timestamp + timedelta(hours=record_ttl)

            if now > expiry:
                # 删除记录文件
                record_file.unlink()
                # 删除状态文件
                checkpoint_id: str = record.get("checkpoint_id", "")
                state_file: Path = self.storage_path / f"{checkpoint_id}_state.json"
                if state_file.exists():
                    state_file.unlink()
                cleaned += 1

        return cleaned

    def _save_checkpoint(
        self,
        record: CheckpointRecord,
        state: dict[str, Any],
    ) -> None:
        """
        保存检查点（内部方法）

        Args:
            record: 检查点记录
            state: 完整状态
        """
        # 保存记录
        record_file: Path = self.storage_path / f"{record.checkpoint_id}_record.json"
        with open(record_file, "w", encoding="utf-8") as f:
            json.dump(record.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

        # 保存状态
        state_file: Path = self.storage_path / f"{record.checkpoint_id}_state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)


# ============================================================================
# 时间旅行器
# ============================================================================


class TimeTravel:
    """
    时间旅行器

    负责：
    - 获取历史状态
    - 状态差异比较
    - 状态回放
    """

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        state_reducer: StateReducer,
    ) -> None:
        """
        初始化时间旅行器

        Args:
            checkpoint_manager: 检查点管理器
            state_reducer: 状态归约器
        """
        self.checkpoint_manager: CheckpointManager = checkpoint_manager
        self.state_reducer: StateReducer = state_reducer

    def get_state_at(
        self,
        checkpoint_id: str,
    ) -> dict[str, Any] | None:
        """
        获取指定检查点的状态

        Args:
            checkpoint_id: 检查点ID

        Returns:
            状态字典，不存在则返回None
        """
        return self.checkpoint_manager.restore(checkpoint_id)

    def get_state_history(
        self,
        thread_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        获取状态历史

        Args:
            thread_id: 线程ID
            limit: 最大数量

        Returns:
            状态历史列表
        """
        checkpoints: list[dict[str, Any]] = self.checkpoint_manager.list(
            thread_id=thread_id,
            limit=limit,
        )

        history: list[dict[str, Any]] = []
        for cp in checkpoints:
            state: dict[str, Any] | None = self.get_state_at(cp["checkpoint_id"])
            if state:
                history.append({
                    "checkpoint_id": cp["checkpoint_id"],
                    "timestamp": cp["timestamp"],
                    "node_name": cp["node_name"],
                    "state": state,
                })

        return history

    def get_state_diff(
        self,
        checkpoint_id_1: str,
        checkpoint_id_2: str,
    ) -> dict[str, Any] | None:
        """
        获取两个检查点的状态差异

        Args:
            checkpoint_id_1: 第一个检查点ID
            checkpoint_id_2: 第二个检查点ID

        Returns:
            差异字典，任一检查点不存在则返回None
        """
        state1: dict[str, Any] | None = self.get_state_at(checkpoint_id_1)
        state2: dict[str, Any] | None = self.get_state_at(checkpoint_id_2)

        if state1 is None or state2 is None:
            return None

        return self.state_reducer.compute_diff(state1, state2)


# ============================================================================
# 状态同步器
# ============================================================================


class StateSynchronizer:
    """
    状态同步器

    负责：
    - 从LangGraph同步状态
    - 检测状态变化
    - 触发事件
    """

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        event_bus: StateEventBus,
    ) -> None:
        """
        初始化状态同步器

        Args:
            checkpoint_manager: 检查点管理器
            event_bus: 事件总线
        """
        self.checkpoint_manager: CheckpointManager = checkpoint_manager
        self.event_bus: StateEventBus = event_bus
        self._current_state: dict[str, Any] = {}
        self._thread_id: str = ""

    def sync(
        self,
        state: dict[str, Any],
        node_name: str,
        thread_id: str | None = None,
    ) -> str:
        """
        同步状态（从LangGraph调用）

        Args:
            state: 当前状态
            node_name: 节点名称
            thread_id: 线程ID（可选）

        Returns:
            检查点ID
        """
        thread_id = thread_id or self._thread_id or f"thread_{uuid.uuid4().hex[:8]}"
        self._thread_id = thread_id

        # 检测变化类型
        event_type: StateEventType = self._detect_change_type(
            self._current_state,
            state,
        )

        # 创建检查点
        checkpoint: CheckpointRecord = self.checkpoint_manager.create(
            state=state,
            thread_id=thread_id,
            node_name=node_name,
            previous_state=self._current_state if self._current_state else None,
        )

        # 发布事件
        event: StateChangeEvent = StateChangeEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            checkpoint_id=checkpoint.checkpoint_id,
            thread_id=thread_id,
            changes=checkpoint.state_diff,
            previous_state=self._current_state,
            current_state=state,
        )

        self.event_bus.emit(event)

        # 更新当前状态
        self._current_state = dict(state)

        return checkpoint.checkpoint_id

    def _detect_change_type(
        self,
        previous: dict[str, Any],
        current: dict[str, Any],
    ) -> StateEventType:
        """
        检测变化类型

        Args:
            previous: 前一个状态
            current: 当前状态

        Returns:
            事件类型
        """
        if not previous:
            return StateEventType.STATE_CHANGE

        # 检查阶段变化
        if previous.get("phase") != current.get("phase"):
            return StateEventType.PHASE_CHANGE

        # 检查任务切换
        if previous.get("current_task") != current.get("current_task"):
            return StateEventType.TASK_SWITCH

        # 检查用户状态变化
        if previous.get("user_state") != current.get("user_state"):
            return StateEventType.USER_STATE_CHANGE

        # 检查步骤计数（任务完成）
        prev_steps: int = previous.get("step_count", 0)
        curr_steps: int = current.get("step_count", 0)
        if prev_steps > 0 and curr_steps >= prev_steps and prev_steps != curr_steps:
            # 检查是否有任务完成标记
            if current.get("task_completed"):
                return StateEventType.TASK_COMPLETE

        return StateEventType.STATE_CHANGE


# ============================================================================
# 全局状态捕捉器（主类）
# ============================================================================


class GlobalStateCapture:
    """
    全局状态捕捉器

    与LangGraph深度集成，提供：
    - 状态同步与检查点管理
    - 状态归约（增量更新）
    - 事件发布/订阅
    - 时间旅行（历史回放）

    使用示例：
    ```python
    # 初始化
    capture = GlobalStateCapture(storage_path="./state_storage")

    # 订阅事件
    capture.subscribe(
        event_types=[StateEventType.PHASE_CHANGE],
        callback=on_phase_change,
    )

    # 从LangGraph同步状态
    checkpoint_id = capture.sync_from_langgraph(
        state={"messages": [...], "phase": "planning"},
        node_name="planner",
    )

    # 恢复检查点
    state = capture.restore_checkpoint(checkpoint_id)

    # 获取状态历史
    history = capture.get_state_history(thread_id="xxx")
    ```
    """

    def __init__(
        self,
        user_id: str = "default_user",
        storage_path: str = "./state_storage",
        default_ttl_hours: int = 168,
    ) -> None:
        """
        初始化全局状态捕捉器

        Args:
            user_id: 用户ID
            storage_path: 存储路径
            default_ttl_hours: 检查点默认TTL（小时）
        """
        self.user_id: str = user_id

        # 初始化子组件
        self._reducer: StateReducer = StateReducer()
        self._event_bus: StateEventBus = StateEventBus()
        self._checkpoint_manager: CheckpointManager = CheckpointManager(
            storage_path=storage_path,
            default_ttl_hours=default_ttl_hours,
        )
        self._synchronizer: StateSynchronizer = StateSynchronizer(
            checkpoint_manager=self._checkpoint_manager,
            event_bus=self._event_bus,
        )
        self._time_travel: TimeTravel = TimeTravel(
            checkpoint_manager=self._checkpoint_manager,
            state_reducer=self._reducer,
        )

    # ========== LangGraph集成 ==========

    def sync_from_langgraph(
        self,
        state: dict[str, Any],
        node_name: str,
        thread_id: str | None = None,
    ) -> str:
        """
        从LangGraph同步状态

        在每个LangGraph节点执行后调用此方法。

        Args:
            state: LangGraph State字典
            node_name: 执行的节点名称
            thread_id: 线程ID（可选）

        Returns:
            检查点ID
        """
        return self._synchronizer.sync(
            state=state,
            node_name=node_name,
            thread_id=thread_id,
        )

    def as_langgraph_node(self) -> Callable[[dict[str, Any]], dict[str, Any]]:
        """
        返回可嵌入LangGraph的节点函数

        使用示例：
        ```python
        capture = GlobalStateCapture()
        workflow.add_node("memory_capture", capture.as_langgraph_node())
        ```

        Returns:
            LangGraph节点函数
        """
        def memory_node(state: dict[str, Any]) -> dict[str, Any]:
            self.sync_from_langgraph(
                state=state,
                node_name="memory_capture",
            )
            return state

        return memory_node

    # ========== 检查点管理 ==========

    def create_checkpoint(
        self,
        state: dict[str, Any],
        thread_id: str | None = None,
        node_name: str = "manual",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        手动创建检查点

        Args:
            state: 状态字典
            thread_id: 线程ID
            node_name: 节点名称
            metadata: 元数据

        Returns:
            检查点ID
        """
        checkpoint: CheckpointRecord = self._checkpoint_manager.create(
            state=state,
            thread_id=thread_id or f"manual_{datetime.now().strftime('%Y%m%d')}",
            node_name=node_name,
            metadata=metadata,
        )
        return checkpoint.checkpoint_id

    def restore_checkpoint(
        self,
        checkpoint_id: str,
    ) -> dict[str, Any] | None:
        """
        恢复检查点

        Args:
            checkpoint_id: 检查点ID

        Returns:
            恢复的状态，不存在则返回None
        """
        state: dict[str, Any] | None = self._checkpoint_manager.restore(checkpoint_id)

        if state:
            # 发布恢复事件
            event: StateChangeEvent = StateChangeEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type=StateEventType.CHECKPOINT_RESTORED,
                checkpoint_id=checkpoint_id,
                thread_id="",
                current_state=state,
            )
            self._event_bus.emit(event)

        return state

    def list_checkpoints(
        self,
        thread_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        列出检查点

        Args:
            thread_id: 线程ID（可选）
            limit: 最大数量

        Returns:
            检查点列表
        """
        return self._checkpoint_manager.list(thread_id=thread_id, limit=limit)

    def garbage_collect(
        self,
        ttl_hours: int | None = None,
    ) -> int:
        """
        清理过期检查点

        Args:
            ttl_hours: TTL（小时）

        Returns:
            清理的检查点数量
        """
        return self._checkpoint_manager.garbage_collect(ttl_hours=ttl_hours)

    # ========== 时间旅行 ==========

    def get_state_at(
        self,
        checkpoint_id: str,
    ) -> dict[str, Any] | None:
        """
        获取指定检查点的状态

        Args:
            checkpoint_id: 检查点ID

        Returns:
            状态字典
        """
        return self._time_travel.get_state_at(checkpoint_id)

    def get_state_history(
        self,
        thread_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        获取状态历史

        Args:
            thread_id: 线程ID
            limit: 最大数量

        Returns:
            状态历史列表
        """
        return self._time_travel.get_state_history(thread_id=thread_id, limit=limit)

    def get_state_diff(
        self,
        checkpoint_id_1: str,
        checkpoint_id_2: str,
    ) -> dict[str, Any] | None:
        """
        获取两个检查点的状态差异

        Args:
            checkpoint_id_1: 第一个检查点ID
            checkpoint_id_2: 第二个检查点ID

        Returns:
            差异字典
        """
        return self._time_travel.get_state_diff(checkpoint_id_1, checkpoint_id_2)

    # ========== 事件发布/订阅 ==========

    def subscribe(
        self,
        event_types: list[StateEventType],
        callback: Callable[[StateChangeEvent], None],
        subscription_id: str | None = None,
    ) -> str:
        """
        订阅状态事件

        Args:
            event_types: 订阅的事件类型列表
            callback: 回调函数
            subscription_id: 订阅ID（可选）

        Returns:
            订阅ID
        """
        return self._event_bus.subscribe(
            event_types=event_types,
            callback=callback,
            subscription_id=subscription_id,
        )

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        取消订阅

        Args:
            subscription_id: 订阅ID

        Returns:
            是否成功取消
        """
        return self._event_bus.unsubscribe(subscription_id)

    def get_subscriptions(self) -> list[dict[str, Any]]:
        """
        获取所有订阅

        Returns:
            订阅列表
        """
        return self._event_bus.get_subscriptions()

    # ========== 兼容旧接口 ==========

    def capture(
        self,
        situation: Any,
        memory: Any,
        context: Any,
        conversation_turn: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        兼容旧接口：捕捉全局状态

        注意：建议使用 sync_from_langgraph() 替代

        Args:
            situation: 情境感知结果
            memory: 长期记忆容器
            context: 重构上下文
            conversation_turn: 当前对话轮次信息

        Returns:
            状态快照
        """
        # 从旧参数构建状态
        state: dict[str, Any] = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "conversation_turn": conversation_turn,
        }

        # 提取情境信息
        if hasattr(situation, "current_task"):
            state["current_task"] = getattr(situation.current_task, "task_type", None)
            state["task_phase"] = getattr(situation.current_task, "task_phase", None)

        if hasattr(situation, "user_current_state"):
            state["user_state"] = getattr(situation.user_current_state, "mental_model", None)

        if hasattr(situation, "context_anchors"):
            state["emotion_state"] = getattr(situation.context_anchors, "emotional", None)

        # 同步状态
        checkpoint_id: str = self.sync_from_langgraph(
            state=state,
            node_name="legacy_capture",
        )

        return {
            "snapshot_id": checkpoint_id,
            "user_id": self.user_id,
            "timestamp": state["timestamp"],
            "state": state,
        }

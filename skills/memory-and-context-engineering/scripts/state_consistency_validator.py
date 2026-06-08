"""
Agent Memory System - State Consistency Validator（状态一致性校验器）

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
确保多个模块间的状态一致性，防止状态冲突导致任务中断。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .types import ConflictSeverity


# ============================================================================
# 枚举类型
# ============================================================================


class ConsistencyLevel(str, Enum):
    """一致性级别"""

    FULLY_CONSISTENT = "fully_consistent"     # 完全一致
    MOSTLY_CONSISTENT = "mostly_consistent"   # 基本一致
    PARTIALLY_CONSISTENT = "partially_consistent"  # 部分一致
    INCONSISTENT = "inconsistent"             # 不一致
    SEVERELY_INCONSISTENT = "severely_inconsistent"  # 严重不一致


class ResolutionStrategy(str, Enum):
    """解决策略"""

    AUTO_FIX = "auto_fix"              # 自动修复
    LATEST_WINS = "latest_wins"        # 最新优先
    PRIORITY_WINS = "priority_wins"    # 优先级优先
    USER_DECISION = "user_decision"    # 用户决策
    MANUAL_FIX = "manual_fix"          # 手动修复


class StateModule(str, Enum):
    """状态模块"""

    TASK_PROGRESS = "task_progress"
    SHORT_TERM_MEMORY = "short_term_memory"
    LONG_TERM_MEMORY = "long_term_memory"
    CONTEXT_ORCHESTRATOR = "context_orchestrator"
    GLOBAL_STATE = "global_state"


# ============================================================================
# 数据模型
# ============================================================================


class StateSnapshot(BaseModel):
    """状态快照"""

    module: StateModule
    state: dict[str, Any] = Field(default_factory=dict)
    version: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    checksum: str = Field(default="")


class StateConflict(BaseModel):
    """状态冲突"""

    conflict_id: str = Field(
        default_factory=lambda: f"conflict_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )

    # 冲突描述
    description: str
    severity: ConflictSeverity = Field(default=ConflictSeverity.MEDIUM)

    # 冲突模块
    modules_involved: list[StateModule] = Field(default_factory=list)

    # 冲突值
    conflicting_values: dict[str, list[Any]] = Field(default_factory=dict)

    # 解决建议
    suggested_resolution: ResolutionStrategy = Field(default=ResolutionStrategy.LATEST_WINS)
    resolution_details: str = Field(default="")

    # 状态
    resolved: bool = Field(default=False)
    resolved_at: datetime | None = None
    resolved_value: Any | None = None

    created_at: datetime = Field(default_factory=datetime.now)


class ConsistencyReport(BaseModel):
    """一致性报告"""

    # 一致性级别
    level: ConsistencyLevel = Field(default=ConsistencyLevel.FULLY_CONSISTENT)

    # 各模块状态
    module_states: dict[str, StateSnapshot] = Field(default_factory=dict)

    # 检测到的冲突
    conflicts: list[StateConflict] = Field(default_factory=list)

    # 统计
    total_checks: int = Field(default=0)
    passed_checks: int = Field(default=0)
    failed_checks: int = Field(default=0)

    # 建议
    recommendations: list[str] = Field(default_factory=list)

    # 元数据
    report_id: str = Field(
        default_factory=lambda: f"report_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class ValidatorConfig(BaseModel):
    """校验器配置"""

    # 一致性阈值
    fully_consistent_threshold: float = Field(default=1.0)
    mostly_consistent_threshold: float = Field(default=0.9)
    partially_consistent_threshold: float = Field(default=0.7)

    # 自动修复
    enable_auto_fix: bool = Field(default=True)
    auto_fix_severity_threshold: ConflictSeverity = Field(default=ConflictSeverity.LOW)

    # 校验规则
    check_interval_seconds: int = Field(default=60)
    max_conflicts: int = Field(default=100)


# ============================================================================
# State Consistency Validator
# ============================================================================


class StateConsistencyValidator:
    """
    状态一致性校验器

    职责：
    - 校验多模块状态一致性
    - 检测状态冲突
    - 自动修复不一致

    使用示例：
    ```python
    from scripts.state_consistency_validator import StateConsistencyValidator

    validator = StateConsistencyValidator()

    # 注册模块状态
    validator.register_state(
        module="task_progress",
        state={"current_task": "实现登录", "progress": 60},
    )

    validator.register_state(
        module="short_term_memory",
        state={"current_task": "实现注册"},
    )

    # 校验一致性
    report = validator.validate()

    if report.conflicts:
        print(f"发现 {len(report.conflicts)} 个冲突")
        for conflict in report.conflicts:
            print(f"  - {conflict.description}")

    # 自动修复
    fixed = validator.auto_fix(report)
    print(f"修复了 {fixed} 个冲突")
    ```
    """

    def __init__(self, config: ValidatorConfig | None = None):
        """初始化状态一致性校验器"""
        self._config = config or ValidatorConfig()
        self._module_states: dict[StateModule, StateSnapshot] = {}
        self._conflict_history: list[StateConflict] = []

    # -----------------------------------------------------------------------
    # 状态注册
    # -----------------------------------------------------------------------

    def register_state(
        self,
        module: StateModule | str,
        state: dict[str, Any],
        version: int = 0,
    ) -> None:
        """注册模块状态"""
        if isinstance(module, str):
            module = StateModule(module)

        snapshot = StateSnapshot(
            module=module,
            state=state,
            version=version,
            checksum=self._compute_checksum(state),
        )
        self._module_states[module] = snapshot

    def update_state(
        self,
        module: StateModule | str,
        updates: dict[str, Any],
    ) -> None:
        """更新模块状态"""
        if isinstance(module, str):
            module = StateModule(module)

        if module in self._module_states:
            current = self._module_states[module]
            new_state = {**current.state, **updates}
            self.register_state(
                module=module,
                state=new_state,
                version=current.version + 1,
            )

    def get_state(self, module: StateModule | str) -> dict[str, Any] | None:
        """获取模块状态"""
        if isinstance(module, str):
            module = StateModule(module)
        snapshot = self._module_states.get(module)
        return snapshot.state if snapshot else None

    # -----------------------------------------------------------------------
    # 一致性校验
    # -----------------------------------------------------------------------

    def validate(self) -> ConsistencyReport:
        """执行一致性校验"""
        conflicts: list[StateConflict] = []
        total_checks = 0
        passed_checks = 0

        # 1. 检查关键状态字段一致性
        key_fields = ["current_task", "phase", "goal", "session_id"]
        for field in key_fields:
            conflict = self._check_field_consistency(field)
            total_checks += 1
            if conflict:
                conflicts.append(conflict)
            else:
                passed_checks += 1

        # 2. 检查版本一致性
        version_conflict = self._check_version_consistency()
        total_checks += 1
        if version_conflict:
            conflicts.append(version_conflict)
        else:
            passed_checks += 1

        # 3. 检查时间戳一致性
        time_conflict = self._check_timestamp_consistency()
        total_checks += 1
        if time_conflict:
            conflicts.append(time_conflict)
        else:
            passed_checks += 1

        # 4. 检查跨模块依赖
        dep_conflicts = self._check_cross_module_dependencies()
        total_checks += len(dep_conflicts)
        conflicts.extend(dep_conflicts)
        passed_checks += len(dep_conflicts) - len(dep_conflicts)

        # 计算一致性级别
        failed_checks = len(conflicts)
        consistency_ratio = passed_checks / total_checks if total_checks > 0 else 1.0
        level = self._determine_level(consistency_ratio)

        # 生成建议
        recommendations = self._generate_recommendations(conflicts)

        return ConsistencyReport(
            level=level,
            module_states={
                m.value: s for m, s in self._module_states.items()
            },
            conflicts=conflicts,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            recommendations=recommendations,
        )

    def _check_field_consistency(self, field: str) -> StateConflict | None:
        """检查字段一致性"""
        values: dict[StateModule, Any] = {}

        for module, snapshot in self._module_states.items():
            if field in snapshot.state:
                values[module] = snapshot.state[field]

        if not values:
            return None

        # 检查是否一致
        unique_values = set(str(v) for v in values.values())
        if len(unique_values) <= 1:
            return None

        # 存在冲突
        return StateConflict(
            description=f"字段 '{field}' 在不同模块中不一致",
            severity=ConflictSeverity.HIGH,
            modules_involved=list(values.keys()),
            conflicting_values={
                field: [str(v) for v in values.values()]
            },
            suggested_resolution=ResolutionStrategy.LATEST_WINS,
        )

    def _check_version_consistency(self) -> StateConflict | None:
        """检查版本一致性"""
        versions: dict[StateModule, int] = {}

        for module, snapshot in self._module_states.items():
            versions[module] = snapshot.version

        # 检查版本差距
        if versions:
            max_version = max(versions.values())
            min_version = min(versions.values())

            if max_version - min_version > 5:
                outdated = [
                    m for m, v in versions.items()
                    if v < max_version - 2
                ]
                return StateConflict(
                    description="部分模块状态版本过旧",
                    severity=ConflictSeverity.MEDIUM,
                    modules_involved=outdated,
                    suggested_resolution=ResolutionStrategy.AUTO_FIX,
                    resolution_details="建议同步更新过时模块状态",
                )

        return None

    def _check_timestamp_consistency(self) -> StateConflict | None:
        """检查时间戳一致性"""
        timestamps: list[datetime] = []

        for snapshot in self._module_states.values():
            timestamps.append(snapshot.timestamp)

        if not timestamps:
            return None

        # 检查时间差距
        max_time = max(timestamps)
        min_time = min(timestamps)

        time_diff = (max_time - min_time).total_seconds()
        if time_diff > 300:  # 5分钟
            return StateConflict(
                description=f"模块状态时间戳差距过大 ({time_diff:.0f}秒)",
                severity=ConflictSeverity.LOW,
                suggested_resolution=ResolutionStrategy.LATEST_WINS,
            )

        return None

    def _check_cross_module_dependencies(self) -> list[StateConflict]:
        """检查跨模块依赖"""
        conflicts: list[StateConflict] = []

        # 检查任务状态与记忆状态的一致性
        task_state = self._module_states.get(StateModule.TASK_PROGRESS)
        memory_state = self._module_states.get(StateModule.SHORT_TERM_MEMORY)

        if task_state and memory_state:
            task_goal = task_state.state.get("goal", "")
            memory_topic = memory_state.state.get("topic", "")

            # 如果两者都有值但不相关
            if task_goal and memory_topic and task_goal not in memory_topic:
                conflicts.append(StateConflict(
                    description="任务目标与短期记忆主题不一致",
                    severity=ConflictSeverity.LOW,
                    modules_involved=[StateModule.TASK_PROGRESS, StateModule.SHORT_TERM_MEMORY],
                    suggested_resolution=ResolutionStrategy.PRIORITY_WINS,
                ))

        return conflicts

    def _determine_level(self, consistency_ratio: float) -> ConsistencyLevel:
        """确定一致性级别"""
        if consistency_ratio >= self._config.fully_consistent_threshold:
            return ConsistencyLevel.FULLY_CONSISTENT
        elif consistency_ratio >= self._config.mostly_consistent_threshold:
            return ConsistencyLevel.MOSTLY_CONSISTENT
        elif consistency_ratio >= self._config.partially_consistent_threshold:
            return ConsistencyLevel.PARTIALLY_CONSISTENT
        elif consistency_ratio >= 0.5:
            return ConsistencyLevel.INCONSISTENT
        else:
            return ConsistencyLevel.SEVERELY_INCONSISTENT

    def _generate_recommendations(self, conflicts: list[StateConflict]) -> list[str]:
        """生成建议"""
        recommendations: list[str] = []

        critical = [c for c in conflicts if c.severity == ConflictSeverity.CRITICAL]
        if critical:
            recommendations.append(f"立即解决 {len(critical)} 个严重冲突")

        high = [c for c in conflicts if c.severity == ConflictSeverity.HIGH]
        if high:
            recommendations.append(f"尽快解决 {len(high)} 个高优先级冲突")

        # 根据冲突类型建议
        auto_fixable = [
            c for c in conflicts
            if c.suggested_resolution == ResolutionStrategy.AUTO_FIX
        ]
        if auto_fixable:
            recommendations.append(f"可自动修复 {len(auto_fixable)} 个冲突")

        return recommendations

    # -----------------------------------------------------------------------
    # 自动修复
    # -----------------------------------------------------------------------

    def auto_fix(self, report: ConsistencyReport) -> int:
        """自动修复冲突"""
        if not self._config.enable_auto_fix:
            return 0

        fixed = 0

        for conflict in report.conflicts:
            # 检查是否可以自动修复
            if not self._can_auto_fix(conflict):
                continue

            # 执行修复
            if self._fix_conflict(conflict):
                conflict.resolved = True
                conflict.resolved_at = datetime.now()
                fixed += 1

        # 记录历史
        self._conflict_history.extend(report.conflicts)

        return fixed

    def _can_auto_fix(self, conflict: StateConflict) -> bool:
        """判断是否可以自动修复"""
        # 检查严重程度
        severity_order = {
            ConflictSeverity.LOW: 0,
            ConflictSeverity.MEDIUM: 1,
            ConflictSeverity.HIGH: 2,
            ConflictSeverity.CRITICAL: 3,
        }

        threshold = severity_order.get(self._config.auto_fix_severity_threshold, 1)
        conflict_level = severity_order.get(conflict.severity, 1)

        return conflict_level <= threshold

    def _fix_conflict(self, conflict: StateConflict) -> bool:
        """修复单个冲突"""
        if conflict.suggested_resolution == ResolutionStrategy.LATEST_WINS:
            return self._fix_latest_wins(conflict)
        elif conflict.suggested_resolution == ResolutionStrategy.PRIORITY_WINS:
            return self._fix_priority_wins(conflict)
        else:
            return False

    def _fix_latest_wins(self, conflict: StateConflict) -> bool:
        """最新优先修复"""
        # 找到最新的状态
        latest_module = None
        latest_time = datetime.min

        for module in conflict.modules_involved:
            snapshot = self._module_states.get(module)
            if snapshot and snapshot.timestamp > latest_time:
                latest_time = snapshot.timestamp
                latest_module = module

        if not latest_module:
            return False

        # 应用最新值
        latest_state = self._module_states[latest_module].state

        for field, values in conflict.conflicting_values.items():
            if field in latest_state:
                conflict.resolved_value = latest_state[field]
                # 更新其他模块
                for module in conflict.modules_involved:
                    if module != latest_module:
                        self.update_state(module, {field: latest_state[field]})

        return True

    def _fix_priority_wins(self, conflict: StateConflict) -> bool:
        """优先级优先修复"""
        # 定义模块优先级
        priority = {
            StateModule.TASK_PROGRESS: 10,
            StateModule.GLOBAL_STATE: 9,
            StateModule.CONTEXT_ORCHESTRATOR: 8,
            StateModule.LONG_TERM_MEMORY: 5,
            StateModule.SHORT_TERM_MEMORY: 3,
        }

        # 找到最高优先级模块
        highest_module = max(
            conflict.modules_involved,
            key=lambda m: priority.get(m, 0),
        )

        highest_state = self._module_states[highest_module].state

        for field, values in conflict.conflicting_values.items():
            if field in highest_state:
                conflict.resolved_value = highest_state[field]
                for module in conflict.modules_involved:
                    if module != highest_module:
                        self.update_state(module, {field: highest_state[field]})

        return True

    # -----------------------------------------------------------------------
    # 工具方法
    # -----------------------------------------------------------------------

    def _compute_checksum(self, state: dict[str, Any]) -> str:
        """计算状态校验和"""
        import hashlib
        import json

        state_str = json.dumps(state, sort_keys=True, default=str)
        return hashlib.md5(state_str.encode()).hexdigest()[:8]

    def get_conflict_history(self, limit: int = 100) -> list[StateConflict]:
        """获取冲突历史"""
        return self._conflict_history[-limit:]

    def clear_history(self) -> None:
        """清空历史"""
        self._conflict_history.clear()


# ============================================================================
# 工厂函数
# ============================================================================


def create_state_validator() -> StateConsistencyValidator:
    """创建状态一致性校验器"""
    return StateConsistencyValidator()


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "ConsistencyLevel",
    "ConflictSeverity",
    "ResolutionStrategy",
    "StateModule",
    "StateSnapshot",
    "StateConflict",
    "ConsistencyReport",
    "ValidatorConfig",
    "StateConsistencyValidator",
    "create_state_validator",
]

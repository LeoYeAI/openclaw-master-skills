"""
Agent Memory System - Task Progress Tracker（任务进度追踪器）

=== 功能说明 ===
对应 Context Engineering 核心能力：状态

实现文档要求：
- "知道自己处在任务链的哪个位置"
- "知道当前目标、已完成步骤、下一步、已确认结论、临时推断"

核心能力：
1. 任务步骤追踪 - 记录已完成步骤、当前步骤
2. 步骤依赖分析 - 分析步骤之间的依赖关系
3. 下一步推理 - 基于当前状态推断下一步行动
4. 目标对齐检查 - 检查当前行动是否与目标一致

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * redis: >=4.5.0
    - 用途：进度状态存储（可选）
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  redis>=4.5.0
  ```
=== 声明结束 ===

安全提醒：确保任务状态的持久化和一致性
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from .types import PhaseType, ScenarioType
from .redis_adapter import RedisAdapter


# ============================================================================
# 枚举类型
# ============================================================================


class StepStatus(str, Enum):
    """步骤状态"""

    PENDING = "pending"          # 待执行
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    SKIPPED = "skipped"          # 已跳过
    BLOCKED = "blocked"          # 被阻塞


class StepType(str, Enum):
    """步骤类型"""

    ANALYSIS = "analysis"        # 分析
    PLANNING = "planning"        # 规划
    EXECUTION = "execution"      # 执行
    VERIFICATION = "verification"  # 验证
    REFINEMENT = "refinement"    # 优化


class GoalStatus(str, Enum):
    """目标状态"""

    NOT_STARTED = "not_started"  # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    ACHIEVED = "achieved"        # 已达成
    ABANDONED = "abandoned"      # 已放弃
    BLOCKED = "blocked"          # 被阻塞


class AlignmentLevel(str, Enum):
    """对齐程度"""

    HIGH = "high"        # 高度对齐
    MEDIUM = "medium"    # 中度对齐
    LOW = "low"          # 低度对齐
    MISALIGNED = "misaligned"  # 未对齐


# ============================================================================
# 数据模型
# ============================================================================


class TaskStep(BaseModel):
    """任务步骤"""

    step_id: str = Field(description="步骤ID")
    step_name: str = Field(description="步骤名称")
    step_type: StepType = Field(description="步骤类型")
    status: StepStatus = Field(default=StepStatus.PENDING, description="状态")

    # 内容
    description: str = Field(default="", description="步骤描述")
    action: str = Field(default="", description="执行动作")
    result: str | None = Field(default=None, description="执行结果")

    # 依赖
    dependencies: list[str] = Field(default_factory=list, description="依赖的步骤ID")
    dependents: list[str] = Field(default_factory=list, description="被依赖的步骤ID")

    # 时间
    started_at: datetime | None = Field(default=None, description="开始时间")
    completed_at: datetime | None = Field(default=None, description="完成时间")

    # 元数据
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class TaskGoal(BaseModel):
    """任务目标"""

    goal_id: str = Field(description="目标ID")
    goal_name: str = Field(description="目标名称")
    description: str = Field(default="", description="目标描述")
    status: GoalStatus = Field(default=GoalStatus.NOT_STARTED, description="状态")

    # 关联步骤
    steps: list[str] = Field(default_factory=list, description="关联的步骤ID")

    # 成功标准
    success_criteria: list[str] = Field(default_factory=list, description="成功标准")

    # 时间
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    achieved_at: datetime | None = Field(default=None, description="达成时间")


class StepDependency(BaseModel):
    """步骤依赖关系"""

    from_step: str = Field(description="源步骤ID")
    to_step: str = Field(description="目标步骤ID")
    dependency_type: str = Field(
        default="sequential",
        description="依赖类型: sequential, conditional, parallel"
    )
    condition: str | None = Field(
        default=None,
        description="条件（条件依赖时）"
    )


class ProgressReport(BaseModel):
    """进度报告"""

    # 任务信息
    task_id: str = Field(description="任务ID")
    task_name: str = Field(description="任务名称")

    # 进度统计
    total_steps: int = Field(default=0, description="总步骤数")
    completed_steps: int = Field(default=0, description="已完成步骤数")
    failed_steps: int = Field(default=0, description="失败步骤数")
    in_progress_steps: int = Field(default=0, description="进行中步骤数")

    # 完成率
    completion_rate: float = Field(ge=0.0, le=1.0, default=0.0, description="完成率")

    # 当前阶段
    current_phase: PhaseType | None = Field(default=None, description="当前阶段")
    current_step: TaskStep | None = Field(default=None, description="当前步骤")

    # 下一步建议
    next_steps: list[TaskStep] = Field(default_factory=list, description="建议的下一步")

    # 问题
    blocked_steps: list[TaskStep] = Field(default_factory=list, description="被阻塞的步骤")
    failed_steps_detail: list[TaskStep] = Field(default_factory=list, description="失败步骤详情")

    # 时间
    estimated_remaining: int | None = Field(
        default=None,
        description="预估剩余时间（秒）"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class GoalAlignmentCheck(BaseModel):
    """目标对齐检查结果"""

    # 检查结果
    is_aligned: bool = Field(description="是否对齐")
    alignment_level: AlignmentLevel = Field(description="对齐程度")
    alignment_score: float = Field(ge=0.0, le=1.0, description="对齐分数")

    # 分析
    current_action: str = Field(description="当前行动")
    goal: str = Field(description="目标")
    alignment_reason: str = Field(description="对齐原因分析")

    # 建议
    suggestions: list[str] = Field(default_factory=list, description="调整建议")

    # 元数据
    checked_at: datetime = Field(default_factory=datetime.now, description="检查时间")


class TaskProgressConfig(BaseModel):
    """任务进度配置"""

    # 自动检查对齐
    auto_alignment_check: bool = Field(default=True, description="自动检查目标对齐")

    # 最大步骤数
    max_steps: int = Field(default=100, description="最大步骤数")

    # 进度报告间隔
    report_interval: int = Field(default=5, description="进度报告间隔（步骤数）")


# ============================================================================
# Task Progress Tracker
# ============================================================================


class TaskProgressTracker:
    """
    任务进度追踪器

    实现文档要求："知道自己处在任务链的哪个位置"

    核心能力：
    1. 追踪任务步骤
    2. 分析步骤依赖
    3. 推断下一步
    4. 检查目标对齐

    使用示例：
    ```python
    from scripts.task_progress import TaskProgressTracker

    # 初始化
    tracker = TaskProgressTracker(
        task_id="task_001",
        task_name="实现用户登录功能",
    )

    # 设置目标
    tracker.set_goal(
        goal_id="goal_001",
        goal_name="实现登录",
        success_criteria=["用户可以登录", "登录状态持久化"],
    )

    # 追踪步骤
    tracker.track_step(
        step_id="step_001",
        step_name="设计登录流程",
        step_type=StepType.PLANNING,
        description="设计用户登录的业务流程",
    )

    # 完成步骤
    tracker.complete_step("step_001", result="流程设计完成")

    # 获取进度报告
    report = tracker.get_progress_report()
    print(f"完成率: {report.completion_rate:.1%}")

    # 推断下一步
    next_step = tracker.infer_next_step()
    if next_step:
        print(f"建议下一步: {next_step.step_name}")

    # 检查目标对齐
    alignment = tracker.check_goal_alignment(
        current_action="实现前端登录表单",
    )
    if alignment.alignment_level == AlignmentLevel.LOW:
        print(f"警告: {alignment.alignment_reason}")
    ```
    """

    def __init__(
        self,
        task_id: str,
        task_name: str,
        redis_adapter: RedisAdapter | None = None,
        config: TaskProgressConfig | None = None,
    ) -> None:
        """
        初始化任务进度追踪器

        Args:
            task_id: 任务ID
            task_name: 任务名称
            redis_adapter: Redis 适配器（可选，用于持久化）
            config: 配置
        """
        self._task_id = task_id
        self._task_name = task_name
        self._redis = redis_adapter
        self._config = config or TaskProgressConfig()

        # 任务状态
        self._goals: dict[str, TaskGoal] = {}
        self._steps: dict[str, TaskStep] = {}
        self._dependencies: list[StepDependency] = []

        # 当前状态
        self._current_phase: PhaseType = PhaseType.EXPLORATION
        self._current_step_id: str | None = None

        # 步骤模板（用于推断下一步）
        self._step_templates: dict[PhaseType, list[StepType]] = {
            PhaseType.EXPLORATION: [
                StepType.ANALYSIS,
                StepType.PLANNING,
            ],
            PhaseType.DESIGN: [
                StepType.PLANNING,
                StepType.ANALYSIS,
            ],
            PhaseType.IMPLEMENTATION: [
                StepType.EXECUTION,
                StepType.VERIFICATION,
            ],
            PhaseType.VERIFICATION: [
                StepType.VERIFICATION,
                StepType.REFINEMENT,
            ],
            PhaseType.REFINEMENT: [
                StepType.REFINEMENT,
                StepType.VERIFICATION,
            ],
        }

    # -----------------------------------------------------------------------
    # 目标管理
    # -----------------------------------------------------------------------

    def set_goal(
        self,
        goal_id: str,
        goal_name: str,
        description: str = "",
        success_criteria: list[str] | None = None,
    ) -> TaskGoal:
        """
        设置任务目标

        Args:
            goal_id: 目标ID
            goal_name: 目标名称
            description: 目标描述
            success_criteria: 成功标准

        Returns:
            TaskGoal 任务目标
        """
        goal = TaskGoal(
            goal_id=goal_id,
            goal_name=goal_name,
            description=description,
            success_criteria=success_criteria or [],
        )

        self._goals[goal_id] = goal
        self._persist_state()

        return goal

    def get_current_goal(self) -> TaskGoal | None:
        """获取当前目标"""
        for goal in self._goals.values():
            if goal.status == GoalStatus.IN_PROGRESS:
                return goal
        return None

    def achieve_goal(self, goal_id: str) -> bool:
        """
        标记目标为已达成

        Args:
            goal_id: 目标ID

        Returns:
            是否成功
        """
        if goal_id not in self._goals:
            return False

        goal = self._goals[goal_id]
        goal.status = GoalStatus.ACHIEVED
        goal.achieved_at = datetime.now()

        self._persist_state()
        return True

    # -----------------------------------------------------------------------
    # 步骤追踪
    # -----------------------------------------------------------------------

    def track_step(
        self,
        step_id: str,
        step_name: str,
        step_type: StepType,
        description: str = "",
        action: str = "",
        dependencies: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TaskStep:
        """
        追踪任务步骤

        Args:
            step_id: 步骤ID
            step_name: 步骤名称
            step_type: 步骤类型
            description: 步骤描述
            action: 执行动作
            dependencies: 依赖的步骤ID列表
            metadata: 元数据

        Returns:
            TaskStep 任务步骤
        """
        step = TaskStep(
            step_id=step_id,
            step_name=step_name,
            step_type=step_type,
            description=description,
            action=action,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        self._steps[step_id] = step

        # 记录依赖关系
        for dep_id in step.dependencies:
            if dep_id in self._steps:
                self._steps[dep_id].dependents.append(step_id)
                self._dependencies.append(StepDependency(
                    from_step=dep_id,
                    to_step=step_id,
                    dependency_type="sequential",
                ))

        self._persist_state()
        return step

    def start_step(self, step_id: str) -> bool:
        """
        开始执行步骤

        Args:
            step_id: 步骤ID

        Returns:
            是否成功
        """
        if step_id not in self._steps:
            return False

        step = self._steps[step_id]

        # 检查依赖
        for dep_id in step.dependencies:
            if dep_id in self._steps:
                dep_step = self._steps[dep_id]
                if dep_step.status != StepStatus.COMPLETED:
                    step.status = StepStatus.BLOCKED
                    step.metadata["blocked_by"] = dep_id
                    self._persist_state()
                    return False

        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.now()
        self._current_step_id = step_id

        # 更新阶段
        self._update_phase(step)

        self._persist_state()
        return True

    def complete_step(
        self,
        step_id: str,
        result: str | None = None,
    ) -> bool:
        """
        完成步骤

        Args:
            step_id: 步骤ID
            result: 执行结果

        Returns:
            是否成功
        """
        if step_id not in self._steps:
            return False

        step = self._steps[step_id]
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.now()
        step.result = result

        # 解除阻塞
        self._unblock_dependents(step_id)

        # 更新目标进度
        self._update_goal_progress()

        # 清除当前步骤
        if self._current_step_id == step_id:
            self._current_step_id = None

        self._persist_state()
        return True

    def fail_step(
        self,
        step_id: str,
        reason: str,
    ) -> bool:
        """
        标记步骤失败

        Args:
            step_id: 步骤ID
            reason: 失败原因

        Returns:
            是否成功
        """
        if step_id not in self._steps:
            return False

        step = self._steps[step_id]
        step.status = StepStatus.FAILED
        step.completed_at = datetime.now()
        step.result = f"失败: {reason}"

        # 清除当前步骤
        if self._current_step_id == step_id:
            self._current_step_id = None

        self._persist_state()
        return True

    def skip_step(
        self,
        step_id: str,
        reason: str = "",
    ) -> bool:
        """
        跳过步骤

        Args:
            step_id: 步骤ID
            reason: 跳过原因

        Returns:
            是否成功
        """
        if step_id not in self._steps:
            return False

        step = self._steps[step_id]
        step.status = StepStatus.SKIPPED
        step.completed_at = datetime.now()
        step.result = f"跳过: {reason}" if reason else "跳过"

        # 解除阻塞
        self._unblock_dependents(step_id)

        # 清除当前步骤
        if self._current_step_id == step_id:
            self._current_step_id = None

        self._persist_state()
        return True

    # -----------------------------------------------------------------------
    # 进度报告
    # -----------------------------------------------------------------------

    def get_progress_report(self) -> ProgressReport:
        """
        获取进度报告

        Returns:
            ProgressReport 进度报告
        """
        steps = list(self._steps.values())

        # 统计
        total = len(steps)
        completed = sum(1 for s in steps if s.status == StepStatus.COMPLETED)
        failed = sum(1 for s in steps if s.status == StepStatus.FAILED)
        in_progress = sum(1 for s in steps if s.status == StepStatus.IN_PROGRESS)
        blocked = sum(1 for s in steps if s.status == StepStatus.BLOCKED)

        # 完成率
        completion_rate = completed / total if total > 0 else 0.0

        # 当前步骤
        current_step = None
        if self._current_step_id and self._current_step_id in self._steps:
            current_step = self._steps[self._current_step_id]

        # 下一步建议
        next_steps = self._get_next_steps()

        # 被阻塞的步骤
        blocked_steps = [s for s in steps if s.status == StepStatus.BLOCKED]

        # 失败的步骤
        failed_steps = [s for s in steps if s.status == StepStatus.FAILED]

        return ProgressReport(
            task_id=self._task_id,
            task_name=self._task_name,
            total_steps=total,
            completed_steps=completed,
            failed_steps=failed,
            in_progress_steps=in_progress,
            completion_rate=completion_rate,
            current_phase=self._current_phase,
            current_step=current_step,
            next_steps=next_steps,
            blocked_steps=blocked_steps,
            failed_steps_detail=failed_steps,
        )

    # -----------------------------------------------------------------------
    # 下一步推理
    # -----------------------------------------------------------------------

    def infer_next_step(self) -> TaskStep | None:
        """
        推断下一步

        基于以下因素：
        1. 当前阶段
        2. 已完成步骤
        3. 步骤依赖
        4. 步骤模板

        Returns:
            TaskStep 建议的下一步，没有则返回 None
        """
        # 获取下一个可执行的步骤
        next_steps = self._get_next_steps()

        if next_steps:
            return next_steps[0]

        # 基于阶段模板推断
        expected_types = self._step_templates.get(self._current_phase, [])

        for step_type in expected_types:
            # 查找该类型的待执行步骤
            for step in self._steps.values():
                if step.step_type == step_type and step.status == StepStatus.PENDING:
                    return step

        return None

    def _get_next_steps(self) -> list[TaskStep]:
        """获取可执行的下一步"""
        next_steps: list[TaskStep] = []

        for step in self._steps.values():
            if step.status != StepStatus.PENDING:
                continue

            # 检查依赖是否满足
            can_execute = True
            for dep_id in step.dependencies:
                if dep_id in self._steps:
                    dep_step = self._steps[dep_id]
                    if dep_step.status not in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                        can_execute = False
                        break

            if can_execute:
                next_steps.append(step)

        # 按步骤类型排序
        type_order = {
            StepType.ANALYSIS: 0,
            StepType.PLANNING: 1,
            StepType.EXECUTION: 2,
            StepType.VERIFICATION: 3,
            StepType.REFINEMENT: 4,
        }

        next_steps.sort(key=lambda s: type_order.get(s.step_type, 5))

        return next_steps

    # -----------------------------------------------------------------------
    # 目标对齐检查
    # -----------------------------------------------------------------------

    def check_goal_alignment(
        self,
        current_action: str,
        goal_id: str | None = None,
    ) -> GoalAlignmentCheck:
        """
        检查目标对齐

        判断当前行动是否与目标一致

        Args:
            current_action: 当前行动
            goal_id: 目标ID（不指定则检查当前目标）

        Returns:
            GoalAlignmentCheck 检查结果
        """
        # 获取目标
        goal = None
        if goal_id:
            goal = self._goals.get(goal_id)
        else:
            goal = self.get_current_goal()

        if not goal:
            return GoalAlignmentCheck(
                is_aligned=False,
                alignment_level=AlignmentLevel.MISALIGNED,
                alignment_score=0.0,
                current_action=current_action,
                goal="无目标",
                alignment_reason="未设置目标",
            )

        # 检查对齐
        alignment_score = self._calculate_alignment_score(
            current_action=current_action,
            goal=goal,
        )

        # 确定对齐程度
        if alignment_score >= 0.8:
            alignment_level = AlignmentLevel.HIGH
            is_aligned = True
        elif alignment_score >= 0.5:
            alignment_level = AlignmentLevel.MEDIUM
            is_aligned = True
        elif alignment_score >= 0.3:
            alignment_level = AlignmentLevel.LOW
            is_aligned = False
        else:
            alignment_level = AlignmentLevel.MISALIGNED
            is_aligned = False

        # 生成原因分析
        reason = self._generate_alignment_reason(
            current_action=current_action,
            goal=goal,
            alignment_score=alignment_score,
        )

        # 生成建议
        suggestions = self._generate_alignment_suggestions(
            current_action=current_action,
            goal=goal,
            alignment_level=alignment_level,
        )

        return GoalAlignmentCheck(
            is_aligned=is_aligned,
            alignment_level=alignment_level,
            alignment_score=alignment_score,
            current_action=current_action,
            goal=goal.goal_name,
            alignment_reason=reason,
            suggestions=suggestions,
        )

    def _calculate_alignment_score(
        self,
        current_action: str,
        goal: TaskGoal,
    ) -> float:
        """
        计算对齐分数

        基于以下因素：
        1. 关键词匹配
        2. 步骤关联
        3. 阶段匹配
        """
        score = 0.0

        # 关键词匹配（简单实现）
        action_lower = current_action.lower()
        goal_lower = goal.goal_name.lower()

        # 目标名称中的关键词
        goal_keywords = set(goal_lower.split())

        # 检查行动中是否包含目标关键词
        matched_keywords = sum(1 for kw in goal_keywords if kw in action_lower)
        keyword_score = matched_keywords / len(goal_keywords) if goal_keywords else 0.0
        score += keyword_score * 0.4

        # 步骤关联
        # 检查当前行动是否与目标关联的步骤相关
        step_score = 0.0
        for step_id in goal.steps:
            if step_id in self._steps:
                step = self._steps[step_id]
                if step.step_name.lower() in action_lower:
                    step_score = 1.0
                    break
        score += step_score * 0.3

        # 成功标准匹配
        criteria_score = 0.0
        for criteria in goal.success_criteria:
            if criteria.lower() in action_lower:
                criteria_score = 1.0
                break
        score += criteria_score * 0.3

        return min(1.0, score)

    def _generate_alignment_reason(
        self,
        current_action: str,
        goal: TaskGoal,
        alignment_score: float,
    ) -> str:
        """生成对齐原因分析"""
        if alignment_score >= 0.8:
            return f"当前行动 '{current_action}' 与目标 '{goal.goal_name}' 高度相关"
        elif alignment_score >= 0.5:
            return f"当前行动 '{current_action}' 与目标 '{goal.goal_name}' 部分相关"
        elif alignment_score >= 0.3:
            return f"当前行动 '{current_action}' 与目标 '{goal.goal_name}' 关联度较低"
        else:
            return f"当前行动 '{current_action}' 与目标 '{goal.goal_name}' 无明显关联"

    def _generate_alignment_suggestions(
        self,
        current_action: str,
        goal: TaskGoal,
        alignment_level: AlignmentLevel,
    ) -> list[str]:
        """生成对齐建议"""
        suggestions: list[str] = []

        if alignment_level == AlignmentLevel.LOW:
            suggestions.append(f"建议聚焦于目标 '{goal.goal_name}' 的核心任务")
            suggestions.append("考虑暂停当前行动，优先处理目标相关步骤")

        elif alignment_level == AlignmentLevel.MISALIGNED:
            suggestions.append("当前行动与目标不符，建议重新评估")
            suggestions.append(f"目标成功标准: {', '.join(goal.success_criteria) or '未定义'}")

        return suggestions

    # -----------------------------------------------------------------------
    # 辅助方法
    # -----------------------------------------------------------------------

    def _update_phase(self, step: TaskStep) -> None:
        """更新阶段"""
        phase_mapping = {
            StepType.ANALYSIS: PhaseType.EXPLORATION,
            StepType.PLANNING: PhaseType.DESIGN,
            StepType.EXECUTION: PhaseType.IMPLEMENTATION,
            StepType.VERIFICATION: PhaseType.VERIFICATION,
            StepType.REFINEMENT: PhaseType.REFINEMENT,
        }

        new_phase = phase_mapping.get(step.step_type)
        if new_phase:
            self._current_phase = new_phase

    def _unblock_dependents(self, step_id: str) -> None:
        """解除依赖步骤的阻塞"""
        if step_id not in self._steps:
            return

        step = self._steps[step_id]

        for dep_id in step.dependents:
            if dep_id in self._steps:
                dep_step = self._steps[dep_id]
                if dep_step.status == StepStatus.BLOCKED:
                    # 检查所有依赖是否完成
                    all_deps_done = all(
                        self._steps[d].status in [StepStatus.COMPLETED, StepStatus.SKIPPED]
                        for d in dep_step.dependencies
                        if d in self._steps
                    )
                    if all_deps_done:
                        dep_step.status = StepStatus.PENDING
                        dep_step.metadata.pop("blocked_by", None)

    def _update_goal_progress(self) -> None:
        """更新目标进度"""
        for goal in self._goals.values():
            if goal.status != GoalStatus.IN_PROGRESS:
                continue

            # 检查关联步骤是否全部完成
            all_steps_done = all(
                self._steps[step_id].status == StepStatus.COMPLETED
                for step_id in goal.steps
                if step_id in self._steps
            )

            if all_steps_done and goal.steps:
                goal.status = GoalStatus.ACHIEVED
                goal.achieved_at = datetime.now()

    def _persist_state(self) -> None:
        """持久化状态到 Redis"""
        if not self._redis:
            return

        try:
            # 存储步骤
            for step_id, step in self._steps.items():
                key = f"task_progress:{self._task_id}:step:{step_id}"
                self._redis.set(key, step.model_dump_json(), ex=86400)  # 1天过期

            # 存储目标
            for goal_id, goal in self._goals.items():
                key = f"task_progress:{self._task_id}:goal:{goal_id}"
                self._redis.set(key, goal.model_dump_json(), ex=86400)

        except Exception:
            pass  # 静默失败，不影响主流程

    # -----------------------------------------------------------------------
    # 状态查询
    # -----------------------------------------------------------------------

    def get_step(self, step_id: str) -> TaskStep | None:
        """获取步骤"""
        return self._steps.get(step_id)

    def get_all_steps(self) -> list[TaskStep]:
        """获取所有步骤"""
        return list(self._steps.values())

    def get_current_step(self) -> TaskStep | None:
        """获取当前步骤"""
        if self._current_step_id:
            return self._steps.get(self._current_step_id)
        return None

    def get_current_phase(self) -> PhaseType:
        """获取当前阶段"""
        return self._current_phase


# ============================================================================
# 工厂函数
# ============================================================================


def create_task_progress_tracker(
    task_id: str,
    task_name: str,
    redis_host: str = "localhost",
    redis_port: int = 6379,
) -> TaskProgressTracker:
    """
    创建任务进度追踪器

    Args:
        task_id: 任务ID
        task_name: 任务名称
        redis_host: Redis 主机
        redis_port: Redis 端口

    Returns:
        TaskProgressTracker 实例
    """
    from .redis_adapter import create_redis_adapter

    redis_adapter = create_redis_adapter(host=redis_host, port=redis_port)

    return TaskProgressTracker(
        task_id=task_id,
        task_name=task_name,
        redis_adapter=redis_adapter,
    )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "StepStatus",
    "StepType",
    "GoalStatus",
    "AlignmentLevel",
    "TaskStep",
    "TaskGoal",
    "StepDependency",
    "ProgressReport",
    "GoalAlignmentCheck",
    "TaskProgressConfig",
    "TaskProgressTracker",
    "create_task_progress_tracker",
]

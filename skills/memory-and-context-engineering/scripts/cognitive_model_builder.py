"""
Agent Memory System - Cognitive Model Builder（认知模型构建器）

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
将原始信息组织成模型可高效理解和推理的认知结构。
不是压缩信息，而是构建"模型需要知道的世界"。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class StepResult(str, Enum):
    """步骤结果"""

    SUCCESS = "success"          # 成功
    FAILURE = "failure"          # 失败
    IN_PROGRESS = "in_progress"  # 进行中
    SKIPPED = "skipped"          # 跳过
    BLOCKED = "blocked"          # 阻塞


class FactSource(str, Enum):
    """事实来源"""

    MEMORY = "memory"            # 来自记忆
    RETRIEVAL = "retrieval"      # 来自检索
    TOOL = "tool"                # 来自工具返回
    USER = "user"                # 来自用户输入
    INFERENCE = "inference"      # 来自推理


class ConstraintType(str, Enum):
    """约束类型"""

    MUST_USE = "must_use"        # 必须使用
    MUST_AVOID = "must_avoid"    # 禁止使用
    PREFERENCE = "preference"    # 用户偏好
    RESOURCE = "resource"        # 资源限制
    PERMISSION = "permission"    # 权限约束


class GapImportance(str, Enum):
    """知识缺口重要程度"""

    CRITICAL = "critical"        # 关键：必须补充
    HIGH = "high"                # 高：强烈建议补充
    MEDIUM = "medium"            # 中：建议补充
    LOW = "low"                  # 低：可选补充


class DecisionStatus(str, Enum):
    """决策状态"""

    PENDING = "pending"          # 待决策
    MADE = "made"                # 已决策
    REVISED = "revised"          # 已修订
    DEFERRED = "deferred"        # 已推迟


# ============================================================================
# 数据模型
# ============================================================================


class TaskContext(BaseModel):
    """任务上下文 - 模型需要知道的"我在哪里、我要去哪里" """

    # 目标层
    goal: str = Field(description="最终目标")
    sub_goals: list[str] = Field(default_factory=list, description="子目标列表")
    success_criteria: list[str] = Field(default_factory=list, description="成功条件")

    # 进度层
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="进度百分比")
    current_phase: str = Field(default="exploration", description="当前阶段")
    current_focus: str = Field(default="", description="当前焦点")

    # 元数据
    session_id: str = Field(default="", description="会话ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PathStep(BaseModel):
    """路径步骤 - 模型需要知道的"我怎么走到这里" """

    step_id: str
    description: str = Field(description="步骤描述")
    result: StepResult = Field(default=StepResult.IN_PROGRESS, description="执行结果")
    key_findings: list[str] = Field(default_factory=list, description="关键发现")
    lessons_learned: list[str] = Field(default_factory=list, description="经验教训")
    timestamp: datetime = Field(default_factory=datetime.now)

    # 关联信息
    related_tools: list[str] = Field(default_factory=list, description="使用的工具")
    dependencies: list[str] = Field(default_factory=list, description="依赖的步骤")


class Constraint(BaseModel):
    """约束条件 - 模型需要知道的"边界" """

    constraint_type: ConstraintType
    content: str = Field(description="约束内容")
    source: str = Field(default="", description="约束来源")
    priority: int = Field(default=1, ge=1, le=10, description="优先级")
    negotiable: bool = Field(default=True, description="是否可协商")


class ConstraintSet(BaseModel):
    """约束集"""

    must_use: list[str] = Field(default_factory=list, description="必须使用的工具/方法")
    must_avoid: list[str] = Field(default_factory=list, description="禁止使用的内容")
    user_preferences: list[str] = Field(default_factory=list, description="用户偏好")
    resource_limits: dict[str, Any] = Field(default_factory=dict, description="资源限制")
    permission_constraints: list[str] = Field(default_factory=list, description="权限约束")

    def add_constraint(self, constraint: Constraint) -> None:
        """添加约束"""
        if constraint.constraint_type == ConstraintType.MUST_USE:
            self.must_use.append(constraint.content)
        elif constraint.constraint_type == ConstraintType.MUST_AVOID:
            self.must_avoid.append(constraint.content)
        elif constraint.constraint_type == ConstraintType.PREFERENCE:
            self.user_preferences.append(constraint.content)
        elif constraint.constraint_type == ConstraintType.RESOURCE:
            self.resource_limits[constraint.content] = constraint.priority
        elif constraint.constraint_type == ConstraintType.PERMISSION:
            self.permission_constraints.append(constraint.content)


class Fact(BaseModel):
    """事实 - 模型需要知道的"我知道什么" """

    fact_id: str = Field(
        default_factory=lambda: f"fact_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    content: str = Field(description="事实内容")
    source: FactSource = Field(default=FactSource.MEMORY, description="事实来源")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度")
    verified: bool = Field(default=False, description="是否已验证")
    verification_method: str | None = Field(default=None, description="验证方式")

    # 关联信息
    related_concepts: list[str] = Field(default_factory=list, description="相关概念")
    created_at: datetime = Field(default_factory=datetime.now)


class Hypothesis(BaseModel):
    """假设 - 模型需要知道的"我假设什么" """

    hypothesis_id: str = Field(
        default_factory=lambda: f"hyp_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    content: str = Field(description="假设内容")
    verification_method: str = Field(description="验证方式")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="当前置信度")
    evidence_for: list[str] = Field(default_factory=list, description="支持证据")
    evidence_against: list[str] = Field(default_factory=list, description="反对证据")
    created_at: datetime = Field(default_factory=datetime.now)


class KnowledgeGap(BaseModel):
    """知识缺口 - 模型需要知道的"我不知道什么" """

    gap_id: str = Field(
        default_factory=lambda: f"gap_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    description: str = Field(description="缺口描述")
    importance: GapImportance = Field(default=GapImportance.MEDIUM, description="重要程度")
    suggested_source: str = Field(default="", description="建议补充来源")
    suggested_query: str = Field(default="", description="建议的检索查询")
    blocking: bool = Field(default=False, description="是否阻塞当前任务")
    created_at: datetime = Field(default_factory=datetime.now)


class DecisionOption(BaseModel):
    """决策选项"""

    option_id: str
    description: str
    pros: list[str] = Field(default_factory=list, description="优点")
    cons: list[str] = Field(default_factory=list, description="缺点")
    estimated_impact: str = Field(default="", description="预估影响")


class DecisionPoint(BaseModel):
    """决策点 - 模型需要知道的"我需要决定什么" """

    decision_id: str = Field(
        default_factory=lambda: f"dec_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    decision: str = Field(description="决策内容")
    options: list[DecisionOption] = Field(default_factory=list, description="可选项")
    criteria: list[str] = Field(default_factory=list, description="决策依据")
    status: DecisionStatus = Field(default=DecisionStatus.PENDING, description="决策状态")
    selected_option: str | None = Field(default=None, description="已选选项")
    rationale: str | None = Field(default=None, description="决策理由")
    impact: str | None = Field(default=None, description="决策影响")
    created_at: datetime = Field(default_factory=datetime.now)


class CausalChain(BaseModel):
    """因果链 - 模型需要知道的"因果关系" """

    chain_id: str = Field(
        default_factory=lambda: f"chain_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    problem: str = Field(description="问题/现象")
    causes: list[str] = Field(default_factory=list, description="原因列表")
    solutions: list[str] = Field(default_factory=list, description="解决方案")
    evidence: list[str] = Field(default_factory=list, description="证据链")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="置信度")

    # 多层级因果
    sub_chains: list["CausalChain"] = Field(default_factory=list, description="子因果链")
    created_at: datetime = Field(default_factory=datetime.now)


class CognitiveModel(BaseModel):
    """
    认知模型 - 模型可高效理解和推理的结构

    核心理念：将原始信息组织成模型能高效理解和推理的样子
    """

    # 任务上下文
    task_context: TaskContext = Field(default_factory=TaskContext)

    # 已完成路径
    completed_path: list[PathStep] = Field(default_factory=list)

    # 当前约束
    constraints: ConstraintSet = Field(default_factory=ConstraintSet)

    # 已知事实
    known_facts: list[Fact] = Field(default_factory=list)

    # 待验证假设
    hypotheses: list[Hypothesis] = Field(default_factory=list)

    # 知识缺口
    knowledge_gaps: list[KnowledgeGap] = Field(default_factory=list)

    # 待决策事项
    pending_decisions: list[DecisionPoint] = Field(default_factory=list)

    # 因果链
    causal_chains: list[CausalChain] = Field(default_factory=list)

    # 建议下一步
    suggested_next_step: str | None = Field(default=None)

    # 元数据
    model_id: str = Field(
        default_factory=lambda: f"cog_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_context_string(self) -> str:
        """
        转换为模型可直接使用的上下文字符串

        这是核心方法：将结构化认知模型转化为模型可理解的格式
        """
        sections: list[str] = []

        # 任务上下文
        sections.append("## 当前认知状态\n")
        sections.append("### 任务上下文")
        sections.append(f"- 目标: {self.task_context.goal}")
        if self.task_context.sub_goals:
            sections.append(f"- 子目标: {', '.join(self.task_context.sub_goals)}")
        sections.append(f"- 进度: {self.task_context.progress_percentage:.0f}% - {self.task_context.current_phase}")
        if self.task_context.current_focus:
            sections.append(f"- 当前焦点: {self.task_context.current_focus}")
        sections.append("")

        # 已完成路径
        if self.completed_path:
            sections.append("### 已完成路径")
            for i, step in enumerate(self.completed_path, 1):
                result_icon = {"success": "✓", "failure": "✗", "in_progress": "→"}.get(
                    step.result.value, "?"
                )
                sections.append(f"{i}. {step.description} {result_icon}")
                if step.key_findings:
                    for finding in step.key_findings:
                        sections.append(f"   - 发现: {finding}")
                if step.lessons_learned:
                    for lesson in step.lessons_learned:
                        sections.append(f"   - 教训: {lesson}")
            sections.append("")

        # 当前约束
        has_constraints = (
            self.constraints.must_use
            or self.constraints.must_avoid
            or self.constraints.user_preferences
            or self.constraints.permission_constraints
        )
        if has_constraints:
            sections.append("### 当前约束")
            if self.constraints.must_use:
                sections.append(f"- 必须使用: {', '.join(self.constraints.must_use)}")
            if self.constraints.must_avoid:
                sections.append(f"- 禁止使用: {', '.join(self.constraints.must_avoid)}")
            if self.constraints.user_preferences:
                sections.append(f"- 用户偏好: {', '.join(self.constraints.user_preferences)}")
            if self.constraints.permission_constraints:
                sections.append(f"- 权限限制: {', '.join(self.constraints.permission_constraints)}")
            sections.append("")

        # 已知事实
        if self.known_facts:
            sections.append("### 已知事实")
            for fact in self.known_facts:
                verified_mark = "✓" if fact.verified else "?"
                sections.append(f"- {fact.content} [{fact.source.value}] {verified_mark}")
            sections.append("")

        # 待验证假设
        if self.hypotheses:
            sections.append("### 待验证假设")
            for hyp in self.hypotheses:
                sections.append(f"- {hyp.content}")
                sections.append(f"  验证方式: {hyp.verification_method}")
                sections.append(f"  置信度: {hyp.confidence:.0%}")
            sections.append("")

        # 知识缺口
        if self.knowledge_gaps:
            sections.append("### 知识缺口")
            for gap in self.knowledge_gaps:
                blocking_mark = "⚠️" if gap.blocking else ""
                sections.append(f"- {gap.description} [{gap.importance.value}] {blocking_mark}")
                if gap.suggested_query:
                    sections.append(f"  建议检索: {gap.suggested_query}")
            sections.append("")

        # 待决策事项
        if self.pending_decisions:
            sections.append("### 待决策事项")
            for dec in self.pending_decisions:
                sections.append(f"- {dec.decision} [{dec.status.value}]")
                if dec.options:
                    sections.append(f"  选项: {', '.join(o.description for o in dec.options)}")
            sections.append("")

        # 因果链
        if self.causal_chains:
            sections.append("### 因果分析")
            for chain in self.causal_chains:
                sections.append(f"- 问题: {chain.problem}")
                if chain.causes:
                    sections.append(f"  原因: {', '.join(chain.causes)}")
                if chain.solutions:
                    sections.append(f"  解决: {', '.join(chain.solutions)}")
            sections.append("")

        # 建议下一步
        if self.suggested_next_step:
            sections.append("### 建议下一步")
            sections.append(self.suggested_next_step)

        return "\n".join(sections)


# ============================================================================
# Cognitive Model Builder
# ============================================================================


class CognitiveModelBuilder:
    """
    认知模型构建器

    职责：
    - 将原始信息组织成模型可高效理解和推理的认知结构
    - 整合来自各模块的信息
    - 输出结构化认知模型

    使用示例：
    ```python
    from scripts.cognitive_model_builder import CognitiveModelBuilder

    builder = CognitiveModelBuilder()

    # 设置任务上下文
    builder.set_task_context(
        goal="实现用户登录功能",
        sub_goals=["数据库设计", "前端表单", "后端验证"],
        current_focus="后端验证逻辑",
    )

    # 添加已完成步骤
    builder.add_completed_step(
        description="设计数据库用户表",
        result="success",
        key_findings=["使用bcrypt加密"],
    )

    # 添加约束
    builder.add_constraint("must_use", "bcrypt加密")
    builder.add_constraint("must_avoid", "明文存储密码")

    # 添加知识缺口
    builder.add_knowledge_gap(
        description="SSO集成方案",
        importance="high",
        suggested_query="如何实现OAuth2 SSO登录",
    )

    # 构建认知模型
    model = builder.build()

    # 输出模型可理解的上下文
    print(model.to_context_string())
    ```
    """

    def __init__(self, session_id: str = ""):
        """初始化认知模型构建器"""
        self._task_context = TaskContext(session_id=session_id)
        self._completed_path: list[PathStep] = []
        self._constraints = ConstraintSet()
        self._known_facts: list[Fact] = []
        self._hypotheses: list[Hypothesis] = []
        self._knowledge_gaps: list[KnowledgeGap] = []
        self._pending_decisions: list[DecisionPoint] = []
        self._causal_chains: list[CausalChain] = []
        self._suggested_next_step: str | None = None

    # -----------------------------------------------------------------------
    # 任务上下文
    # -----------------------------------------------------------------------

    def set_task_context(
        self,
        goal: str,
        sub_goals: list[str] | None = None,
        success_criteria: list[str] | None = None,
        progress_percentage: float = 0.0,
        current_phase: str = "exploration",
        current_focus: str = "",
    ) -> None:
        """设置任务上下文"""
        self._task_context = TaskContext(
            goal=goal,
            sub_goals=sub_goals or [],
            success_criteria=success_criteria or [],
            progress_percentage=progress_percentage,
            current_phase=current_phase,
            current_focus=current_focus,
            session_id=self._task_context.session_id,
        )

    def update_progress(
        self,
        percentage: float,
        phase: str | None = None,
        focus: str | None = None,
    ) -> None:
        """更新进度"""
        self._task_context.progress_percentage = percentage
        if phase:
            self._task_context.current_phase = phase
        if focus:
            self._task_context.current_focus = focus
        self._task_context.updated_at = datetime.now()

    # -----------------------------------------------------------------------
    # 路径步骤
    # -----------------------------------------------------------------------

    def add_completed_step(
        self,
        description: str,
        result: StepResult | str = StepResult.SUCCESS,
        key_findings: list[str] | None = None,
        lessons_learned: list[str] | None = None,
        related_tools: list[str] | None = None,
    ) -> str:
        """添加已完成步骤"""
        if isinstance(result, str):
            result = StepResult(result)

        step = PathStep(
            step_id=f"step_{len(self._completed_path) + 1}",
            description=description,
            result=result,
            key_findings=key_findings or [],
            lessons_learned=lessons_learned or [],
            related_tools=related_tools or [],
        )
        self._completed_path.append(step)
        return step.step_id

    # -----------------------------------------------------------------------
    # 约束管理
    # -----------------------------------------------------------------------

    def add_constraint(
        self,
        constraint_type: ConstraintType | str,
        content: str,
        source: str = "",
        priority: int = 1,
    ) -> None:
        """添加约束"""
        if isinstance(constraint_type, str):
            constraint_type = ConstraintType(constraint_type)

        constraint = Constraint(
            constraint_type=constraint_type,
            content=content,
            source=source,
            priority=priority,
        )
        self._constraints.add_constraint(constraint)

    # -----------------------------------------------------------------------
    # 事实管理
    # -----------------------------------------------------------------------

    def add_fact(
        self,
        content: str,
        source: FactSource | str = FactSource.MEMORY,
        confidence: float = 1.0,
        verified: bool = False,
    ) -> str:
        """添加已知事实"""
        if isinstance(source, str):
            source = FactSource(source)

        fact = Fact(
            content=content,
            source=source,
            confidence=confidence,
            verified=verified,
        )
        self._known_facts.append(fact)
        return fact.fact_id

    # -----------------------------------------------------------------------
    # 假设管理
    # -----------------------------------------------------------------------

    def add_hypothesis(
        self,
        content: str,
        verification_method: str,
        confidence: float = 0.5,
        evidence_for: list[str] | None = None,
        evidence_against: list[str] | None = None,
    ) -> str:
        """添加假设"""
        hypothesis = Hypothesis(
            content=content,
            verification_method=verification_method,
            confidence=confidence,
            evidence_for=evidence_for or [],
            evidence_against=evidence_against or [],
        )
        self._hypotheses.append(hypothesis)
        return hypothesis.hypothesis_id

    # -----------------------------------------------------------------------
    # 知识缺口管理
    # -----------------------------------------------------------------------

    def add_knowledge_gap(
        self,
        description: str,
        importance: GapImportance | str = GapImportance.MEDIUM,
        suggested_source: str = "",
        suggested_query: str = "",
        blocking: bool = False,
    ) -> str:
        """添加知识缺口"""
        if isinstance(importance, str):
            importance = GapImportance(importance)

        gap = KnowledgeGap(
            description=description,
            importance=importance,
            suggested_source=suggested_source,
            suggested_query=suggested_query,
            blocking=blocking,
        )
        self._knowledge_gaps.append(gap)
        return gap.gap_id

    # -----------------------------------------------------------------------
    # 决策管理
    # -----------------------------------------------------------------------

    def add_decision_point(
        self,
        decision: str,
        options: list[dict[str, Any]] | None = None,
        criteria: list[str] | None = None,
    ) -> str:
        """添加决策点"""
        decision_options = []
        if options:
            for i, opt in enumerate(options):
                decision_options.append(DecisionOption(
                    option_id=f"opt_{i + 1}",
                    description=opt.get("description", ""),
                    pros=opt.get("pros", []),
                    cons=opt.get("cons", []),
                    estimated_impact=opt.get("impact", ""),
                ))

        dp = DecisionPoint(
            decision=decision,
            options=decision_options,
            criteria=criteria or [],
        )
        self._pending_decisions.append(dp)
        return dp.decision_id

    def make_decision(
        self,
        decision_id: str,
        selected_option: str,
        rationale: str,
    ) -> bool:
        """做出决策"""
        for dp in self._pending_decisions:
            if dp.decision_id == decision_id:
                dp.status = DecisionStatus.MADE
                dp.selected_option = selected_option
                dp.rationale = rationale
                return True
        return False

    # -----------------------------------------------------------------------
    # 因果链管理
    # -----------------------------------------------------------------------

    def add_causal_chain(
        self,
        problem: str,
        causes: list[str],
        solutions: list[str] | None = None,
        evidence: list[str] | None = None,
        confidence: float = 0.5,
    ) -> str:
        """添加因果链"""
        chain = CausalChain(
            problem=problem,
            causes=causes,
            solutions=solutions or [],
            evidence=evidence or [],
            confidence=confidence,
        )
        self._causal_chains.append(chain)
        return chain.chain_id

    # -----------------------------------------------------------------------
    # 建议下一步
    # -----------------------------------------------------------------------

    def set_suggested_next_step(self, suggestion: str) -> None:
        """设置建议的下一步"""
        self._suggested_next_step = suggestion

    def infer_next_step(self) -> str:
        """推断下一步"""
        # 基于当前状态推断
        if self._knowledge_gaps:
            critical_gaps = [
                g for g in self._knowledge_gaps
                if g.importance == GapImportance.CRITICAL or g.blocking
            ]
            if critical_gaps:
                return f"补充关键知识缺口: {critical_gaps[0].description}"

        if self._pending_decisions:
            pending = [
                d for d in self._pending_decisions
                if d.status == DecisionStatus.PENDING
            ]
            if pending:
                return f"需要决策: {pending[0].decision}"

        if self._task_context.current_focus:
            return f"继续: {self._task_context.current_focus}"

        return "推进任务进度"

    # -----------------------------------------------------------------------
    # 构建认知模型
    # -----------------------------------------------------------------------

    def build(self) -> CognitiveModel:
        """构建认知模型"""
        # 如果没有设置建议下一步，自动推断
        if self._suggested_next_step is None:
            self._suggested_next_step = self.infer_next_step()

        return CognitiveModel(
            task_context=self._task_context,
            completed_path=self._completed_path.copy(),
            constraints=self._constraints,
            known_facts=self._known_facts.copy(),
            hypotheses=self._hypotheses.copy(),
            knowledge_gaps=self._knowledge_gaps.copy(),
            pending_decisions=self._pending_decisions.copy(),
            causal_chains=self._causal_chains.copy(),
            suggested_next_step=self._suggested_next_step,
        )

    # -----------------------------------------------------------------------
    # 从其他模块导入
    # -----------------------------------------------------------------------

    def import_from_task_progress(self, task_progress: Any) -> None:
        """从 TaskProgressTracker 导入"""
        # 导入目标
        if hasattr(task_progress, "_goals"):
            for goal_id, goal in task_progress._goals.items():
                self._task_context.goal = goal.name
                self._task_context.success_criteria = goal.success_criteria

        # 导入进度
        if hasattr(task_progress, "get_progress_report"):
            report = task_progress.get_progress_report()
            self._task_context.progress_percentage = report.completion_rate * 100
            self._task_context.current_phase = report.current_phase.value

        # 导入步骤
        if hasattr(task_progress, "_steps"):
            for step_id, step in task_progress._steps.items():
                result = StepResult.SUCCESS if step.status.value == "completed" else StepResult.IN_PROGRESS
                self.add_completed_step(
                    description=step.name,
                    result=result,
                    key_findings=[step.result] if step.result else [],
                )

    def import_from_memory(self, memories: list[Any]) -> None:
        """从长期记忆导入"""
        for memory in memories:
            # 提取事实
            if hasattr(memory, "content"):
                self.add_fact(
                    content=memory.content,
                    source=FactSource.MEMORY,
                    confidence=getattr(memory, "confidence", 0.8),
                )


# ============================================================================
# 工厂函数
# ============================================================================


def create_cognitive_model(session_id: str = "") -> CognitiveModel:
    """创建空白认知模型"""
    return CognitiveModel(task_context=TaskContext(session_id=session_id))


def create_cognitive_builder(session_id: str = "") -> CognitiveModelBuilder:
    """创建认知模型构建器"""
    return CognitiveModelBuilder(session_id=session_id)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    # 枚举
    "StepResult",
    "FactSource",
    "ConstraintType",
    "GapImportance",
    "DecisionStatus",
    # 数据模型
    "TaskContext",
    "PathStep",
    "Constraint",
    "ConstraintSet",
    "Fact",
    "Hypothesis",
    "KnowledgeGap",
    "DecisionOption",
    "DecisionPoint",
    "CausalChain",
    "CognitiveModel",
    # 构建器
    "CognitiveModelBuilder",
    # 工厂函数
    "create_cognitive_model",
    "create_cognitive_builder",
]

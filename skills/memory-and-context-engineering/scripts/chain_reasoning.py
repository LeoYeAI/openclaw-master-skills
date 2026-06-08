"""
Agent Memory System - 链式推理增强模块

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

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

from .types import (
    LearningValue,
    MemoryCategory,
    MetaLearningSample,
    ReasoningStepWithReflection,
    ReflectionMemoryItem,
    ReflectionOutcome,
    ReflectionProcessResult,
    ReflectionSeverity,
    ReflectionSignal,
    ReflectionTriggerRecord,
    ReflectionTriggerType,
    VerificationResult,
)

if TYPE_CHECKING:
    from .state_capture import GlobalStateCapture
    from .short_term import ShortTermMemoryManager
    from .long_term import LongTermMemoryManager


# ============================================================================
# 配置常量
# ============================================================================

DEFAULT_CONFIG: dict[str, Any] = {
    "max_rollback_count": 3,
    "verification_threshold": 0.7,
    "learning_value_threshold": LearningValue.MEDIUM,
    "meta_learning_sample_limit": 100,
}


# ============================================================================
# 链式推理增强器（主类）
# ============================================================================


class ChainReasoningEnhancer:
    """
    链式推理增强模块

    设计原则：
    1. 反思检测由模型自身完成（通过输出信号）
    2. 反思结果持久化到长期记忆
    3. 仅在恰当时机介入，不影响推理效率

    与 LangGraph 集成方式：
    - 作为可选节点嵌入推理流程
    - 通过条件边判断是否执行
    - 回退时利用 GlobalStateCapture 的检查点机制

    使用示例：
    ```python
    from scripts.chain_reasoning import ChainReasoningEnhancer
    from scripts.state_capture import GlobalStateCapture
    from scripts.short_term import ShortTermMemoryManager
    from scripts.long_term import LongTermMemoryManager

    # 初始化
    enhancer = ChainReasoningEnhancer(
        state_capture=capture,
        short_term=short_term,
        long_term=long_term,
    )

    # 处理推理步骤（带反思信号）
    result = enhancer.process_reasoning_step(
        step=reasoning_step,
        step_index=12,
    )

    if result["should_reflect"]:
        # 执行反思
        reflection_result = enhancer.execute_reflection(
            signal=result["signal"],
            context_snapshot=result["context_snapshot"],
        )

        if not reflection_result.passed:
            # 处理反思失败
            pass
    ```
    """

    def __init__(
        self,
        state_capture: "GlobalStateCapture",
        short_term: "ShortTermMemoryManager",
        long_term: "LongTermMemoryManager",
        config: dict[str, Any] | None = None,
    ) -> None:
        """
        初始化链式推理增强器

        Args:
            state_capture: 全局状态捕捉器
            short_term: 短期记忆管理器
            long_term: 长期记忆管理器
            config: 配置参数
        """
        self._state_capture = state_capture
        self._short_term = short_term
        self._long_term = long_term
        self._config = {**DEFAULT_CONFIG, **(config or {})}

        # 回退计数器
        self._rollback_count: int = 0
        self._tried_paths: set[str] = set()

    # ========================================================================
    # 核心方法：处理推理步骤
    # ========================================================================

    def process_reasoning_step(
        self,
        step: dict[str, Any] | ReasoningStepWithReflection,
        step_index: int,
        task_type: str = "unknown",
    ) -> dict[str, Any]:
        """
        处理带反思信号的推理步骤

        Args:
            step: 推理步骤（字典或模型）
            step_index: 步骤索引
            task_type: 任务类型

        Returns:
            {
                "should_reflect": bool,
                "signal": ReflectionSignal,
                "context_snapshot": dict,
                "trigger_record": ReflectionTriggerRecord,
            }
        """
        # 提取反思信号
        signal = self._extract_reflection_signal(step)

        # 捕获状态快照
        context_snapshot = self._capture_context_snapshot()

        result: dict[str, Any] = {
            "should_reflect": signal.need_reflect,
            "signal": signal,
            "context_snapshot": context_snapshot,
            "trigger_record": None,
        }

        # 如果需要反思，创建触发记录
        if signal.need_reflect:
            trigger_record = ReflectionTriggerRecord(
                trigger_type=ReflectionTriggerType.SELF_DETECTED,
                trigger_reason=signal.reflect_reason or "模型自检测",
                trigger_confidence=signal.reflect_confidence or 0.5,
                step_index=step_index,
                task_type=task_type,
                context_snapshot=context_snapshot,
            )

            # 存储到短期记忆
            self._store_trigger_record(trigger_record)

            result["trigger_record"] = trigger_record

        return result

    # ========================================================================
    # 反思执行
    # ========================================================================

    def execute_reflection(
        self,
        signal: ReflectionSignal,
        context_snapshot: dict[str, Any],
        reasoning_context: list[dict[str, Any]] | None = None,
    ) -> ReflectionProcessResult:
        """
        执行反思过程

        Args:
            signal: 反思信号
            context_snapshot: 状态快照
            reasoning_context: 推理上下文（可选）

        Returns:
            ReflectionProcessResult
        """
        # 获取推理上下文
        if reasoning_context is None:
            reasoning_context = self._get_recent_reasoning()

        # 分析反思原因，确定严重程度
        severity = self._assess_severity(signal, reasoning_context)

        # 检测具体问题
        issues = self._detect_issues(signal, reasoning_context, context_snapshot)

        # 生成修正建议
        suggestion = self._generate_suggestion(issues, severity)

        # 判断是否需要验证
        need_verification = self._should_trigger_verification(
            severity, context_snapshot
        )

        return ReflectionProcessResult(
            passed=len(issues) == 0,
            issues=issues,
            severity=severity,
            suggestion=suggestion,
            need_verification=need_verification,
        )

    # ========================================================================
    # 验证执行
    # ========================================================================

    def execute_verification(
        self,
        reflection_result: ReflectionProcessResult,
        context_snapshot: dict[str, Any],
    ) -> VerificationResult:
        """
        执行验证过程

        Args:
            reflection_result: 反思结果
            context_snapshot: 状态快照

        Returns:
            VerificationResult
        """
        # 验证逻辑（可扩展）
        evidence: list[str] = []

        # 根据问题类型选择验证策略
        for issue in reflection_result.issues:
            if "矛盾" in issue:
                # 矛盾问题：收集证据
                evidence.append(f"检测到矛盾: {issue}")

            elif "置信度" in issue:
                # 低置信度问题：标记不确定
                evidence.append(f"低置信度: {issue}")

            else:
                # 其他问题：记录
                evidence.append(f"问题: {issue}")

        # 确定验证结果
        if len(evidence) == 0:
            result = "passed"
            resolution = None
        elif reflection_result.severity == ReflectionSeverity.CRITICAL:
            result = "failed"
            resolution = "需要回退并重新推理"
        else:
            result = "needs_review"
            resolution = reflection_result.suggestion

        return VerificationResult(
            triggered=True,
            result=result,
            resolution=resolution,
            evidence=evidence,
        )

    # ========================================================================
    # 回退管理
    # ========================================================================

    def handle_rollback(
        self,
        step_index: int,
        reason: str,
    ) -> dict[str, Any]:
        """
        处理回退逻辑

        Args:
            step_index: 当前步骤索引
            reason: 回退原因

        Returns:
            {
                "rollback_to": int,
                "checkpoint_id": str | None,
                "success": bool,
            }
        """
        # 检查回退限制
        if self._rollback_count >= self._config["max_rollback_count"]:
            return {
                "rollback_to": -1,
                "checkpoint_id": None,
                "success": False,
                "reason": "已达到最大回退次数",
            }

        # 生成路径键，避免重复回退
        path_key = f"{step_index}:{reason}"
        if path_key in self._tried_paths:
            return {
                "rollback_to": step_index - 2,  # 尝试更早的节点
                "checkpoint_id": None,
                "success": True,
                "reason": "避免重复路径",
            }

        self._tried_paths.add(path_key)
        self._rollback_count += 1

        # 获取最近的检查点
        checkpoints = self._state_capture.list_checkpoints(limit=5)

        if checkpoints:
            # 选择合适的检查点
            target_checkpoint = None
            for cp in checkpoints:
                # 选择比当前步骤早的检查点
                if cp.get("step_count", 0) < step_index:
                    target_checkpoint = cp
                    break

            if target_checkpoint:
                return {
                    "rollback_to": target_checkpoint.get("step_count", step_index - 1),
                    "checkpoint_id": target_checkpoint["checkpoint_id"],
                    "success": True,
                    "reason": f"回退到检查点 {target_checkpoint['checkpoint_id']}",
                }

        # 无合适检查点，返回上一步
        return {
            "rollback_to": max(0, step_index - 1),
            "checkpoint_id": None,
            "success": True,
            "reason": "无合适检查点，回退到上一步",
        }

    def reset_rollback_state(self) -> None:
        """重置回退状态（新任务开始时调用）"""
        self._rollback_count = 0
        self._tried_paths.clear()

    # ========================================================================
    # 反思结果持久化
    # ========================================================================

    def persist_reflection_result(
        self,
        trigger_record: ReflectionTriggerRecord,
        reflection_result: ReflectionProcessResult,
        verification_result: VerificationResult | None,
        final_outcome: ReflectionOutcome,
    ) -> str:
        """
        持久化反思结果到长期记忆

        Args:
            trigger_record: 触发记录
            reflection_result: 反思结果
            verification_result: 验证结果
            final_outcome: 最终结果

        Returns:
            memory_id
        """
        # 评估元学习价值
        learning_value = self._evaluate_learning_value(
            reflection_result, verification_result, final_outcome
        )

        # 构建反思记忆项
        memory_item = ReflectionMemoryItem(
            trigger_type=trigger_record.trigger_type,
            trigger_reason=trigger_record.trigger_reason,
            trigger_confidence=trigger_record.trigger_confidence,
            step_index=trigger_record.step_index,
            task_type=trigger_record.task_type,
            context_snapshot=trigger_record.context_snapshot,
            reflection_issues=reflection_result.issues,
            reflection_severity=reflection_result.severity,
            reflection_suggestion=reflection_result.suggestion,
            verification_triggered=verification_result is not None,
            verification_result=verification_result.result if verification_result else None,
            verification_resolution=verification_result.resolution if verification_result else None,
            outcome=final_outcome,
            learning_value=learning_value,
            user_id=self._state_capture.user_id,
            session_id=getattr(self._state_capture, "_thread_id", "unknown"),
        )

        # 存储到长期记忆
        return self._store_reflection_memory(memory_item)

    # ========================================================================
    # 元学习数据提取
    # ========================================================================

    def extract_meta_learning_data(
        self,
        min_learning_value: LearningValue = LearningValue.MEDIUM,
        limit: int = 100,
    ) -> list[MetaLearningSample]:
        """
        提取元学习训练数据

        Args:
            min_learning_value: 最小学习价值
            limit: 最大样本数

        Returns:
            用于训练模型"何时反思"的数据集
        """
        reflections = self._get_reflection_memories(limit=limit)

        # 过滤高价值样本
        value_order = {
            LearningValue.HIGH: 2,
            LearningValue.MEDIUM: 1,
            LearningValue.LOW: 0,
        }

        high_value = [
            r for r in reflections
            if value_order.get(r.get("learning_value"), 0) >= value_order.get(min_learning_value, 0)
        ]

        # 转换为训练格式
        training_data: list[MetaLearningSample] = []
        for r in high_value:
            sample = MetaLearningSample(
                sample_id=f"ml_{uuid.uuid4().hex[:8]}",
                context_snapshot=r.get("context_snapshot", {}),
                step_index=r.get("step_index", 0),
                task_type=r.get("task_type", "unknown"),
                recent_thoughts=[],  # 可扩展
                should_reflect=True,
                reflect_reason=r.get("trigger_reason"),
                reflect_confidence=r.get("trigger_confidence"),
                outcome=ReflectionOutcome(r.get("outcome", "confirmed")),
                was_correct=r.get("outcome") == ReflectionOutcome.CORRECTED.value,
            )
            training_data.append(sample)

        return training_data

    # ========================================================================
    # LangGraph 节点工厂方法
    # ========================================================================

    def as_reflection_node(
        self,
    ) -> Callable[[dict[str, Any]], dict[str, Any]]:
        """
        返回可嵌入 LangGraph 的反思节点函数

        使用示例：
        ```python
        enhancer = ChainReasoningEnhancer(...)
        workflow.add_node("reflection", enhancer.as_reflection_node())
        workflow.add_conditional_edges(
            "reasoning",
            lambda state: "reflect" if state.get("need_reflect") else "continue",
            {"reflect": "reflection", "continue": "next_node"}
        )
        ```

        Returns:
            LangGraph 节点函数
        """
        def reflection_node(state: dict[str, Any]) -> dict[str, Any]:
            # 提取反思信号
            signal = self._extract_reflection_signal(state)

            if not signal.need_reflect:
                return state

            # 执行反思
            context_snapshot = self._capture_context_snapshot()
            result = self.execute_reflection(signal, context_snapshot)

            # 更新状态
            state_updates: dict[str, Any] = {
                "reflection_result": result.model_dump(),
            }

            if result.need_verification:
                verification = self.execute_verification(result, context_snapshot)
                state_updates["verification_result"] = verification.model_dump()

                if verification.result == "failed":
                    state_updates["needs_rollback"] = True

            return {**state, **state_updates}

        return reflection_node

    def as_verification_node(
        self,
    ) -> Callable[[dict[str, Any]], dict[str, Any]]:
        """
        返回可嵌入 LangGraph 的验证节点函数

        Returns:
            LangGraph 节点函数
        """
        def verification_node(state: dict[str, Any]) -> dict[str, Any]:
            reflection_result = state.get("reflection_result")
            if not reflection_result:
                return state

            context_snapshot = self._capture_context_snapshot()
            result = self.execute_verification(
                ReflectionProcessResult(**reflection_result),
                context_snapshot,
            )

            state_updates: dict[str, Any] = {
                "verification_result": result.model_dump(),
            }

            if result.result == "failed":
                state_updates["needs_rollback"] = True

            return {**state, **state_updates}

        return verification_node

    # ========================================================================
    # 条件边辅助函数
    # ========================================================================

    @staticmethod
    def should_reflect(state: dict[str, Any]) -> str:
        """
        LangGraph 条件边：判断是否需要反思

        Args:
            state: LangGraph 状态

        Returns:
            节点名称
        """
        if state.get("need_reflect", False):
            return "reflection"
        return "continue"

    @staticmethod
    def should_verify(state: dict[str, Any]) -> str:
        """
        LangGraph 条件边：判断是否需要验证

        Args:
            state: LangGraph 状态

        Returns:
            节点名称
        """
        reflection_result = state.get("reflection_result", {})
        if reflection_result.get("need_verification", False):
            return "verification"
        elif reflection_result.get("passed", True):
            return "continue"
        else:
            return "rollback"

    @staticmethod
    def should_rollback(state: dict[str, Any]) -> str:
        """
        LangGraph 条件边：判断是否需要回退

        Args:
            state: LangGraph 状态

        Returns:
            节点名称
        """
        if state.get("needs_rollback", False):
            return "rollback"
        return "continue"

    # ========================================================================
    # 私有方法
    # ========================================================================

    def _extract_reflection_signal(
        self,
        step: dict[str, Any] | ReasoningStepWithReflection,
    ) -> ReflectionSignal:
        """从推理步骤中提取反思信号"""
        if isinstance(step, ReasoningStepWithReflection):
            return step.reflection_signal

        return ReflectionSignal(
            need_reflect=step.get("need_reflect", False),
            reflect_reason=step.get("reflect_reason"),
            reflect_confidence=step.get("reflect_confidence"),
        )

    def _capture_context_snapshot(self) -> dict[str, Any]:
        """捕获当前状态快照"""
        try:
            state = self._state_capture.get_current_state()
            return {
                "phase": state.get("phase"),
                "scenario": state.get("scenario"),
                "step_count": state.get("step_count"),
                "user_state": state.get("user_state"),
            }
        except Exception:
            return {}

    def _get_recent_reasoning(self) -> list[dict[str, Any]]:
        """获取最近推理上下文"""
        try:
            items = self._short_term.get_items(limit=10)
            return [
                {"content": item.content, "bucket_type": item.bucket_type.value}
                for item in items
            ]
        except Exception:
            return []

    def _assess_severity(
        self,
        signal: ReflectionSignal,
        reasoning_context: list[dict[str, Any]],
    ) -> ReflectionSeverity:
        """评估问题严重程度"""
        reason = signal.reflect_reason or ""

        # 关键词判断
        critical_keywords = ["错误", "矛盾", "冲突", "失败"]
        high_keywords = ["不确定", "可能", "似乎"]
        medium_keywords = ["需要", "应该", "考虑"]

        for keyword in critical_keywords:
            if keyword in reason:
                return ReflectionSeverity.CRITICAL

        for keyword in high_keywords:
            if keyword in reason:
                return ReflectionSeverity.HIGH

        for keyword in medium_keywords:
            if keyword in reason:
                return ReflectionSeverity.MEDIUM

        # 置信度判断
        if signal.reflect_confidence is not None:
            if signal.reflect_confidence >= 0.8:
                return ReflectionSeverity.HIGH
            elif signal.reflect_confidence >= 0.6:
                return ReflectionSeverity.MEDIUM

        return ReflectionSeverity.LOW

    def _detect_issues(
        self,
        signal: ReflectionSignal,
        reasoning_context: list[dict[str, Any]],
        context_snapshot: dict[str, Any],
    ) -> list[str]:
        """检测具体问题"""
        issues: list[str] = []
        reason = signal.reflect_reason or ""

        # 基于反思原因提取问题
        if "矛盾" in reason:
            issues.append("检测到信息矛盾")
        if "不确定" in reason:
            issues.append("推理置信度不足")
        if "遗漏" in reason:
            issues.append("可能遗漏关键信息")
        if "错误" in reason:
            issues.append("可能存在推理错误")

        return issues

    def _generate_suggestion(
        self,
        issues: list[str],
        severity: ReflectionSeverity,
    ) -> str | None:
        """生成修正建议"""
        if not issues:
            return None

        suggestions: list[str] = []

        for issue in issues:
            if "矛盾" in issue:
                suggestions.append("需要交叉验证矛盾信息")
            elif "置信度" in issue:
                suggestions.append("需要收集更多证据")
            elif "遗漏" in issue:
                suggestions.append("需要回顾之前的信息")
            elif "错误" in issue:
                suggestions.append("需要重新审视推理过程")

        return "; ".join(suggestions) if suggestions else None

    def _should_trigger_verification(
        self,
        severity: ReflectionSeverity,
        context: dict[str, Any],
    ) -> bool:
        """判断是否需要触发验证"""
        # 高严重程度需要验证
        if severity in [ReflectionSeverity.CRITICAL, ReflectionSeverity.HIGH]:
            return True

        # 高风险场景需要验证
        scenario = context.get("scenario", "")
        if scenario in ["financial", "legal", "medical", "debugging"]:
            return True

        return False

    def _evaluate_learning_value(
        self,
        reflection_result: ReflectionProcessResult,
        verification_result: VerificationResult | None,
        outcome: ReflectionOutcome,
    ) -> LearningValue:
        """评估元学习价值"""
        if outcome == ReflectionOutcome.CORRECTED:
            return LearningValue.HIGH
        elif outcome == ReflectionOutcome.FALSE_POSITIVE:
            return LearningValue.LOW
        elif outcome == ReflectionOutcome.CONFIRMED:
            return LearningValue.MEDIUM
        else:
            return LearningValue.LOW

    def _store_trigger_record(
        self,
        record: ReflectionTriggerRecord,
    ) -> str:
        """存储触发记录到短期记忆"""
        try:
            self._short_term.store_with_semantics(
                content=f"反思触发: {record.trigger_reason}",
                bucket_type=ReflectionSignal.__name__,  # 使用特殊标记
                topic_label="reflection_trigger",
                relevance_score=record.trigger_confidence,
            )
        except Exception:
            pass

        return record.record_id

    def _store_reflection_memory(
        self,
        item: ReflectionMemoryItem,
    ) -> str:
        """存储反思记忆到长期记忆"""
        try:
            # 使用长期记忆的扩展接口
            return self._long_term.store_reflection(item)
        except Exception:
            # 如果长期记忆不支持，返回临时ID
            return item.memory_id

    def _get_reflection_memories(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """获取反思记忆"""
        try:
            return self._long_term.get_memories_by_category(
                category=MemoryCategory.EXTENDED_REFLECTION.value,
                limit=limit,
            )
        except Exception:
            return []


# ============================================================================
# 工厂函数
# ============================================================================


def create_chain_reasoning_enhancer(
    state_capture: "GlobalStateCapture",
    short_term: "ShortTermMemoryManager",
    long_term: "LongTermMemoryManager",
    config: dict[str, Any] | None = None,
) -> ChainReasoningEnhancer:
    """
    创建链式推理增强器实例

    Args:
        state_capture: 全局状态捕捉器
        short_term: 短期记忆管理器
        long_term: 长期记忆管理器
        config: 配置参数

    Returns:
        ChainReasoningEnhancer 实例
    """
    return ChainReasoningEnhancer(
        state_capture=state_capture,
        short_term=short_term,
        long_term=long_term,
        config=config,
    )

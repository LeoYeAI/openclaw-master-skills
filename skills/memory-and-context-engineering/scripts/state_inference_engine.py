"""
Agent Memory System - State Inference Engine（状态推理引擎）

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
基于已知状态推理未知状态，填补信息缺口。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class InferenceType(str, Enum):
    """推理类型"""

    DEDUCTIVE = "deductive"        # 演绎推理
    INDUCTIVE = "inductive"        # 归纳推理
    ABDUCTIVE = "abductive"        # 溯因推理
    ANALOGICAL = "analogical"      # 类比推理


class InferenceConfidence(str, Enum):
    """推理置信度"""

    CERTAIN = "certain"            # 确定
    HIGH = "high"                  # 高
    MEDIUM = "medium"              # 中
    LOW = "low"                    # 低
    UNCERTAIN = "uncertain"        # 不确定


class InferenceSource(str, Enum):
    """推理来源"""

    PATTERN = "pattern"            # 模式匹配
    RULE = "rule"                  # 规则推导
    HEURISTIC = "heuristic"        # 启发式
    TEMPORAL = "temporal"          # 时序推断
    CONTEXTUAL = "contextual"      # 上下文推断


# ============================================================================
# 数据模型
# ============================================================================


class InferencePremise(BaseModel):
    """推理前提"""

    fact: str = Field(description="前提事实")
    source: str = Field(default="", description="事实来源")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class InferenceRule(BaseModel):
    """推理规则"""

    rule_id: str
    name: str = Field(description="规则名称")
    condition: str = Field(description="触发条件")
    conclusion: str = Field(description="结论模板")
    confidence_modifier: float = Field(default=0.9, ge=0.0, le=1.0)


class InferenceResult(BaseModel):
    """推理结果"""

    # 推理值
    inferred_value: Any
    inference_type: InferenceType = Field(default=InferenceType.DEDUCTIVE)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence_level: InferenceConfidence = Field(default=InferenceConfidence.MEDIUM)

    # 推理依据
    premises: list[InferencePremise] = Field(default_factory=list)
    applied_rules: list[InferenceRule] = Field(default_factory=list)
    reasoning_chain: list[str] = Field(default_factory=list)

    # 来源
    source: InferenceSource = Field(default=InferenceSource.RULE)

    # 元数据
    inference_id: str = Field(
        default_factory=lambda: f"inf_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class StateTransition(BaseModel):
    """状态转移"""

    from_state: str
    to_state: str
    trigger: str = Field(description="触发条件")
    probability: float = Field(default=1.0, ge=0.0, le=1.0)
    conditions: list[str] = Field(default_factory=list)


class TransitionGraph(BaseModel):
    """状态转移图"""

    states: list[str] = Field(default_factory=list)
    transitions: list[StateTransition] = Field(default_factory=list)
    current_state: str = Field(default="")


class InferenceEngineConfig(BaseModel):
    """推理引擎配置"""

    # 置信度阈值
    high_confidence_threshold: float = Field(default=0.8)
    medium_confidence_threshold: float = Field(default=0.6)
    low_confidence_threshold: float = Field(default=0.4)

    # 推理深度
    max_inference_depth: int = Field(default=5)

    # 启用的推理类型
    enabled_inference_types: list[InferenceType] = Field(
        default_factory=lambda: list(InferenceType)
    )


# ============================================================================
# State Inference Engine
# ============================================================================


class StateInferenceEngine:
    """
    状态推理引擎

    职责：
    - 基于已知推理未知状态
    - 状态转移预测
    - 填补信息缺口

    使用示例：
    ```python
    from scripts.state_inference_engine import StateInferenceEngine

    engine = StateInferenceEngine()

    # 添加已知前提
    engine.add_premise("任务进度是80%", confidence=0.9)
    engine.add_premise("没有阻塞问题", confidence=0.8)

    # 推理下一步状态
    result = engine.infer_next_state()

    print(f"推理结果: {result.inferred_value}")
    print(f"置信度: {result.confidence:.0%}")
    print(f"推理链: {result.reasoning_chain}")
    ```
    """

    def __init__(self, config: InferenceEngineConfig | None = None):
        """初始化状态推理引擎"""
        self._config = config or InferenceEngineConfig()
        self._premises: list[InferencePremise] = []
        self._rules: list[InferenceRule] = []
        self._state_graph: TransitionGraph | None = None

        # 初始化默认规则
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """初始化默认推理规则"""
        # 进度推理规则
        self._rules.extend([
            InferenceRule(
                rule_id="progress_high",
                name="高进度推理",
                condition="进度 >= 80% 且 无阻塞",
                conclusion="任务即将完成",
                confidence_modifier=0.9,
            ),
            InferenceRule(
                rule_id="progress_mid",
                name="中进度推理",
                condition="进度 >= 50% 且 无严重问题",
                conclusion="任务正常进行",
                confidence_modifier=0.85,
            ),
            InferenceRule(
                rule_id="progress_low",
                name="低进度推理",
                condition="进度 < 30%",
                conclusion="任务处于早期阶段",
                confidence_modifier=0.8,
            ),
        ])

        # 状态转移规则
        self._rules.extend([
            InferenceRule(
                rule_id="transition_complete",
                name="完成转移",
                condition="当前任务完成",
                conclusion="进入下一任务",
                confidence_modifier=0.85,
            ),
            InferenceRule(
                rule_id="transition_block",
                name="阻塞转移",
                condition="遇到阻塞",
                conclusion="需要外部帮助",
                confidence_modifier=0.9,
            ),
        ])

    # -----------------------------------------------------------------------
    # 前提管理
    # -----------------------------------------------------------------------

    def add_premise(
        self,
        fact: str,
        source: str = "",
        confidence: float = 1.0,
    ) -> None:
        """添加推理前提"""
        premise = InferencePremise(
            fact=fact,
            source=source,
            confidence=confidence,
        )
        self._premises.append(premise)

    def clear_premises(self) -> None:
        """清空前提"""
        self._premises.clear()

    # -----------------------------------------------------------------------
    # 状态转移图
    # -----------------------------------------------------------------------

    def set_state_graph(self, graph: TransitionGraph) -> None:
        """设置状态转移图"""
        self._state_graph = graph

    def define_transition(
        self,
        from_state: str,
        to_state: str,
        trigger: str,
        probability: float = 1.0,
    ) -> None:
        """定义状态转移"""
        if not self._state_graph:
            self._state_graph = TransitionGraph()

        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
            probability=probability,
        )

        self._state_graph.transitions.append(transition)
        self._state_graph.states.extend([from_state, to_state])
        self._state_graph.states = list(set(self._state_graph.states))

    # -----------------------------------------------------------------------
    # 推理执行
    # -----------------------------------------------------------------------

    def infer_next_state(self) -> InferenceResult:
        """推理下一个状态"""
        # 收集当前状态信息
        current_state = self._extract_current_state()

        # 应用规则推理
        applied_rules: list[InferenceRule] = []
        reasoning_chain: list[str] = []

        for rule in self._rules:
            if self._match_rule_condition(rule, current_state):
                applied_rules.append(rule)
                reasoning_chain.append(f"规则 '{rule.name}' 匹配: {rule.condition}")

        # 如果有状态转移图，预测转移
        if self._state_graph and current_state.get("state"):
            transition = self._predict_transition(current_state["state"])
            if transition:
                reasoning_chain.append(
                    f"预测转移: {transition.from_state} -> {transition.to_state}"
                )

        # 生成推理结果
        if applied_rules:
            # 取最高置信度的规则
            best_rule = max(applied_rules, key=lambda r: r.confidence_modifier)
            inferred_value = best_rule.conclusion
            confidence = best_rule.confidence_modifier * self._compute_premise_confidence()
        else:
            inferred_value = "无法确定下一状态"
            confidence = 0.3

        return InferenceResult(
            inferred_value=inferred_value,
            inference_type=InferenceType.DEDUCTIVE,
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            premises=self._premises.copy(),
            applied_rules=applied_rules,
            reasoning_chain=reasoning_chain,
            source=InferenceSource.RULE,
        )

    def infer_missing_field(self, field_name: str) -> InferenceResult:
        """推理缺失字段"""
        # 基于已有前提推理
        reasoning_chain: list[str] = []

        # 查找相关前提
        relevant_premises = [
            p for p in self._premises
            if field_name.lower() in p.fact.lower()
        ]

        if relevant_premises:
            # 直接从前提提取
            premise = relevant_premises[0]
            # 简单提取逻辑
            import re
            match = re.search(rf"{field_name}.*?[:：]\s*(.+)", premise.fact, re.I)
            if match:
                inferred_value = match.group(1).strip()
                reasoning_chain.append(f"从前提直接提取: {premise.fact}")

                return InferenceResult(
                    inferred_value=inferred_value,
                    inference_type=InferenceType.DEDUCTIVE,
                    confidence=premise.confidence,
                    confidence_level=self._get_confidence_level(premise.confidence),
                    premises=[premise],
                    reasoning_chain=reasoning_chain,
                    source=InferenceSource.CONTEXTUAL,
                )

        # 尝试归纳推理
        if len(self._premises) >= 2:
            inferred_value = self._inductive_inference(field_name)
            if inferred_value:
                return InferenceResult(
                    inferred_value=inferred_value,
                    inference_type=InferenceType.INDUCTIVE,
                    confidence=0.6,
                    confidence_level=InferenceConfidence.MEDIUM,
                    premises=self._premises,
                    reasoning_chain=["基于多个前提的归纳推理"],
                    source=InferenceSource.HEURISTIC,
                )

        return InferenceResult(
            inferred_value=None,
            inference_type=InferenceType.ABDUCTIVE,
            confidence=0.0,
            confidence_level=InferenceConfidence.UNCERTAIN,
            reasoning_chain=["无法推理缺失字段"],
        )

    def infer_task_phase(self) -> InferenceResult:
        """推理任务阶段"""
        # 提取进度信息
        progress = self._extract_progress()

        reasoning_chain: list[str] = []

        if progress >= 0.8:
            phase = "收尾阶段"
            confidence = 0.9
        elif progress >= 0.5:
            phase = "执行阶段"
            confidence = 0.85
        elif progress >= 0.2:
            phase = "探索阶段"
            confidence = 0.8
        else:
            phase = "初始阶段"
            confidence = 0.75

        reasoning_chain.append(f"基于进度 {progress:.0%} 推理任务阶段")

        return InferenceResult(
            inferred_value=phase,
            inference_type=InferenceType.DEDUCTIVE,
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            premises=self._premises,
            reasoning_chain=reasoning_chain,
            source=InferenceSource.HEURISTIC,
        )

    def infer_blocking_issues(self) -> InferenceResult:
        """推理阻塞问题"""
        reasoning_chain: list[str] = []
        blocking_issues: list[str] = []

        # 检查前提中的阻塞信号
        block_indicators = [
            "阻塞", "卡住", "等待", "无法", "失败",
            "blocked", "waiting", "failed", "cannot",
        ]

        for premise in self._premises:
            for indicator in block_indicators:
                if indicator in premise.fact.lower():
                    blocking_issues.append(premise.fact)
                    reasoning_chain.append(f"检测到阻塞信号: {indicator}")
                    break

        if blocking_issues:
            return InferenceResult(
                inferred_value=blocking_issues,
                inference_type=InferenceType.DEDUCTIVE,
                confidence=0.85,
                confidence_level=InferenceConfidence.HIGH,
                premises=[p for p in self._premises if p.fact in blocking_issues],
                reasoning_chain=reasoning_chain,
                source=InferenceSource.PATTERN,
            )

        return InferenceResult(
            inferred_value=[],
            inference_type=InferenceType.DEDUCTIVE,
            confidence=0.9,
            confidence_level=InferenceConfidence.HIGH,
            reasoning_chain=["未检测到阻塞信号"],
        )

    # -----------------------------------------------------------------------
    # 内部方法
    # -----------------------------------------------------------------------

    def _extract_current_state(self) -> dict[str, Any]:
        """提取当前状态"""
        state: dict[str, Any] = {}

        for premise in self._premises:
            # 提取进度
            if "进度" in premise.fact or "progress" in premise.fact.lower():
                import re
                match = re.search(r"(\d+(?:\.\d+)?)\s*%", premise.fact)
                if match:
                    state["progress"] = float(match.group(1)) / 100

            # 提取状态
            if "状态" in premise.fact or "state" in premise.fact.lower():
                state["state"] = premise.fact

            # 提取问题
            if "问题" in premise.fact or "problem" in premise.fact.lower():
                state["problems"] = state.get("problems", []) + [premise.fact]

        return state

    def _extract_progress(self) -> float:
        """提取进度"""
        import re

        for premise in self._premises:
            match = re.search(r"(\d+(?:\.\d+)?)\s*%", premise.fact)
            if match:
                return float(match.group(1)) / 100

        return 0.0

    def _match_rule_condition(self, rule: InferenceRule, state: dict[str, Any]) -> bool:
        """匹配规则条件"""
        condition = rule.condition.lower()

        # 检查进度条件
        if "进度 >=" in condition:
            import re
            match = re.search(r"进度\s*>=\s*(\d+)", condition)
            if match:
                threshold = float(match.group(1)) / 100
                if state.get("progress", 0) >= threshold:
                    if "无阻塞" in condition:
                        return not state.get("problems")
                    return True

        if "进度 <" in condition:
            import re
            match = re.search(r"进度\s*<\s*(\d+)", condition)
            if match:
                threshold = float(match.group(1)) / 100
                return state.get("progress", 0) < threshold

        # 检查状态条件
        if "完成" in condition:
            return state.get("state", "").endswith("完成")

        if "阻塞" in condition:
            return bool(state.get("problems"))

        return False

    def _predict_transition(self, current_state: str) -> StateTransition | None:
        """预测状态转移"""
        if not self._state_graph:
            return None

        # 查找可能的转移
        possible_transitions = [
            t for t in self._state_graph.transitions
            if t.from_state == current_state
        ]

        if possible_transitions:
            # 返回概率最高的
            return max(possible_transitions, key=lambda t: t.probability)

        return None

    def _inductive_inference(self, field_name: str) -> Any:
        """归纳推理"""
        # 简化实现：从多个前提中寻找模式
        values: list[str] = []

        for premise in self._premises:
            # 提取可能的值
            import re
            matches = re.findall(rf"{field_name}.*?[:：]\s*(.+)", premise.fact, re.I)
            values.extend(matches)

        if values:
            # 返回最频繁的值
            from collections import Counter
            counter = Counter(values)
            return counter.most_common(1)[0][0]

        return None

    def _compute_premise_confidence(self) -> float:
        """计算前提置信度"""
        if not self._premises:
            return 0.5

        # 加权平均
        return sum(p.confidence for p in self._premises) / len(self._premises)

    def _get_confidence_level(self, confidence: float) -> InferenceConfidence:
        """获取置信度级别"""
        if confidence >= self._config.high_confidence_threshold:
            return InferenceConfidence.CERTAIN
        elif confidence >= self._config.medium_confidence_threshold:
            return InferenceConfidence.HIGH
        elif confidence >= self._config.low_confidence_threshold:
            return InferenceConfidence.MEDIUM
        else:
            return InferenceConfidence.LOW


# ============================================================================
# 工厂函数
# ============================================================================


def create_inference_engine() -> StateInferenceEngine:
    """创建状态推理引擎"""
    return StateInferenceEngine()


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "InferenceType",
    "InferenceConfidence",
    "InferenceSource",
    "InferencePremise",
    "InferenceRule",
    "InferenceResult",
    "StateTransition",
    "TransitionGraph",
    "InferenceEngineConfig",
    "StateInferenceEngine",
    "create_inference_engine",
]

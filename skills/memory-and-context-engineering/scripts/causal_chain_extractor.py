"""
Agent Memory System - Causal Chain Extractor（因果链提取器）

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
从原始信息中提取因果关系，构建"问题→原因→解决方案"链。
这是模型高效推理的核心能力。
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class CausalRelationType(str, Enum):
    """因果关系类型"""

    DIRECT_CAUSE = "direct_cause"          # 直接原因
    CONTRIBUTING_FACTOR = "contributing"   # 促成因素
    ROOT_CAUSE = "root_cause"              # 根本原因
    ENABLING_CONDITION = "enabling"        # 使能条件
    TRIGGER = "trigger"                    # 触发因素


class ProblemType(str, Enum):
    """问题类型"""

    ERROR = "error"                        # 错误
    FAILURE = "failure"                    # 失败
    ANOMALY = "anomaly"                    # 异常
    BOTTLENECK = "bottleneck"              # 瓶颈
    CONFLICT = "conflict"                  # 冲突
    GAP = "gap"                            # 缺口


class SolutionStatus(str, Enum):
    """解决方案状态"""

    PROPOSED = "proposed"                  # 已提出
    VALIDATED = "validated"                # 已验证
    IMPLEMENTED = "implemented"            # 已实施
    FAILED = "failed"                      # 失败


# ============================================================================
# 数据模型
# ============================================================================


class CausalNode(BaseModel):
    """因果节点"""

    node_id: str = Field(
        default_factory=lambda: f"node_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    content: str = Field(description="节点内容")
    node_type: str = Field(default="event", description="节点类型")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="置信度")
    evidence: list[str] = Field(default_factory=list, description="证据")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CausalRelation(BaseModel):
    """因果关系"""

    from_node: str = Field(description="原因节点ID")
    to_node: str = Field(description="结果节点ID")
    relation_type: CausalRelationType = Field(description="关系类型")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="置信度")
    evidence: list[str] = Field(default_factory=list, description="证据")


class ProblemNode(CausalNode):
    """问题节点"""

    problem_type: ProblemType = Field(default=ProblemType.ERROR)
    impact: str = Field(default="", description="影响范围")
    urgency: int = Field(default=1, ge=1, le=5, description="紧急程度")


class CauseNode(CausalNode):
    """原因节点"""

    is_root_cause: bool = Field(default=False, description="是否根本原因")
    depth: int = Field(default=1, description="因果深度")


class SolutionNode(CausalNode):
    """解决方案节点"""

    status: SolutionStatus = Field(default=SolutionStatus.PROPOSED)
    effectiveness: float = Field(default=0.0, ge=0.0, le=1.0, description="有效性")
    effort: str = Field(default="medium", description="实施难度")


class ExtractedCausalChain(BaseModel):
    """提取的因果链"""

    chain_id: str = Field(
        default_factory=lambda: f"chain_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )

    # 问题
    problem: ProblemNode

    # 原因（可能多层级）
    causes: list[CauseNode] = Field(default_factory=list)
    causal_relations: list[CausalRelation] = Field(default_factory=list)

    # 解决方案
    solutions: list[SolutionNode] = Field(default_factory=list)

    # 元数据
    source_text: str = Field(default="", description="来源文本")
    extraction_confidence: float = Field(default=0.5, description="提取置信度")
    created_at: datetime = Field(default_factory=datetime.now)

    def to_summary(self) -> str:
        """生成摘要"""
        lines: list[str] = []

        lines.append(f"问题: {self.problem.content}")

        if self.causes:
            root_causes = [c for c in self.causes if c.is_root_cause]
            if root_causes:
                lines.append(f"根本原因: {', '.join(c.content for c in root_causes)}")
            else:
                lines.append(f"原因: {', '.join(c.content for c in self.causes)}")

        if self.solutions:
            lines.append(f"解决方案: {', '.join(s.content for s in self.solutions)}")

        return "\n".join(lines)


class ExtractionConfig(BaseModel):
    """提取配置"""

    # 因果关键词
    cause_keywords: list[str] = Field(
        default_factory=lambda: [
            "导致", "引起", "造成", "因为", "由于", "原因是",
            "caused by", "due to", "because", "result of",
        ]
    )

    # 问题关键词
    problem_keywords: list[str] = Field(
        default_factory=lambda: [
            "错误", "失败", "异常", "问题", "报错", "崩溃",
            "error", "failure", "exception", "issue", "bug", "crash",
        ]
    )

    # 解决方案关键词
    solution_keywords: list[str] = Field(
        default_factory=lambda: [
            "解决", "修复", "方案", "处理", "优化", "建议",
            "fix", "solution", "resolve", "optimize", "suggest",
        ]
    )

    # 置信度阈值
    min_confidence: float = Field(default=0.3, ge=0.0, le=1.0)


# ============================================================================
# Causal Chain Extractor
# ============================================================================


class CausalChainExtractor:
    """
    因果链提取器

    职责：
    - 从原始文本中提取因果关系
    - 构建"问题→原因→解决方案"链
    - 支持多层级因果推理

    使用示例：
    ```python
    from scripts.causal_chain_extractor import CausalChainExtractor

    extractor = CausalChainExtractor()

    # 提取因果链
    text = '''
    登录失败是因为数据库连接超时。
    连接超时的原因是连接池配置过小。
    解决方案：增加连接池大小到50。
    '''

    chains = extractor.extract(text)
    for chain in chains:
        print(chain.to_summary())
    ```
    """

    def __init__(self, config: ExtractionConfig | None = None):
        """初始化因果链提取器"""
        self._config = config or ExtractionConfig()
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> dict[str, re.Pattern]:
        """编译正则模式"""
        patterns = {}

        # 因果模式: A导致B
        cause_pattern = r"(.+?)(?:导致|引起|造成|caused?|due to)(.+)"
        patterns["cause"] = re.compile(cause_pattern, re.IGNORECASE)

        # 原因模式: 因为A，所以B
        reason_pattern = r"(?:因为|由于|because|since)(.+?)(?:，|,|所以|therefore)?(.+)"
        patterns["reason"] = re.compile(reason_pattern, re.IGNORECASE)

        # 解决方案模式
        solution_pattern = r"(?:解决|修复|方案|fix|solution)[:：]?\s*(.+)"
        patterns["solution"] = re.compile(solution_pattern, re.IGNORECASE)

        # 问题模式
        problem_pattern = r"(?:错误|失败|异常|error|failure|exception)[:：]?\s*(.+)"
        patterns["problem"] = re.compile(problem_pattern, re.IGNORECASE)

        return patterns

    def extract(self, text: str) -> list[ExtractedCausalChain]:
        """
        从文本提取因果链

        Args:
            text: 输入文本

        Returns:
            提取的因果链列表
        """
        chains: list[ExtractedCausalChain] = []

        # 分句
        sentences = self._split_sentences(text)

        # 提取问题
        problems = self._extract_problems(sentences)

        # 提取原因
        causes = self._extract_causes(sentences)

        # 提取解决方案
        solutions = self._extract_solutions(sentences)

        # 组装因果链
        for problem in problems:
            # 找到相关原因
            related_causes = self._find_related_causes(problem, causes, sentences)

            # 找到相关解决方案
            related_solutions = self._find_related_solutions(problem, solutions, sentences)

            # 创建因果链
            chain = ExtractedCausalChain(
                problem=problem,
                causes=related_causes,
                solutions=related_solutions,
                source_text=text,
                extraction_confidence=self._calculate_confidence(
                    problem, related_causes, related_solutions
                ),
            )
            chains.append(chain)

        return chains

    def _split_sentences(self, text: str) -> list[str]:
        """分句"""
        # 按句号、换行分割
        sentences = re.split(r"[。\n\.]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_problems(self, sentences: list[str]) -> list[ProblemNode]:
        """提取问题"""
        problems: list[ProblemNode] = []

        for sentence in sentences:
            # 匹配问题模式
            match = self._compiled_patterns["problem"].search(sentence)
            if match:
                problem = ProblemNode(
                    content=match.group(1).strip(),
                    problem_type=self._classify_problem(match.group(1)),
                    confidence=0.7,
                )
                problems.append(problem)
            else:
                # 检查问题关键词
                for keyword in self._config.problem_keywords:
                    if keyword in sentence.lower():
                        problem = ProblemNode(
                            content=sentence,
                            problem_type=self._classify_problem(sentence),
                            confidence=0.5,
                        )
                        problems.append(problem)
                        break

        return problems

    def _classify_problem(self, text: str) -> ProblemType:
        """分类问题类型"""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["错误", "error"]):
            return ProblemType.ERROR
        elif any(kw in text_lower for kw in ["失败", "failure"]):
            return ProblemType.FAILURE
        elif any(kw in text_lower for kw in ["异常", "exception", "anomaly"]):
            return ProblemType.ANOMALY
        elif any(kw in text_lower for kw in ["瓶颈", "bottleneck", "慢", "slow"]):
            return ProblemType.BOTTLENECK
        elif any(kw in text_lower for kw in ["冲突", "conflict", "矛盾"]):
            return ProblemType.CONFLICT
        else:
            return ProblemType.GAP

    def _extract_causes(self, sentences: list[str]) -> list[CauseNode]:
        """提取原因"""
        causes: list[CauseNode] = []

        for sentence in sentences:
            # 匹配因果模式
            match = self._compiled_patterns["cause"].search(sentence)
            if match:
                cause = CauseNode(
                    content=match.group(1).strip(),
                    confidence=0.7,
                    is_root_cause=self._is_root_cause(match.group(1)),
                )
                causes.append(cause)

            # 匹配原因模式
            match = self._compiled_patterns["reason"].search(sentence)
            if match:
                cause = CauseNode(
                    content=match.group(1).strip(),
                    confidence=0.6,
                )
                causes.append(cause)

        return causes

    def _extract_solutions(self, sentences: list[str]) -> list[SolutionNode]:
        """提取解决方案"""
        solutions: list[SolutionNode] = []

        for sentence in sentences:
            # 匹配解决方案模式
            match = self._compiled_patterns["solution"].search(sentence)
            if match:
                solution = SolutionNode(
                    content=match.group(1).strip(),
                    status=SolutionStatus.PROPOSED,
                    confidence=0.7,
                )
                solutions.append(solution)
            else:
                # 检查解决方案关键词
                for keyword in self._config.solution_keywords:
                    if keyword in sentence.lower():
                        solution = SolutionNode(
                            content=sentence,
                            status=SolutionStatus.PROPOSED,
                            confidence=0.5,
                        )
                        solutions.append(solution)
                        break

        return solutions

    def _is_root_cause(self, text: str) -> bool:
        """判断是否根本原因"""
        root_indicators = ["根本", "root", "底层", "基础", "核心"]
        return any(indicator in text.lower() for indicator in root_indicators)

    def _find_related_causes(
        self,
        problem: ProblemNode,
        causes: list[CauseNode],
        sentences: list[str],
    ) -> list[CauseNode]:
        """找到与问题相关的原因"""
        related: list[CauseNode] = []

        # 简单启发式：同一句或相邻句中的原因
        problem_text = problem.content.lower()

        for cause in causes:
            cause_text = cause.content.lower()

            # 检查是否有共同关键词
            problem_words = set(problem_text.split())
            cause_words = set(cause_text.split())
            common_words = problem_words & cause_words

            if common_words or self._are_adjacent(problem_text, cause_text, sentences):
                related.append(cause)

        return related

    def _find_related_solutions(
        self,
        problem: ProblemNode,
        solutions: list[SolutionNode],
        sentences: list[str],
    ) -> list[SolutionNode]:
        """找到与问题相关的解决方案"""
        related: list[SolutionNode] = []

        problem_text = problem.content.lower()

        for solution in solutions:
            solution_text = solution.content.lower()

            # 检查相关性
            if self._are_related(problem_text, solution_text):
                related.append(solution)

        return related

    def _are_adjacent(self, text1: str, text2: str, sentences: list[str]) -> bool:
        """检查两段文本是否相邻"""
        for i, sentence in enumerate(sentences):
            if text1 in sentence.lower():
                if i > 0 and text2 in sentences[i - 1].lower():
                    return True
                if i < len(sentences) - 1 and text2 in sentences[i + 1].lower():
                    return True
        return False

    def _are_related(self, text1: str, text2: str) -> bool:
        """检查两段文本是否相关"""
        # 简单的关键词重叠检查
        words1 = set(text1.split())
        words2 = set(text2.split())

        # 排除常见停用词
        stopwords = {"的", "是", "在", "了", "和", "the", "a", "is", "are", "was", "were"}
        words1 -= stopwords
        words2 -= stopwords

        common = words1 & words2
        return len(common) > 0

    def _calculate_confidence(
        self,
        problem: ProblemNode,
        causes: list[CauseNode],
        solutions: list[SolutionNode],
    ) -> float:
        """计算提取置信度"""
        # 基础置信度
        confidence = problem.confidence

        # 有原因增加置信度
        if causes:
            confidence += 0.2

        # 有解决方案增加置信度
        if solutions:
            confidence += 0.2

        # 有根本原因增加置信度
        if any(c.is_root_cause for c in causes):
            confidence += 0.1

        return min(1.0, confidence)

    def extract_from_dict(self, data: dict[str, Any]) -> ExtractedCausalChain | None:
        """
        从结构化数据提取因果链

        Args:
            data: 包含 problem, causes, solutions 的字典

        Returns:
            提取的因果链
        """
        if "problem" not in data:
            return None

        problem = ProblemNode(
            content=data["problem"],
            problem_type=self._classify_problem(data["problem"]),
        )

        causes = []
        for cause_data in data.get("causes", []):
            if isinstance(cause_data, str):
                causes.append(CauseNode(
                    content=cause_data,
                    is_root_cause=self._is_root_cause(cause_data),
                ))
            else:
                causes.append(CauseNode(
                    content=cause_data.get("content", ""),
                    is_root_cause=cause_data.get("is_root_cause", False),
                    confidence=cause_data.get("confidence", 0.5),
                ))

        solutions = []
        for sol_data in data.get("solutions", []):
            if isinstance(sol_data, str):
                solutions.append(SolutionNode(content=sol_data))
            else:
                solutions.append(SolutionNode(
                    content=sol_data.get("content", ""),
                    status=SolutionStatus(sol_data.get("status", "proposed")),
                ))

        return ExtractedCausalChain(
            problem=problem,
            causes=causes,
            solutions=solutions,
            extraction_confidence=0.8,
        )


# ============================================================================
# 工厂函数
# ============================================================================


def create_causal_extractor() -> CausalChainExtractor:
    """创建因果链提取器"""
    return CausalChainExtractor()


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "CausalRelationType",
    "ProblemType",
    "SolutionStatus",
    "CausalNode",
    "CausalRelation",
    "ProblemNode",
    "CauseNode",
    "SolutionNode",
    "ExtractedCausalChain",
    "ExtractionConfig",
    "CausalChainExtractor",
    "create_causal_extractor",
]

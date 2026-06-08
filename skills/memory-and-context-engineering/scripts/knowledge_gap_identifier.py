"""
Agent Memory System - Knowledge Gap Identifier（知识缺口识别器）

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
识别模型需要知道但当前缺失的知识，明确"已知/未知/假设"。
这是模型做出正确决策的前提。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class KnowledgeType(str, Enum):
    """知识类型"""

    FACTUAL = "factual"           # 事实性知识
    PROCEDURAL = "procedural"     # 过程性知识
    CONCEPTUAL = "conceptual"     # 概念性知识
    CONTEXTUAL = "contextual"     # 上下文知识
    PREFERENTIAL = "preferential" # 偏好性知识
    TEMPORAL = "temporal"         # 时间性知识


class GapCategory(str, Enum):
    """缺口类别"""

    MISSING_INFO = "missing_info"       # 缺失信息
    UNCERTAINTY = "uncertainty"         # 不确定性
    AMBIGUITY = "ambiguity"             # 歧义
    CONFLICT = "conflict"               # 冲突
    OUTDATED = "outdated"               # 过时
    UNVERIFIED = "unverified"           # 未验证


class FillStrategy(str, Enum):
    """填充策略"""

    RETRIEVAL = "retrieval"        # 检索补充
    USER_CLARIFICATION = "user"    # 用户澄清
    TOOL_QUERY = "tool"            # 工具查询
    INFERENCE = "inference"        # 推理推断
    ASSUMPTION = "assumption"      # 假设暂时


class BlockingLevel(str, Enum):
    """阻塞级别"""

    CRITICAL = "critical"          # 必须立即解决
    HIGH = "high"                  # 强烈建议解决
    MEDIUM = "medium"              # 建议解决
    LOW = "low"                    # 可选解决
    NON_BLOCKING = "non_blocking"  # 不阻塞


# ============================================================================
# 数据模型
# ============================================================================


class KnowledgeItem(BaseModel):
    """知识项"""

    item_id: str = Field(
        default_factory=lambda: f"know_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    content: str = Field(description="知识内容")
    knowledge_type: KnowledgeType = Field(default=KnowledgeType.FACTUAL)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = Field(default="", description="知识来源")
    verified: bool = Field(default=False)
    expires_at: datetime | None = Field(default=None, description="过期时间")


class RequiredKnowledge(BaseModel):
    """所需知识"""

    description: str = Field(description="所需知识描述")
    knowledge_type: KnowledgeType = Field(default=KnowledgeType.FACTUAL)
    for_task: str = Field(default="", description="用于哪个任务")
    importance: int = Field(default=1, ge=1, le=5, description="重要性")
    context: str = Field(default="", description="上下文")


class IdentifiedGap(BaseModel):
    """识别的知识缺口"""

    gap_id: str = Field(
        default_factory=lambda: f"gap_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )

    # 缺口描述
    description: str = Field(description="缺口描述")
    category: GapCategory = Field(default=GapCategory.MISSING_INFO)
    knowledge_type: KnowledgeType = Field(default=KnowledgeType.FACTUAL)

    # 影响评估
    blocking_level: BlockingLevel = Field(default=BlockingLevel.MEDIUM)
    affected_tasks: list[str] = Field(default_factory=list, description="受影响的任务")
    impact_description: str = Field(default="", description="影响描述")

    # 填充建议
    suggested_strategy: FillStrategy = Field(default=FillStrategy.RETRIEVAL)
    suggested_query: str = Field(default="", description="建议的检索查询")
    suggested_questions: list[str] = Field(default_factory=list, description="建议向用户提问")

    # 状态
    filled: bool = Field(default=False)
    filled_by: str | None = Field(default=None)
    filled_at: datetime | None = Field(default=None)

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def mark_filled(self, source: str) -> None:
        """标记为已填充"""
        self.filled = True
        self.filled_by = source
        self.filled_at = datetime.now()
        self.updated_at = datetime.now()


class GapAnalysisResult(BaseModel):
    """缺口分析结果"""

    # 已有知识
    existing_knowledge: list[KnowledgeItem] = Field(default_factory=list)

    # 所需知识
    required_knowledge: list[RequiredKnowledge] = Field(default_factory=list)

    # 识别的缺口
    gaps: list[IdentifiedGap] = Field(default_factory=list)

    # 统计
    total_required: int = Field(default=0)
    total_existing: int = Field(default=0)
    total_gaps: int = Field(default=0)
    critical_gaps: int = Field(default=0)
    coverage_ratio: float = Field(default=1.0)

    # 建议
    recommended_actions: list[str] = Field(default_factory=list)

    # 元数据
    analysis_id: str = Field(
        default_factory=lambda: f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class GapIdentifierConfig(BaseModel):
    """缺口识别器配置"""

    # 置信度阈值
    low_confidence_threshold: float = Field(default=0.5, description="低置信度阈值")
    unverified_threshold: float = Field(default=0.7, description="未验证阈值")

    # 关键词
    uncertainty_keywords: list[str] = Field(
        default_factory=lambda: [
            "不确定", "不知道", "不清楚", "可能", "也许",
            "uncertain", "unknown", "maybe", "might", "possibly",
        ]
    )

    missing_keywords: list[str] = Field(
        default_factory=lambda: [
            "缺少", "缺失", "没有", "需要", "待确认",
            "missing", "lack", "need", "required", "pending",
        ]
    )


# ============================================================================
# Knowledge Gap Identifier
# ============================================================================


class KnowledgeGapIdentifier:
    """
    知识缺口识别器

    职责：
    - 识别当前任务需要的知识
    - 与已有知识对比
    - 明确缺口并建议补充方式

    使用示例：
    ```python
    from scripts.knowledge_gap_identifier import KnowledgeGapIdentifier

    identifier = KnowledgeGapIdentifier()

    # 注册已有知识
    identifier.register_knowledge(
        content="用户使用Python 3.9",
        knowledge_type="factual",
        confidence=0.9,
    )

    # 定义所需知识
    identifier.define_required(
        description="用户的Python环境配置",
        for_task="安装依赖包",
        importance=4,
    )

    # 分析缺口
    result = identifier.analyze()
    print(f"发现 {len(result.gaps)} 个知识缺口")

    # 获取建议的检索查询
    for gap in result.gaps:
        if gap.suggested_query:
            print(f"建议检索: {gap.suggested_query}")
    ```
    """

    def __init__(self, config: GapIdentifierConfig | None = None):
        """初始化知识缺口识别器"""
        self._config = config or GapIdentifierConfig()
        self._existing_knowledge: dict[str, KnowledgeItem] = {}
        self._required_knowledge: list[RequiredKnowledge] = []

    # -----------------------------------------------------------------------
    # 知识注册
    # -----------------------------------------------------------------------

    def register_knowledge(
        self,
        content: str,
        knowledge_type: KnowledgeType | str = KnowledgeType.FACTUAL,
        confidence: float = 1.0,
        source: str = "",
        verified: bool = False,
    ) -> str:
        """注册已有知识"""
        if isinstance(knowledge_type, str):
            knowledge_type = KnowledgeType(knowledge_type)

        item = KnowledgeItem(
            content=content,
            knowledge_type=knowledge_type,
            confidence=confidence,
            source=source,
            verified=verified,
        )
        self._existing_knowledge[item.item_id] = item
        return item.item_id

    def register_from_memory(self, memories: list[Any]) -> None:
        """从记忆注册知识"""
        for memory in memories:
            if hasattr(memory, "content"):
                confidence = getattr(memory, "confidence", 0.8)
                self.register_knowledge(
                    content=memory.content,
                    confidence=confidence,
                    source="memory",
                )

    # -----------------------------------------------------------------------
    # 所需知识定义
    # -----------------------------------------------------------------------

    def define_required(
        self,
        description: str,
        knowledge_type: KnowledgeType | str = KnowledgeType.FACTUAL,
        for_task: str = "",
        importance: int = 3,
        context: str = "",
    ) -> None:
        """定义所需知识"""
        if isinstance(knowledge_type, str):
            knowledge_type = KnowledgeType(knowledge_type)

        required = RequiredKnowledge(
            description=description,
            knowledge_type=knowledge_type,
            for_task=for_task,
            importance=importance,
            context=context,
        )
        self._required_knowledge.append(required)

    def infer_required_from_task(self, task_description: str) -> list[RequiredKnowledge]:
        """
        从任务描述推断所需知识

        Args:
            task_description: 任务描述

        Returns:
            推断的所需知识列表
        """
        required_list: list[RequiredKnowledge] = []

        # 分析任务描述中的关键词
        # 这里是简化的启发式实现

        # 检查技术栈需求
        tech_keywords = ["python", "java", "javascript", "数据库", "api", "框架"]
        for keyword in tech_keywords:
            if keyword in task_description.lower():
                required_list.append(RequiredKnowledge(
                    description=f"关于{keyword}的相关知识",
                    knowledge_type=KnowledgeType.PROCEDURAL,
                    for_task=task_description,
                    importance=4,
                ))

        # 检查不确定性
        for keyword in self._config.uncertainty_keywords:
            if keyword in task_description.lower():
                required_list.append(RequiredKnowledge(
                    description="任务中存在不确定性，需要澄清",
                    knowledge_type=KnowledgeType.CONTEXTUAL,
                    for_task=task_description,
                    importance=3,
                ))

        return required_list

    # -----------------------------------------------------------------------
    # 缺口分析
    # -----------------------------------------------------------------------

    def analyze(self) -> GapAnalysisResult:
        """执行缺口分析"""
        gaps: list[IdentifiedGap] = []

        # 1. 检查所需知识是否已有
        for required in self._required_knowledge:
            matched = self._find_matching_knowledge(required)

            if not matched:
                # 完全缺失
                gap = IdentifiedGap(
                    description=required.description,
                    category=GapCategory.MISSING_INFO,
                    knowledge_type=required.knowledge_type,
                    blocking_level=self._importance_to_blocking(required.importance),
                    affected_tasks=[required.for_task] if required.for_task else [],
                    suggested_strategy=self._suggest_strategy(required),
                    suggested_query=self._generate_query(required),
                )
                gaps.append(gap)

            elif matched.confidence < self._config.low_confidence_threshold:
                # 置信度低
                gap = IdentifiedGap(
                    description=f"'{required.description}' 置信度低 ({matched.confidence:.0%})",
                    category=GapCategory.UNCERTAINTY,
                    knowledge_type=required.knowledge_type,
                    blocking_level=BlockingLevel.MEDIUM,
                    affected_tasks=[required.for_task] if required.for_task else [],
                    suggested_strategy=FillStrategy.USER_CLARIFICATION,
                )
                gaps.append(gap)

            elif not matched.verified and matched.confidence < self._config.unverified_threshold:
                # 未验证
                gap = IdentifiedGap(
                    description=f"'{required.description}' 未验证",
                    category=GapCategory.UNVERIFIED,
                    knowledge_type=required.knowledge_type,
                    blocking_level=BlockingLevel.LOW,
                    suggested_strategy=FillStrategy.VERIFICATION,
                )
                gaps.append(gap)

        # 2. 检查知识冲突
        conflicts = self._detect_conflicts()
        for conflict in conflicts:
            gap = IdentifiedGap(
                description=f"知识冲突: {conflict['description']}",
                category=GapCategory.CONFLICT,
                blocking_level=BlockingLevel.HIGH,
                suggested_strategy=FillStrategy.USER_CLARIFICATION,
                suggested_questions=[conflict["question"]],
            )
            gaps.append(gap)

        # 3. 计算统计
        critical_gaps = sum(
            1 for g in gaps
            if g.blocking_level in [BlockingLevel.CRITICAL, BlockingLevel.HIGH]
        )

        coverage_ratio = (
            1.0 - len(gaps) / len(self._required_knowledge)
            if self._required_knowledge else 1.0
        )

        # 4. 生成建议
        recommended_actions = self._generate_recommendations(gaps)

        return GapAnalysisResult(
            existing_knowledge=list(self._existing_knowledge.values()),
            required_knowledge=self._required_knowledge,
            gaps=gaps,
            total_required=len(self._required_knowledge),
            total_existing=len(self._existing_knowledge),
            total_gaps=len(gaps),
            critical_gaps=critical_gaps,
            coverage_ratio=coverage_ratio,
            recommended_actions=recommended_actions,
        )

    def _find_matching_knowledge(self, required: RequiredKnowledge) -> KnowledgeItem | None:
        """查找匹配的已有知识"""
        required_keywords = set(required.description.lower().split())

        best_match: KnowledgeItem | None = None
        best_score = 0.0

        for item in self._existing_knowledge.values():
            # 类型匹配
            if item.knowledge_type != required.knowledge_type:
                continue

            # 内容相似度
            item_keywords = set(item.content.lower().split())
            common = required_keywords & item_keywords
            score = len(common) / len(required_keywords) if required_keywords else 0

            if score > best_score:
                best_score = score
                best_match = item

        return best_match if best_score > 0.3 else None

    def _importance_to_blocking(self, importance: int) -> BlockingLevel:
        """重要性转阻塞级别"""
        if importance >= 5:
            return BlockingLevel.CRITICAL
        elif importance >= 4:
            return BlockingLevel.HIGH
        elif importance >= 3:
            return BlockingLevel.MEDIUM
        elif importance >= 2:
            return BlockingLevel.LOW
        else:
            return BlockingLevel.NON_BLOCKING

    def _suggest_strategy(self, required: RequiredKnowledge) -> FillStrategy:
        """建议填充策略"""
        if required.knowledge_type == KnowledgeType.PREFERENTIAL:
            return FillStrategy.USER_CLARIFICATION
        elif required.knowledge_type == KnowledgeType.FACTUAL:
            return FillStrategy.RETRIEVAL
        elif required.knowledge_type == KnowledgeType.PROCEDURAL:
            return FillStrategy.TOOL_QUERY
        else:
            return FillStrategy.RETRIEVAL

    def _generate_query(self, required: RequiredKnowledge) -> str:
        """生成检索查询"""
        return required.description

    def _detect_conflicts(self) -> list[dict[str, str]]:
        """检测知识冲突"""
        conflicts: list[dict[str, str]] = []

        items = list(self._existing_knowledge.values())

        for i, item1 in enumerate(items):
            for item2 in items[i + 1:]:
                # 检查内容冲突（简化实现）
                if self._are_conflicting(item1.content, item2.content):
                    conflicts.append({
                        "description": f"'{item1.content}' vs '{item2.content}'",
                        "question": f"哪个是正确的：'{item1.content}' 还是 '{item2.content}'？",
                    })

        return conflicts

    def _are_conflicting(self, content1: str, content2: str) -> bool:
        """检查两个内容是否冲突"""
        # 简化实现：检查相反的关键词
        opposites = [
            (["是", "yes", "true"], ["不是", "no", "false"]),
            (["成功", "success"], ["失败", "failure"]),
            (["启用", "enable"], ["禁用", "disable"]),
        ]

        for positive, negative in opposites:
            has_positive_1 = any(p in content1.lower() for p in positive)
            has_negative_1 = any(n in content1.lower() for n in negative)
            has_positive_2 = any(p in content2.lower() for p in positive)
            has_negative_2 = any(n in content2.lower() for n in negative)

            if (has_positive_1 and has_negative_2) or (has_negative_1 and has_positive_2):
                return True

        return False

    def _generate_recommendations(self, gaps: list[IdentifiedGap]) -> list[str]:
        """生成建议行动"""
        recommendations: list[str] = []

        # 关键缺口
        critical = [g for g in gaps if g.blocking_level == BlockingLevel.CRITICAL]
        if critical:
            recommendations.append(
                f"立即解决 {len(critical)} 个关键知识缺口"
            )

        # 用户澄清
        user_gaps = [g for g in gaps if g.suggested_strategy == FillStrategy.USER_CLARIFICATION]
        if user_gaps:
            recommendations.append(
                f"向用户询问 {len(user_gaps)} 个问题以澄清"
            )

        # 检索补充
        retrieval_gaps = [g for g in gaps if g.suggested_strategy == FillStrategy.RETRIEVAL]
        if retrieval_gaps:
            recommendations.append(
                f"检索补充 {len(retrieval_gaps)} 个知识缺口"
            )

        return recommendations

    # -----------------------------------------------------------------------
    # 快速分析
    # -----------------------------------------------------------------------

    def quick_analyze(self, text: str) -> list[IdentifiedGap]:
        """
        快速分析文本中的知识缺口

        Args:
            text: 输入文本

        Returns:
            识别的缺口列表
        """
        gaps: list[IdentifiedGap] = []

        # 检查不确定性
        for keyword in self._config.uncertainty_keywords:
            if keyword in text.lower():
                gap = IdentifiedGap(
                    description=f"检测到不确定性: '{keyword}'",
                    category=GapCategory.UNCERTAINTY,
                    suggested_strategy=FillStrategy.USER_CLARIFICATION,
                    blocking_level=BlockingLevel.MEDIUM,
                )
                gaps.append(gap)
                break

        # 检查缺失信息
        for keyword in self._config.missing_keywords:
            if keyword in text.lower():
                gap = IdentifiedGap(
                    description=f"检测到缺失信息: '{keyword}'",
                    category=GapCategory.MISSING_INFO,
                    suggested_strategy=FillStrategy.RETRIEVAL,
                    blocking_level=BlockingLevel.HIGH,
                )
                gaps.append(gap)
                break

        return gaps

    # -----------------------------------------------------------------------
    # 清理
    # -----------------------------------------------------------------------

    def clear(self) -> None:
        """清空所有数据"""
        self._existing_knowledge.clear()
        self._required_knowledge.clear()


# ============================================================================
# 工厂函数
# ============================================================================


def create_gap_identifier() -> KnowledgeGapIdentifier:
    """创建知识缺口识别器"""
    return KnowledgeGapIdentifier()


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "KnowledgeType",
    "GapCategory",
    "FillStrategy",
    "BlockingLevel",
    "KnowledgeItem",
    "RequiredKnowledge",
    "IdentifiedGap",
    "GapAnalysisResult",
    "GapIdentifierConfig",
    "KnowledgeGapIdentifier",
    "create_gap_identifier",
]

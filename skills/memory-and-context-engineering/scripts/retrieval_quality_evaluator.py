"""
Agent Memory System - Retrieval Quality Evaluator（检索质量评估器）

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
评估检索结果质量，决定是否需要二次检索。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class QualityDimension(str, Enum):
    """质量维度"""

    RELEVANCE = "relevance"           # 相关性
    COMPLETENESS = "completeness"     # 完整性
    FRESHNESS = "freshness"           # 新鲜度
    DIVERSITY = "diversity"           # 多样性
    COHERENCE = "coherence"           # 连贯性
    CREDIBILITY = "credibility"       # 可信度


class QualityLevel(str, Enum):
    """质量级别"""

    EXCELLENT = "excellent"           # 优秀
    GOOD = "good"                     # 良好
    ACCEPTABLE = "acceptable"         # 可接受
    POOR = "poor"                     # 较差
    UNACCEPTABLE = "unacceptable"     # 不可接受


class ReretrievalNeed(str, Enum):
    """二次检索需求"""

    NOT_NEEDED = "not_needed"         # 不需要
    RECOMMENDED = "recommended"       # 建议
    REQUIRED = "required"             # 需要
    URGENT = "urgent"                 # 紧急


# ============================================================================
# 数据模型
# ============================================================================


class RetrievalItem(BaseModel):
    """检索项"""

    item_id: str
    content: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = Field(default="")
    timestamp: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DimensionScore(BaseModel):
    """维度评分"""

    dimension: QualityDimension
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    details: str = Field(default="")


class QualityAssessment(BaseModel):
    """质量评估结果"""

    # 各维度评分
    dimension_scores: list[DimensionScore] = Field(default_factory=list)

    # 综合评分
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    quality_level: QualityLevel = Field(default=QualityLevel.ACCEPTABLE)

    # 覆盖度
    coverage_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    covered_aspects: list[str] = Field(default_factory=list)
    missing_aspects: list[str] = Field(default_factory=list)

    # 多样性
    diversity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    unique_topics: int = Field(default=0)
    redundant_items: int = Field(default=0)

    # 元数据
    assessment_id: str = Field(
        default_factory=lambda: f"assess_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class ReretrievalDecision(BaseModel):
    """二次检索决策"""

    need: ReretrievalNeed = Field(default=ReretrievalNeed.NOT_NEEDED)
    reason: str = Field(default="")

    # 建议的改进
    suggested_queries: list[str] = Field(default_factory=list)
    suggested_strategy: str = Field(default="")

    # 调整参数
    suggested_top_k: int | None = None
    suggested_threshold: float | None = None

    created_at: datetime = Field(default_factory=datetime.now)


class EvaluationResult(BaseModel):
    """评估结果"""

    # 原始查询
    query: str = Field(default="")
    items: list[RetrievalItem] = Field(default_factory=list)

    # 质量评估
    quality: QualityAssessment = Field(default_factory=QualityAssessment)

    # 二次检索决策
    reretrieval: ReretrievalDecision = Field(default_factory=ReretrievalDecision)

    # 统计
    total_items: int = Field(default=0)
    high_quality_items: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.now)


class EvaluatorConfig(BaseModel):
    """评估器配置"""

    # 维度权重
    dimension_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "relevance": 0.30,
            "completeness": 0.20,
            "freshness": 0.15,
            "diversity": 0.15,
            "coherence": 0.10,
            "credibility": 0.10,
        }
    )

    # 阈值
    excellent_threshold: float = Field(default=0.85)
    good_threshold: float = Field(default=0.70)
    acceptable_threshold: float = Field(default=0.50)
    poor_threshold: float = Field(default=0.30)

    # 二次检索触发
    reretrieval_threshold: float = Field(default=0.50)
    min_high_quality_ratio: float = Field(default=0.30)


# ============================================================================
# Retrieval Quality Evaluator
# ============================================================================


class RetrievalQualityEvaluator:
    """
    检索质量评估器

    职责：
    - 评估检索结果质量
    - 计算各维度评分
    - 决定是否需要二次检索

    使用示例：
    ```python
    from scripts.retrieval_quality_evaluator import RetrievalQualityEvaluator

    evaluator = RetrievalQualityEvaluator()

    # 评估检索结果
    items = [
        {"item_id": "1", "content": "Python性能优化技巧", "score": 0.9},
        {"item_id": "2", "content": "代码优化最佳实践", "score": 0.8},
    ]

    result = evaluator.evaluate(
        query="如何优化Python代码",
        items=items,
    )

    print(f"综合评分: {result.quality.overall_score}")
    print(f"质量级别: {result.quality.quality_level}")
    print(f"是否需要二次检索: {result.reretrieval.need}")
    ```
    """

    def __init__(self, config: EvaluatorConfig | None = None):
        """初始化质量评估器"""
        self._config = config or EvaluatorConfig()

    # -----------------------------------------------------------------------
    # 核心评估
    # -----------------------------------------------------------------------

    def evaluate(
        self,
        query: str,
        items: list[RetrievalItem] | list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """
        评估检索结果

        Args:
            query: 原始查询
            items: 检索结果列表
            context: 上下文信息

        Returns:
            EvaluationResult 评估结果
        """
        # 标准化输入
        normalized_items = self._normalize_items(items)

        # 计算各维度评分
        dimension_scores = self._calculate_dimensions(query, normalized_items, context)

        # 计算综合评分
        overall_score = self._calculate_overall(dimension_scores)
        quality_level = self._determine_level(overall_score)

        # 计算覆盖度
        coverage = self._calculate_coverage(query, normalized_items)

        # 计算多样性
        diversity = self._calculate_diversity(normalized_items)

        # 构建质量评估
        quality = QualityAssessment(
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            quality_level=quality_level,
            coverage_ratio=coverage["ratio"],
            covered_aspects=coverage["covered"],
            missing_aspects=coverage["missing"],
            diversity_score=diversity["score"],
            unique_topics=diversity["unique_topics"],
            redundant_items=diversity["redundant"],
        )

        # 决定是否需要二次检索
        reretrieval = self._decide_reretrieval(query, quality, normalized_items)

        # 统计
        high_quality = sum(1 for item in normalized_items if item.score >= 0.7)

        return EvaluationResult(
            query=query,
            items=normalized_items,
            quality=quality,
            reretrieval=reretrieval,
            total_items=len(normalized_items),
            high_quality_items=high_quality,
        )

    def _normalize_items(
        self,
        items: list[RetrievalItem] | list[dict[str, Any]],
    ) -> list[RetrievalItem]:
        """标准化输入项"""
        normalized = []
        for item in items:
            if isinstance(item, RetrievalItem):
                normalized.append(item)
            else:
                normalized.append(RetrievalItem(
                    item_id=item.get("item_id", f"item_{len(normalized)}"),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    source=item.get("source", ""),
                    metadata=item.get("metadata", {}),
                ))
        return normalized

    # -----------------------------------------------------------------------
    # 维度计算
    # -----------------------------------------------------------------------

    def _calculate_dimensions(
        self,
        query: str,
        items: list[RetrievalItem],
        context: dict[str, Any] | None,
    ) -> list[DimensionScore]:
        """计算各维度评分"""
        scores: list[DimensionScore] = []

        # 相关性
        relevance = self._calculate_relevance(query, items)
        scores.append(DimensionScore(
            dimension=QualityDimension.RELEVANCE,
            score=relevance,
            weight=self._config.dimension_weights.get("relevance", 0.3),
            details=f"平均相关性: {relevance:.2f}",
        ))

        # 完整性
        completeness = self._calculate_completeness(query, items)
        scores.append(DimensionScore(
            dimension=QualityDimension.COMPLETENESS,
            score=completeness,
            weight=self._config.dimension_weights.get("completeness", 0.2),
            details=f"覆盖完整性: {completeness:.2f}",
        ))

        # 新鲜度
        freshness = self._calculate_freshness(items)
        scores.append(DimensionScore(
            dimension=QualityDimension.FRESHNESS,
            score=freshness,
            weight=self._config.dimension_weights.get("freshness", 0.15),
            details=f"平均新鲜度: {freshness:.2f}",
        ))

        # 多样性
        diversity = self._calculate_diversity(items)["score"]
        scores.append(DimensionScore(
            dimension=QualityDimension.DIVERSITY,
            score=diversity,
            weight=self._config.dimension_weights.get("diversity", 0.15),
            details=f"多样性: {diversity:.2f}",
        ))

        # 连贯性
        coherence = self._calculate_coherence(items)
        scores.append(DimensionScore(
            dimension=QualityDimension.COHERENCE,
            score=coherence,
            weight=self._config.dimension_weights.get("coherence", 0.1),
            details=f"连贯性: {coherence:.2f}",
        ))

        # 可信度
        credibility = self._calculate_credibility(items)
        scores.append(DimensionScore(
            dimension=QualityDimension.CREDIBILITY,
            score=credibility,
            weight=self._config.dimension_weights.get("credibility", 0.1),
            details=f"可信度: {credibility:.2f}",
        ))

        return scores

    def _calculate_relevance(self, query: str, items: list[RetrievalItem]) -> float:
        """计算相关性"""
        if not items:
            return 0.0

        # 基于检索分数
        scores = [item.score for item in items]
        return sum(scores) / len(scores)

    def _calculate_completeness(self, query: str, items: list[RetrievalItem]) -> float:
        """计算完整性"""
        if not items:
            return 0.0

        # 提取查询关键词
        query_keywords = set(query.lower().split())

        # 检查覆盖
        covered = 0
        for keyword in query_keywords:
            for item in items:
                if keyword in item.content.lower():
                    covered += 1
                    break

        return covered / len(query_keywords) if query_keywords else 1.0

    def _calculate_freshness(self, items: list[RetrievalItem]) -> float:
        """计算新鲜度"""
        if not items:
            return 0.0

        now = datetime.now()
        scores = []

        for item in items:
            if item.timestamp:
                age_days = (now - item.timestamp).days
                # 新鲜度随时间衰减
                freshness = max(0, 1 - age_days / 365)
                scores.append(freshness)
            else:
                scores.append(0.5)  # 未知时间假设中等

        return sum(scores) / len(scores)

    def _calculate_diversity(self, items: list[RetrievalItem]) -> dict[str, Any]:
        """计算多样性"""
        if not items:
            return {"score": 0.0, "unique_topics": 0, "redundant": 0}

        # 提取主题
        topics: set[str] = set()
        for item in items:
            # 简化：使用前几个词作为主题
            words = item.content.lower().split()[:3]
            if words:
                topics.add(" ".join(words))

        # 检测冗余
        redundant = len(items) - len(topics) if len(items) > len(topics) else 0

        # 多样性分数
        diversity = min(1.0, len(topics) / len(items)) if items else 0.0

        return {
            "score": diversity,
            "unique_topics": len(topics),
            "redundant": redundant,
        }

    def _calculate_coherence(self, items: list[RetrievalItem]) -> float:
        """计算连贯性"""
        if len(items) < 2:
            return 1.0

        # 简化实现：检查内容重叠
        overlaps = []
        for i, item1 in enumerate(items):
            for item2 in items[i + 1:]:
                words1 = set(item1.content.lower().split())
                words2 = set(item2.content.lower().split())
                overlap = len(words1 & words2) / min(len(words1), len(words2)) if words1 and words2 else 0
                overlaps.append(overlap)

        # 适度重叠表示连贯
        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
        coherence = 1 - abs(avg_overlap - 0.3)  # 0.3 是理想的适度重叠

        return max(0, coherence)

    def _calculate_credibility(self, items: list[RetrievalItem]) -> float:
        """计算可信度"""
        if not items:
            return 0.0

        # 基于来源和分数
        credible_sources = {"official", "documentation", "verified", "trusted"}

        scores = []
        for item in items:
            score = item.score
            if item.source.lower() in credible_sources:
                score = min(1.0, score + 0.1)
            scores.append(score)

        return sum(scores) / len(scores)

    def _calculate_overall(self, dimension_scores: list[DimensionScore]) -> float:
        """计算综合评分"""
        if not dimension_scores:
            return 0.0

        weighted_sum = sum(
            ds.score * ds.weight
            for ds in dimension_scores
        )
        total_weight = sum(ds.weight for ds in dimension_scores)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _determine_level(self, score: float) -> QualityLevel:
        """确定质量级别"""
        if score >= self._config.excellent_threshold:
            return QualityLevel.EXCELLENT
        elif score >= self._config.good_threshold:
            return QualityLevel.GOOD
        elif score >= self._config.acceptable_threshold:
            return QualityLevel.ACCEPTABLE
        elif score >= self._config.poor_threshold:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE

    def _calculate_coverage(
        self,
        query: str,
        items: list[RetrievalItem],
    ) -> dict[str, Any]:
        """计算覆盖度"""
        query_keywords = set(query.lower().split())

        covered: list[str] = []
        missing: list[str] = []

        for keyword in query_keywords:
            found = False
            for item in items:
                if keyword in item.content.lower():
                    covered.append(keyword)
                    found = True
                    break
            if not found:
                missing.append(keyword)

        ratio = len(covered) / len(query_keywords) if query_keywords else 1.0

        return {
            "ratio": ratio,
            "covered": covered,
            "missing": missing,
        }

    # -----------------------------------------------------------------------
    # 二次检索决策
    # -----------------------------------------------------------------------

    def _decide_reretrieval(
        self,
        query: str,
        quality: QualityAssessment,
        items: list[RetrievalItem],
    ) -> ReretrievalDecision:
        """决定是否需要二次检索"""
        # 评估质量
        if quality.overall_score >= self._config.good_threshold:
            return ReretrievalDecision(need=ReretrievalNeed.NOT_NEEDED)

        # 检查高质量项比例
        high_quality_ratio = (
            quality.diversity_score  # 简化使用多样性代替
        )
        if high_quality_ratio < self._config.min_high_quality_ratio:
            # 生成改进建议
            suggested_queries = self._generate_improved_queries(query, quality)
            return ReretrievalDecision(
                need=ReretrievalNeed.REQUIRED,
                reason=f"高质量结果比例过低 ({high_quality_ratio:.0%})",
                suggested_queries=suggested_queries,
                suggested_strategy="增加查询扩展和多样性保证",
                suggested_top_k=15,
            )

        # 检查覆盖度
        if quality.coverage_ratio < 0.5:
            return ReretrievalDecision(
                need=ReretrievalNeed.RECOMMENDED,
                reason=f"覆盖度不足 ({quality.coverage_ratio:.0%})",
                suggested_queries=quality.missing_aspects[:3],
                suggested_threshold=0.5,
            )

        # 检查质量级别
        if quality.quality_level == QualityLevel.POOR:
            return ReretrievalDecision(
                need=ReretrievalNeed.URGENT,
                reason="检索质量较差，建议立即重新检索",
                suggested_strategy="切换检索策略，增加查询扩展",
            )

        return ReretrievalDecision(
            need=ReretrievalNeed.NOT_NEEDED,
            reason="当前质量可接受",
        )

    def _generate_improved_queries(
        self,
        query: str,
        quality: QualityAssessment,
    ) -> list[str]:
        """生成改进的查询"""
        queries = [query]

        # 添加缺失方面
        for missing in quality.missing_aspects[:2]:
            queries.append(f"{query} {missing}")

        return queries


# ============================================================================
# 工厂函数
# ============================================================================


def create_quality_evaluator() -> RetrievalQualityEvaluator:
    """创建质量评估器"""
    return RetrievalQualityEvaluator()


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "QualityDimension",
    "QualityLevel",
    "ReretrievalNeed",
    "RetrievalItem",
    "DimensionScore",
    "QualityAssessment",
    "ReretrievalDecision",
    "EvaluationResult",
    "EvaluatorConfig",
    "RetrievalQualityEvaluator",
    "create_quality_evaluator",
]

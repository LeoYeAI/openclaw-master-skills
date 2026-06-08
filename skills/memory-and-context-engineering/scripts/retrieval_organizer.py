"""
Agent Memory System - Retrieval Organizer（检索结果组织器）

=== 功能说明 ===
对应 Context Engineering 核心能力：检索

实现文档要求：
- "RAG 只是把东西找回来，Context Engineering 决定这些东西能不能被模型用好"
- "能不能把检索结果组织成高质量上下文"

核心能力：
1. 检索结果重排序 - 基于相关性、新鲜度、热度的综合评分
2. 结果去重 - 去除重复或高度相似的检索结果
3. 多样性保证 - 避免结果过于集中
4. 检索结果压缩 - 将检索结果压缩为高质量摘要

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * tiktoken: >=0.5.0
    - 用途：Token 计数
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  tiktoken>=0.5.0
  ```
=== 声明结束 ===

安全提醒：检索结果组织不应改变原始语义
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from .token_budget import TokenBudgetManager


# ============================================================================
# 枚举类型
# ============================================================================


class RelevanceSource(str, Enum):
    """相关性来源"""

    VECTOR = "vector"          # 向量检索
    KEYWORD = "keyword"        # 关键词检索
    SEMANTIC = "semantic"      # 语义桶检索
    HYBRID = "hybrid"          # 混合检索


class DiversityStrategy(str, Enum):
    """多样性策略"""

    MMR = "mmr"                # 最大边际相关性
    CLUSTER = "cluster"        # 聚类后采样
    TOPIC = "topic"            # 主题分散
    NONE = "none"              # 不保证多样性


class RerankStrategy(str, Enum):
    """重排序策略"""

    RELEVANCE_ONLY = "relevance_only"      # 仅相关性
    FRESHNESS_WEIGHTED = "freshness_weighted"  # 新鲜度加权
    HEAT_WEIGHTED = "heat_weighted"        # 热度加权
    BALANCED = "balanced"                  # 平衡策略


# ============================================================================
# 数据模型
# ============================================================================


class RetrievalItem(BaseModel):
    """检索项"""

    item_id: str = Field(description="项ID")
    content: str = Field(description="内容")
    source: RelevanceSource = Field(description="检索来源")

    # 相关性指标
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5, description="相关性分数")
    vector_score: float = Field(ge=0.0, le=1.0, default=0.0, description="向量分数")
    keyword_score: float = Field(ge=0.0, le=1.0, default=0.0, description="关键词分数")

    # 时间指标
    created_at: datetime | None = Field(default=None, description="创建时间")
    freshness_score: float = Field(ge=0.0, le=1.0, default=1.0, description="新鲜度分数")

    # 热度指标
    access_count: int = Field(default=0, description="访问次数")
    heat_score: float = Field(ge=0.0, le=1.0, default=0.5, description="热度分数")

    # 元数据
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")

    # 去重相关
    content_hash: str | None = Field(default=None, description="内容哈希")


class RerankedItem(BaseModel):
    """重排序后的项"""

    item: RetrievalItem = Field(description="原始检索项")
    final_score: float = Field(ge=0.0, le=1.0, description="最终分数")
    rank: int = Field(description="排名")
    score_components: dict[str, float] = Field(
        default_factory=dict, description="分数组成"
    )


class RetrievalOrganizerConfig(BaseModel):
    """检索组织器配置"""

    # 重排序配置
    rerank_strategy: RerankStrategy = Field(
        default=RerankStrategy.BALANCED, description="重排序策略"
    )

    # 权重配置
    relevance_weight: float = Field(ge=0.0, le=1.0, default=0.4, description="相关性权重")
    freshness_weight: float = Field(ge=0.0, le=1.0, default=0.3, description="新鲜度权重")
    heat_weight: float = Field(ge=0.0, le=1.0, default=0.3, description="热度权重")

    # 去重配置
    dedup_threshold: float = Field(
        ge=0.0, le=1.0, default=0.95, description="去重相似度阈值"
    )

    # 多样性配置
    diversity_strategy: DiversityStrategy = Field(
        default=DiversityStrategy.TOPIC, description="多样性策略"
    )
    diversity_threshold: float = Field(
        ge=0.0, le=1.0, default=0.7, description="多样性阈值"
    )

    # 输出配置
    max_results: int = Field(default=10, description="最大结果数")
    max_tokens: int = Field(default=4000, description="最大Token数")


class OrganizedRetrieval(BaseModel):
    """组织后的检索结果"""

    # 结果列表
    items: list[RerankedItem] = Field(default_factory=list, description="重排序后的项")

    # 统计信息
    original_count: int = Field(default=0, description="原始数量")
    deduped_count: int = Field(default=0, description="去重后数量")
    final_count: int = Field(default=0, description="最终数量")

    # 压缩后的摘要
    summary: str | None = Field(default=None, description="压缩摘要")
    summary_tokens: int = Field(default=0, description="摘要Token数")

    # 质量评估
    quality_metrics: dict[str, float] = Field(
        default_factory=dict, description="质量指标"
    )

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


# ============================================================================
# Retrieval Organizer
# ============================================================================


class RetrievalOrganizer:
    """
    检索结果组织器

    实现文档要求："检索结果组织成高质量上下文"

    核心能力：
    1. 重排序 - 基于相关性、新鲜度、热度的综合评分
    2. 去重 - 去除重复或高度相似的结果
    3. 多样性 - 确保结果覆盖不同主题
    4. 压缩 - 将结果压缩为高质量摘要

    使用示例：
    ```python
    from scripts.retrieval_organizer import RetrievalOrganizer, RetrievalItem

    organizer = RetrievalOrganizer()

    # 添加检索结果
    items = [
        RetrievalItem(
            item_id="1",
            content="Python性能优化最佳实践",
            source=RelevanceSource.VECTOR,
            relevance_score=0.9,
            freshness_score=0.8,
            heat_score=0.7,
        ),
        # ... 更多结果
    ]

    # 组织检索结果
    result = organizer.organize(items, query="如何优化Python性能")

    print(f"原始数量: {result.original_count}")
    print(f"去重后: {result.deduped_count}")
    print(f"最终数量: {result.final_count}")

    # 查看排名
    for item in result.items[:3]:
        print(f"#{item.rank}: {item.item.content} (分数: {item.final_score:.2f})")
    ```
    """

    def __init__(
        self,
        config: RetrievalOrganizerConfig | None = None,
        token_budget: TokenBudgetManager | None = None,
    ) -> None:
        """
        初始化检索结果组织器

        Args:
            config: 配置
            token_budget: Token 预算管理器
        """
        self._config = config or RetrievalOrganizerConfig()
        self._token_budget = token_budget

    # -----------------------------------------------------------------------
    # 核心方法：组织检索结果
    # -----------------------------------------------------------------------

    def organize(
        self,
        items: list[RetrievalItem],
        query: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> OrganizedRetrieval:
        """
        组织检索结果

        流程：
        1. 计算内容哈希
        2. 去重
        3. 重排序
        4. 确保多样性
        5. 压缩摘要

        Args:
            items: 检索项列表
            query: 查询字符串（可选）
            context: 上下文信息（可选）

        Returns:
            OrganizedRetrieval 组织后的结果
        """
        original_count = len(items)

        # 1. 计算内容哈希
        items = self._compute_hashes(items)

        # 2. 去重
        deduped_items = self._deduplicate(items)
        deduped_count = len(deduped_items)

        # 3. 重排序
        reranked_items = self._rerank(deduped_items, query, context)

        # 4. 确保多样性
        diverse_items = self._ensure_diversity(reranked_items)

        # 5. 限制数量
        final_items = diverse_items[:self._config.max_results]

        # 6. 生成摘要
        summary = self._generate_summary(final_items, query)
        summary_tokens = self._count_tokens(summary) if summary else 0

        # 7. 计算质量指标
        quality_metrics = self._calculate_quality_metrics(final_items)

        return OrganizedRetrieval(
            items=final_items,
            original_count=original_count,
            deduped_count=deduped_count,
            final_count=len(final_items),
            summary=summary,
            summary_tokens=summary_tokens,
            quality_metrics=quality_metrics,
        )

    # -----------------------------------------------------------------------
    # 去重
    # -----------------------------------------------------------------------

    def _compute_hashes(self, items: list[RetrievalItem]) -> list[RetrievalItem]:
        """计算内容哈希"""
        for item in items:
            if item.content_hash is None:
                item.content_hash = self._hash_content(item.content)
        return items

    def _hash_content(self, content: str) -> str:
        """计算内容哈希"""
        # 标准化内容：去除空白、转小写
        normalized = " ".join(content.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()

    def _deduplicate(self, items: list[RetrievalItem]) -> list[RetrievalItem]:
        """
        去重

        策略：
        1. 基于哈希的精确去重
        2. 基于相似度的模糊去重
        """
        # 精确去重
        seen_hashes: set[str] = set()
        unique_items: list[RetrievalItem] = []

        for item in items:
            if item.content_hash and item.content_hash not in seen_hashes:
                seen_hashes.add(item.content_hash)
                unique_items.append(item)

        # 模糊去重（基于相似度）
        if self._config.dedup_threshold < 1.0:
            unique_items = self._fuzzy_dedup(unique_items)

        return unique_items

    def _fuzzy_dedup(self, items: list[RetrievalItem]) -> list[RetrievalItem]:
        """模糊去重"""
        result: list[RetrievalItem] = []

        for item in items:
            is_duplicate = False

            for existing in result:
                similarity = self._calculate_similarity(item.content, existing.content)

                if similarity >= self._config.dedup_threshold:
                    is_duplicate = True
                    # 保留分数更高的
                    if item.relevance_score > existing.relevance_score:
                        result.remove(existing)
                        result.append(item)
                    break

            if not is_duplicate:
                result.append(item)

        return result

    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        """计算文本相似度（Jaccard）"""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0

    # -----------------------------------------------------------------------
    # 重排序
    # -----------------------------------------------------------------------

    def _rerank(
        self,
        items: list[RetrievalItem],
        query: str | None,
        context: dict[str, Any] | None,
    ) -> list[RerankedItem]:
        """
        重排序

        策略：
        - relevance_only: 仅考虑相关性
        - freshness_weighted: 新鲜度加权
        - heat_weighted: 热度加权
        - balanced: 平衡策略
        """
        reranked: list[RerankedItem] = []

        for i, item in enumerate(items):
            final_score, components = self._calculate_final_score(
                item, query, context
            )

            reranked.append(RerankedItem(
                item=item,
                final_score=final_score,
                rank=i + 1,  # 临时排名，排序后更新
                score_components=components,
            ))

        # 按分数排序
        reranked.sort(key=lambda x: x.final_score, reverse=True)

        # 更新排名
        for i, item in enumerate(reranked):
            item.rank = i + 1

        return reranked

    def _calculate_final_score(
        self,
        item: RetrievalItem,
        query: str | None,
        context: dict[str, Any] | None,
    ) -> tuple[float, dict[str, float]]:
        """
        计算最终分数

        Returns:
            (最终分数, 分数组成)
        """
        components: dict[str, float] = {}

        # 相关性分数
        components["relevance"] = item.relevance_score

        # 新鲜度分数
        components["freshness"] = item.freshness_score

        # 热度分数
        components["heat"] = item.heat_score

        # 根据策略计算最终分数
        strategy = self._config.rerank_strategy

        if strategy == RerankStrategy.RELEVANCE_ONLY:
            final_score = item.relevance_score

        elif strategy == RerankStrategy.FRESHNESS_WEIGHTED:
            final_score = (
                item.relevance_score * 0.5 +
                item.freshness_score * 0.5
            )

        elif strategy == RerankStrategy.HEAT_WEIGHTED:
            final_score = (
                item.relevance_score * 0.5 +
                item.heat_score * 0.5
            )

        else:  # BALANCED
            final_score = (
                item.relevance_score * self._config.relevance_weight +
                item.freshness_score * self._config.freshness_weight +
                item.heat_score * self._config.heat_weight
            )

        # 查询匹配加成
        if query:
            query_bonus = self._calculate_query_match(query, item.content)
            final_score = final_score * 0.8 + query_bonus * 0.2
            components["query_match"] = query_bonus

        return min(1.0, final_score), components

    def _calculate_query_match(self, query: str, content: str) -> float:
        """计算查询匹配度"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        matches = query_words & content_words
        return len(matches) / len(query_words)

    # -----------------------------------------------------------------------
    # 多样性
    # -----------------------------------------------------------------------

    def _ensure_diversity(
        self,
        items: list[RerankedItem],
    ) -> list[RerankedItem]:
        """
        确保多样性

        策略：
        - mmr: 最大边际相关性
        - cluster: 聚类后采样
        - topic: 主题分散
        - none: 不处理
        """
        if self._config.diversity_strategy == DiversityStrategy.NONE:
            return items

        if len(items) <= 3:
            return items

        strategy = self._config.diversity_strategy

        if strategy == DiversityStrategy.MMR:
            return self._apply_mmr(items)
        elif strategy == DiversityStrategy.TOPIC:
            return self._apply_topic_diversity(items)
        else:
            return items

    def _apply_mmr(self, items: list[RerankedItem]) -> list[RerankedItem]:
        """
        应用 MMR (Maximal Marginal Relevance)

        平衡相关性和多样性
        """
        if not items:
            return items

        lambda_param = 0.7  # 相关性权重
        selected: list[RerankedItem] = [items[0]]  # 先选最相关的
        remaining = items[1:]

        while remaining and len(selected) < self._config.max_results:
            best_item = None
            best_score = -1

            for item in remaining:
                # 相关性分数
                relevance = item.final_score

                # 与已选项目的最大相似度（惩罚）
                max_similarity = max(
                    self._calculate_similarity(item.item.content, s.item.content)
                    for s in selected
                )

                # MMR 分数
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_item = item

            if best_item:
                selected.append(best_item)
                remaining.remove(best_item)
            else:
                break

        # 更新排名
        for i, item in enumerate(selected):
            item.rank = i + 1

        return selected

    def _apply_topic_diversity(self, items: list[RerankedItem]) -> list[RerankedItem]:
        """
        应用主题分散策略

        确保结果覆盖不同主题
        """
        # 简化实现：按关键词分组
        topic_groups: dict[str, list[RerankedItem]] = {}

        for item in items:
            # 提取主题关键词
            topic = self._extract_topic(item.item.content)
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(item)

        # 从每个主题组选择最优项
        selected: list[RerankedItem] = []
        for topic, group in topic_groups.items():
            if group:
                selected.append(group[0])  # 该主题最相关的

        # 补充剩余项
        remaining = [item for item in items if item not in selected]
        selected.extend(remaining)

        # 限制数量并更新排名
        selected = selected[:self._config.max_results]
        for i, item in enumerate(selected):
            item.rank = i + 1

        return selected

    def _extract_topic(self, content: str) -> str:
        """提取主题关键词"""
        # 简化：使用前几个词作为主题
        words = content.lower().split()[:3]
        return "_".join(words) if words else "unknown"

    # -----------------------------------------------------------------------
    # 摘要生成
    # -----------------------------------------------------------------------

    def _generate_summary(
        self,
        items: list[RerankedItem],
        query: str | None,
    ) -> str | None:
        """
        生成检索结果摘要

        格式：
        [检索摘要] (N个结果)
        1. 内容... (相关性: X.XX)
        2. 内容... (相关性: X.XX)
        ...
        """
        if not items:
            return None

        lines: list[str] = [f"[检索摘要] ({len(items)}个结果)"]

        if query:
            lines.append(f"查询: {query}")
            lines.append("")

        for item in items[:5]:  # 最多5个
            content = item.item.content[:100]  # 截断
            if len(item.item.content) > 100:
                content += "..."
            lines.append(f"{item.rank}. {content} (分数: {item.final_score:.2f})")

        if len(items) > 5:
            lines.append(f"... 还有 {len(items) - 5} 个结果")

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # 质量评估
    # -----------------------------------------------------------------------

    def _calculate_quality_metrics(
        self,
        items: list[RerankedItem],
    ) -> dict[str, float]:
        """计算质量指标"""
        if not items:
            return {
                "avg_relevance": 0.0,
                "avg_freshness": 0.0,
                "avg_heat": 0.0,
                "diversity": 0.0,
            }

        # 平均相关性
        avg_relevance = sum(i.item.relevance_score for i in items) / len(items)

        # 平均新鲜度
        avg_freshness = sum(i.item.freshness_score for i in items) / len(items)

        # 平均热度
        avg_heat = sum(i.item.heat_score for i in items) / len(items)

        # 多样性（基于内容差异）
        diversity = self._calculate_diversity_score(items)

        return {
            "avg_relevance": avg_relevance,
            "avg_freshness": avg_freshness,
            "avg_heat": avg_heat,
            "diversity": diversity,
        }

    def _calculate_diversity_score(self, items: list[RerankedItem]) -> float:
        """计算多样性分数"""
        if len(items) < 2:
            return 1.0

        # 计算所有对之间的平均相似度
        total_similarity = 0.0
        pair_count = 0

        for i, item_a in enumerate(items):
            for item_b in items[i + 1:]:
                similarity = self._calculate_similarity(
                    item_a.item.content, item_b.item.content
                )
                total_similarity += similarity
                pair_count += 1

        avg_similarity = total_similarity / pair_count if pair_count > 0 else 0

        # 多样性 = 1 - 平均相似度
        return 1.0 - avg_similarity

    # -----------------------------------------------------------------------
    # 辅助方法
    # -----------------------------------------------------------------------

    def _count_tokens(self, text: str) -> int:
        """计算 Token 数"""
        if self._token_budget:
            return self._token_budget.count(text)
        return max(1, len(text) // 4)


# ============================================================================
# 工厂函数
# ============================================================================


def create_retrieval_organizer(
    rerank_strategy: RerankStrategy = RerankStrategy.BALANCED,
    max_results: int = 10,
) -> RetrievalOrganizer:
    """
    创建检索结果组织器

    Args:
        rerank_strategy: 重排序策略
        max_results: 最大结果数

    Returns:
        RetrievalOrganizer 实例
    """
    config = RetrievalOrganizerConfig(
        rerank_strategy=rerank_strategy,
        max_results=max_results,
    )

    return RetrievalOrganizer(config=config)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "RelevanceSource",
    "DiversityStrategy",
    "RerankStrategy",
    "RetrievalItem",
    "RerankedItem",
    "RetrievalOrganizerConfig",
    "OrganizedRetrieval",
    "RetrievalOrganizer",
    "create_retrieval_organizer",
]

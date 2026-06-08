"""
Agent Memory System - Noise Filter（噪声过滤器）

=== 功能说明 ===
对应 Context Engineering 核心能力：选择

实现文档要求：
- "不是所有信息都该进模型"
- "相关、及时、可控"
- "相关、及时、可控"是第一原则

核心能力：
1. 相关性过滤 - 过滤低相关性内容
2. 新鲜度过滤 - 过滤过时内容
3. 冗余去除 - 去除重复信息
4. 噪声识别 - 识别并标记噪声

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

安全提醒：过滤应保守，避免误删关键信息
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class FilterReason(str, Enum):
    """过滤原因"""

    LOW_RELEVANCE = "low_relevance"          # 低相关性
    OUTDATED = "outdated"                    # 过时
    REDUNDANT = "redundant"                  # 冗余
    NOISY = "noisy"                          # 噪声
    IRRELEVANT_CONTEXT = "irrelevant_context"  # 与上下文无关
    LOW_QUALITY = "low_quality"              # 低质量


class ContentType(str, Enum):
    """内容类型"""

    MEMORY = "memory"          # 记忆内容
    RETRIEVAL = "retrieval"    # 检索结果
    TOOL_RESULT = "tool_result"  # 工具返回
    CONVERSATION = "conversation"  # 对话内容
    DOCUMENT = "document"      # 文档内容


class FilterStrategy(str, Enum):
    """过滤策略"""

    AGGRESSIVE = "aggressive"    # 激进过滤
    BALANCED = "balanced"        # 平衡过滤
    CONSERVATIVE = "conservative"  # 保守过滤


# ============================================================================
# 数据模型
# ============================================================================


class FilterableItem(BaseModel):
    """可过滤项"""

    item_id: str = Field(description="项ID")
    content: str = Field(description="内容")
    content_type: ContentType = Field(description="内容类型")

    # 相关性指标
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5, description="相关性分数")

    # 时间指标
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_accessed: datetime | None = Field(default=None, description="最后访问时间")

    # 质量指标
    quality_score: float = Field(ge=0.0, le=1.0, default=0.5, description="质量分数")

    # 元数据
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class FilterResult(BaseModel):
    """过滤结果"""

    # 保留的项
    kept_items: list[FilterableItem] = Field(default_factory=list, description="保留项")

    # 过滤掉的项
    filtered_items: list[tuple[FilterableItem, FilterReason]] = Field(
        default_factory=list, description="被过滤项及原因"
    )

    # 统计
    original_count: int = Field(default=0, description="原始数量")
    kept_count: int = Field(default=0, description="保留数量")
    filtered_count: int = Field(default=0, description="过滤数量")

    # 过滤率
    filter_rate: float = Field(ge=0.0, le=1.0, default=0.0, description="过滤率")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class NoiseFilterConfig(BaseModel):
    """噪声过滤器配置"""

    # 过滤策略
    strategy: FilterStrategy = Field(
        default=FilterStrategy.BALANCED, description="过滤策略"
    )

    # 相关性阈值
    relevance_threshold: float = Field(
        ge=0.0, le=1.0, default=0.3, description="相关性阈值"
    )

    # 新鲜度阈值（小时）
    freshness_threshold_hours: int = Field(
        default=168, description="新鲜度阈值（小时）"  # 默认7天
    )

    # 冗余相似度阈值
    redundancy_threshold: float = Field(
        ge=0.0, le=1.0, default=0.9, description="冗余相似度阈值"
    )

    # 质量阈值
    quality_threshold: float = Field(
        ge=0.0, le=1.0, default=0.3, description="质量阈值"
    )

    # 噪声关键词
    noise_keywords: list[str] = Field(
        default_factory=lambda: [
            "test", "测试", "debug", "调试", "temp", "临时",
            "draft", "草稿", "todo", "待办", "placeholder",
        ],
        description="噪声关键词",
    )

    # 保留关键词（包含这些词的内容不被过滤）
    preserve_keywords: list[str] = Field(
        default_factory=lambda: [
            "error", "错误", "fail", "失败", "critical", "关键",
            "important", "重要", "required", "必需",
        ],
        description="保留关键词",
    )


# ============================================================================
# Noise Filter
# ============================================================================


class NoiseFilter:
    """
    噪声过滤器

    实现文档要求："相关、及时、可控"

    核心能力：
    1. 相关性过滤 - 过滤与当前任务无关的内容
    2. 新鲜度过滤 - 过滤过时的内容
    3. 冗余去除 - 去除重复或高度相似的内容
    4. 噪声识别 - 识别测试、调试、临时等内容

    使用示例：
    ```python
    from scripts.noise_filter import NoiseFilter, FilterableItem, ContentType

    filter = NoiseFilter()

    # 创建可过滤项
    items = [
        FilterableItem(
            item_id="1",
            content="这是重要的错误日志",
            content_type=ContentType.MEMORY,
            relevance_score=0.8,
            quality_score=0.9,
        ),
        FilterableItem(
            item_id="2",
            content="这是一条测试数据",
            content_type=ContentType.MEMORY,
            relevance_score=0.3,
            quality_score=0.4,
        ),
    ]

    # 执行过滤
    result = filter.filter(items, context={"task": "调试错误"})

    print(f"原始数量: {result.original_count}")
    print(f"保留数量: {result.kept_count}")
    print(f"过滤数量: {result.filtered_count}")

    # 查看被过滤的原因
    for item, reason in result.filtered_items:
        print(f"过滤: {item.content[:20]}... 原因: {reason.value}")
    ```
    """

    def __init__(
        self,
        config: NoiseFilterConfig | None = None,
    ) -> None:
        """
        初始化噪声过滤器

        Args:
            config: 配置
        """
        self._config = config or NoiseFilterConfig()

        # 根据策略调整阈值
        self._adjust_thresholds_by_strategy()

    def _adjust_thresholds_by_strategy(self) -> None:
        """根据策略调整阈值"""
        if self._config.strategy == FilterStrategy.AGGRESSIVE:
            # 激进过滤：提高阈值
            self._relevance_threshold = self._config.relevance_threshold + 0.1
            self._quality_threshold = self._config.quality_threshold + 0.1

        elif self._config.strategy == FilterStrategy.CONSERVATIVE:
            # 保守过滤：降低阈值
            self._relevance_threshold = max(0.1, self._config.relevance_threshold - 0.1)
            self._quality_threshold = max(0.1, self._config.quality_threshold - 0.1)

        else:  # BALANCED
            self._relevance_threshold = self._config.relevance_threshold
            self._quality_threshold = self._config.quality_threshold

    # -----------------------------------------------------------------------
    # 核心方法：过滤
    # -----------------------------------------------------------------------

    def filter(
        self,
        items: list[FilterableItem],
        context: dict[str, Any] | None = None,
        query: str | None = None,
    ) -> FilterResult:
        """
        执行过滤

        流程：
        1. 识别保留关键词（强制保留）
        2. 相关性过滤
        3. 新鲜度过滤
        4. 噪声识别
        5. 质量过滤
        6. 冗余去除

        Args:
            items: 待过滤项列表
            context: 上下文信息
            query: 查询字符串

        Returns:
            FilterResult 过滤结果
        """
        original_count = len(items)
        kept_items: list[FilterableItem] = []
        filtered_items: list[tuple[FilterableItem, FilterReason]] = []

        # 待冗余处理的项
        candidates: list[FilterableItem] = []

        for item in items:
            # 检查保留关键词（强制保留）
            if self._contains_preserve_keywords(item.content):
                candidates.append(item)
                continue

            # 相关性过滤
            if item.relevance_score < self._relevance_threshold:
                filtered_items.append((item, FilterReason.LOW_RELEVANCE))
                continue

            # 新鲜度过滤
            if self._is_outdated(item):
                filtered_items.append((item, FilterReason.OUTDATED))
                continue

            # 噪声识别
            if self._is_noisy(item):
                filtered_items.append((item, FilterReason.NOISY))
                continue

            # 质量过滤
            if item.quality_score < self._quality_threshold:
                filtered_items.append((item, FilterReason.LOW_QUALITY))
                continue

            # 上下文相关性检查
            if context and not self._is_contextually_relevant(item, context, query):
                filtered_items.append((item, FilterReason.IRRELEVANT_CONTEXT))
                continue

            candidates.append(item)

        # 冗余去除
        kept_items = self._remove_redundancy(candidates, filtered_items)

        # 统计
        kept_count = len(kept_items)
        filtered_count = len(filtered_items)
        filter_rate = filtered_count / original_count if original_count > 0 else 0.0

        return FilterResult(
            kept_items=kept_items,
            filtered_items=filtered_items,
            original_count=original_count,
            kept_count=kept_count,
            filtered_count=filtered_count,
            filter_rate=filter_rate,
        )

    # -----------------------------------------------------------------------
    # 过滤规则
    # -----------------------------------------------------------------------

    def _contains_preserve_keywords(self, content: str) -> bool:
        """检查是否包含保留关键词"""
        content_lower = content.lower()
        return any(kw in content_lower for kw in self._config.preserve_keywords)

    def _is_outdated(self, item: FilterableItem) -> bool:
        """检查是否过时"""
        threshold = timedelta(hours=self._config.freshness_threshold_hours)
        now = datetime.now()

        # 检查创建时间
        age = now - item.created_at
        if age > threshold:
            # 但如果质量很高，仍然保留
            if item.quality_score >= 0.8:
                return False
            return True

        return False

    def _is_noisy(self, item: FilterableItem) -> bool:
        """识别噪声内容"""
        content_lower = item.content.lower()

        # 检查噪声关键词
        for keyword in self._config.noise_keywords:
            if keyword in content_lower:
                # 但如果相关性很高，仍然保留
                if item.relevance_score >= 0.8:
                    return False
                return True

        # 检查常见噪声模式
        noise_patterns = [
            "test_", "_test", "tmp_", "_tmp",  # 测试文件
            "placeholder", "lorem ipsum",       # 占位符
            "copy of", "副本",                   # 副本
        ]

        for pattern in noise_patterns:
            if pattern in content_lower:
                return True

        return False

    def _is_contextually_relevant(
        self,
        item: FilterableItem,
        context: dict[str, Any],
        query: str | None,
    ) -> bool:
        """检查与上下文的相关性"""
        # 如果有查询，计算查询匹配度
        if query:
            query_words = set(query.lower().split())
            content_words = set(item.content.lower().split())

            if query_words:
                matches = query_words & content_words
                match_ratio = len(matches) / len(query_words)

                # 如果查询匹配度很低，可能不相关
                if match_ratio < 0.2:
                    return False

        # 检查任务上下文
        task = context.get("task", "")
        if task:
            # 简单的任务-内容匹配
            task_words = set(task.lower().split())
            content_words = set(item.content.lower().split())

            # 如果任务关键词出现在内容中，相关
            if task_words & content_words:
                return True

        # 默认相关
        return True

    # -----------------------------------------------------------------------
    # 冗余去除
    # -----------------------------------------------------------------------

    def _remove_redundancy(
        self,
        items: list[FilterableItem],
        filtered_items: list[tuple[FilterableItem, FilterReason]],
    ) -> list[FilterableItem]:
        """
        去除冗余

        策略：保留第一个出现的项，过滤后续高度相似的项
        """
        result: list[FilterableItem] = []

        for item in items:
            is_redundant = False

            for existing in result:
                similarity = self._calculate_similarity(item.content, existing.content)

                if similarity >= self._config.redundancy_threshold:
                    is_redundant = True
                    # 记录被过滤的原因
                    filtered_items.append((item, FilterReason.REDUNDANT))

                    # 如果新项质量更高，替换
                    if item.quality_score > existing.quality_score:
                        result.remove(existing)
                        result.append(item)
                    break

            if not is_redundant:
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
    # 辅助方法
    # -----------------------------------------------------------------------

    def update_config(self, config: NoiseFilterConfig) -> None:
        """更新配置"""
        self._config = config
        self._adjust_thresholds_by_strategy()

    def set_strategy(self, strategy: FilterStrategy) -> None:
        """设置过滤策略"""
        self._config.strategy = strategy
        self._adjust_thresholds_by_strategy()

    def get_filter_stats(self, result: FilterResult) -> dict[str, Any]:
        """
        获取过滤统计

        Args:
            result: 过滤结果

        Returns:
            统计信息
        """
        # 按原因统计
        by_reason: dict[str, int] = {}
        for _, reason in result.filtered_items:
            by_reason[reason.value] = by_reason.get(reason.value, 0) + 1

        return {
            "original_count": result.original_count,
            "kept_count": result.kept_count,
            "filtered_count": result.filtered_count,
            "filter_rate": result.filter_rate,
            "by_reason": by_reason,
            "strategy": self._config.strategy.value,
        }


# ============================================================================
# 工厂函数
# ============================================================================


def create_noise_filter(
    strategy: FilterStrategy = FilterStrategy.BALANCED,
    relevance_threshold: float = 0.3,
) -> NoiseFilter:
    """
    创建噪声过滤器

    Args:
        strategy: 过滤策略
        relevance_threshold: 相关性阈值

    Returns:
        NoiseFilter 实例
    """
    config = NoiseFilterConfig(
        strategy=strategy,
        relevance_threshold=relevance_threshold,
    )

    return NoiseFilter(config=config)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "FilterReason",
    "ContentType",
    "FilterStrategy",
    "FilterableItem",
    "FilterResult",
    "NoiseFilterConfig",
    "NoiseFilter",
    "create_noise_filter",
]

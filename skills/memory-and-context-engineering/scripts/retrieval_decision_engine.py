"""
Agent Memory System - Retrieval Decision Engine（检索时机决策引擎）

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
智能决定"何时检索"、"检索什么"，避免不必要的检索开销。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class RetrievalNeed(str, Enum):
    """检索需求级别"""

    REQUIRED = "required"          # 必须检索
    RECOMMENDED = "recommended"    # 建议检索
    OPTIONAL = "optional"          # 可选检索
    UNNECESSARY = "unnecessary"    # 不需要检索
    CACHED = "cached"              # 可用缓存


class QueryType(str, Enum):
    """查询类型"""

    FACTUAL = "factual"            # 事实查询
    PROCEDURAL = "procedural"      # 过程查询
    CONCEPTUAL = "conceptual"      # 概念查询
    TROUBLESHOOTING = "troubleshooting"  # 故障排查
    EXPLORATORY = "exploratory"    # 探索性查询


class RetrievalStrategy(str, Enum):
    """检索策略"""

    VECTOR_ONLY = "vector_only"              # 仅向量检索
    KEYWORD_ONLY = "keyword_only"            # 仅关键词检索
    HYBRID = "hybrid"                        # 混合检索
    SEMANTIC_BUCKET = "semantic_bucket"      # 语义桶检索
    MULTI_PATH = "multi_path"                # 多路召回


class CacheDecision(str, Enum):
    """缓存决策"""

    USE_CACHE = "use_cache"        # 使用缓存
    PARTIAL_CACHE = "partial"      # 部分使用缓存
    FRESH_RETRIEVAL = "fresh"      # 全新检索


# ============================================================================
# 数据模型
# ============================================================================


class QueryAnalysis(BaseModel):
    """查询分析结果"""

    original_query: str
    query_type: QueryType = Field(default=QueryType.FACTUAL)
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    intent: str = Field(default="", description="查询意图")
    complexity: int = Field(default=1, ge=1, le=5, description="复杂度")


class CacheStatus(BaseModel):
    """缓存状态"""

    has_cache: bool = Field(default=False)
    cache_age_seconds: float = Field(default=0.0)
    cache_hit_ratio: float = Field(default=0.0)
    cache_completeness: float = Field(default=0.0)  # 缓存完整性
    cache_key: str = Field(default="")


class RetrievalDecision(BaseModel):
    """检索决策"""

    # 决策结果
    need: RetrievalNeed = Field(default=RetrievalNeed.OPTIONAL)
    strategy: RetrievalStrategy = Field(default=RetrievalStrategy.HYBRID)
    cache_decision: CacheDecision = Field(default=CacheDecision.FRESH_RETRIEVAL)

    # 检索参数
    queries: list[str] = Field(default_factory=list)
    top_k: int = Field(default=10)
    similarity_threshold: float = Field(default=0.7)

    # 理由
    reason: str = Field(default="")

    # 预估
    estimated_latency_ms: float = Field(default=0.0)
    estimated_cost: float = Field(default=0.0)

    # 元数据
    decision_id: str = Field(
        default_factory=lambda: f"dec_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class DecisionConfig(BaseModel):
    """决策配置"""

    # 缓存配置
    cache_max_age_seconds: int = Field(default=3600, description="缓存最大年龄")
    cache_min_completeness: float = Field(default=0.8, description="最小缓存完整性")

    # 检索阈值
    knowledge_boundary_threshold: float = Field(default=0.6, description="知识边界阈值")
    uncertainty_threshold: float = Field(default=0.5, description="不确定性阈值")

    # 成本控制
    max_retrieval_per_session: int = Field(default=50, description="每会话最大检索次数")
    retrieval_cooldown_seconds: float = Field(default=1.0, description="检索冷却时间")


# ============================================================================
# Retrieval Decision Engine
# ============================================================================


class RetrievalDecisionEngine:
    """
    检索时机决策引擎

    职责：
    - 判断是否需要检索
    - 选择检索策略
    - 缓存优先决策

    使用示例：
    ```python
    from scripts.retrieval_decision_engine import RetrievalDecisionEngine

    engine = RetrievalDecisionEngine()

    # 分析查询
    decision = engine.decide(
        query="如何优化Python代码性能",
        context={
            "task": "代码优化",
            "has_cache": False,
        },
    )

    if decision.need == "required":
        print(f"建议检索: {decision.queries}")
        print(f"策略: {decision.strategy}")
    ```
    """

    def __init__(
        self,
        config: DecisionConfig | None = None,
        cache_checker: Callable[[str], CacheStatus] | None = None,
    ):
        """初始化检索决策引擎"""
        self._config = config or DecisionConfig()
        self._cache_checker = cache_checker
        self._retrieval_history: list[datetime] = []

    # -----------------------------------------------------------------------
    # 核心决策
    # -----------------------------------------------------------------------

    def decide(
        self,
        query: str,
        context: dict[str, Any] | None = None,
        knowledge_state: dict[str, Any] | None = None,
    ) -> RetrievalDecision:
        """
        做出检索决策

        Args:
            query: 用户查询
            context: 上下文信息
            knowledge_state: 当前知识状态

        Returns:
            RetrievalDecision 检索决策
        """
        context = context or {}
        knowledge_state = knowledge_state or {}

        # 1. 分析查询
        analysis = self._analyze_query(query)

        # 2. 检查缓存
        cache_status = self._check_cache(query)

        # 3. 评估检索需求
        need = self._evaluate_need(analysis, context, knowledge_state, cache_status)

        # 4. 选择策略
        strategy = self._select_strategy(analysis, need, cache_status)

        # 5. 生成检索查询
        queries = self._generate_queries(analysis, context)

        # 6. 做出缓存决策
        cache_decision = self._decide_cache(cache_status)

        # 7. 预估
        latency, cost = self._estimate(queries, strategy)

        return RetrievalDecision(
            need=need,
            strategy=strategy,
            cache_decision=cache_decision,
            queries=queries,
            reason=self._get_reason(need, cache_status),
            estimated_latency_ms=latency,
            estimated_cost=cost,
        )

    # -----------------------------------------------------------------------
    # 查询分析
    # -----------------------------------------------------------------------

    def _analyze_query(self, query: str) -> QueryAnalysis:
        """分析查询"""
        # 确定查询类型
        query_type = self._classify_query(query)

        # 提取关键词
        keywords = self._extract_keywords(query)

        # 提取实体
        entities = self._extract_entities(query)

        # 分析意图
        intent = self._analyze_intent(query)

        # 计算复杂度
        complexity = self._calculate_complexity(query)

        return QueryAnalysis(
            original_query=query,
            query_type=query_type,
            keywords=keywords,
            entities=entities,
            intent=intent,
            complexity=complexity,
        )

    def _classify_query(self, query: str) -> QueryType:
        """分类查询类型"""
        query_lower = query.lower()

        # 故障排查
        if any(kw in query_lower for kw in ["错误", "失败", "异常", "error", "fail", "exception"]):
            return QueryType.TROUBLESHOOTING

        # 过程查询
        if any(kw in query_lower for kw in ["如何", "怎么", "步骤", "how to", "steps"]):
            return QueryType.PROCEDURAL

        # 概念查询
        if any(kw in query_lower for kw in ["什么是", "概念", "解释", "what is", "concept"]):
            return QueryType.CONCEPTUAL

        # 探索性查询
        if any(kw in query_lower for kw in ["比较", "分析", "evaluate", "compare"]):
            return QueryType.EXPLORATORY

        return QueryType.FACTUAL

    def _extract_keywords(self, query: str) -> list[str]:
        """提取关键词"""
        # 简化实现：分割并过滤
        words = query.split()
        stopwords = {"的", "是", "在", "了", "和", "the", "a", "is", "are", "was", "were"}
        return [w for w in words if w.lower() not in stopwords and len(w) > 1]

    def _extract_entities(self, query: str) -> list[str]:
        """提取实体"""
        # 简化实现：提取大写单词和特定模式
        import re
        entities = []

        # 大写单词
        entities.extend(re.findall(r"\b[A-Z][a-z]+\b", query))

        # 技术术语
        tech_terms = re.findall(r"\b(?:Python|Java|JavaScript|API|SQL|NoSQL)\b", query, re.I)
        entities.extend(tech_terms)

        return list(set(entities))

    def _analyze_intent(self, query: str) -> str:
        """分析查询意图"""
        # 简化实现
        if "优化" in query:
            return "optimization"
        elif "实现" in query:
            return "implementation"
        elif "解决" in query:
            return "problem_solving"
        else:
            return "information_seeking"

    def _calculate_complexity(self, query: str) -> int:
        """计算查询复杂度"""
        # 基于长度和关键词
        length = len(query)
        question_marks = query.count("?") + query.count("？")

        complexity = 1
        if length > 50:
            complexity += 1
        if length > 100:
            complexity += 1
        if question_marks > 1:
            complexity += 1

        return min(5, complexity)

    # -----------------------------------------------------------------------
    # 缓存检查
    # -----------------------------------------------------------------------

    def _check_cache(self, query: str) -> CacheStatus:
        """检查缓存"""
        if self._cache_checker:
            return self._cache_checker(query)

        # 默认返回无缓存
        return CacheStatus(has_cache=False)

    def _decide_cache(self, cache_status: CacheStatus) -> CacheDecision:
        """决定是否使用缓存"""
        if not cache_status.has_cache:
            return CacheDecision.FRESH_RETRIEVAL

        # 检查缓存年龄
        if cache_status.cache_age_seconds > self._config.cache_max_age_seconds:
            return CacheDecision.FRESH_RETRIEVAL

        # 检查完整性
        if cache_status.cache_completeness >= self._config.cache_min_completeness:
            return CacheDecision.USE_CACHE

        return CacheDecision.PARTIAL_CACHE

    # -----------------------------------------------------------------------
    # 需求评估
    # -----------------------------------------------------------------------

    def _evaluate_need(
        self,
        analysis: QueryAnalysis,
        context: dict[str, Any],
        knowledge_state: dict[str, Any],
        cache_status: CacheStatus,
    ) -> RetrievalNeed:
        """评估检索需求"""
        # 可以使用缓存
        if cache_status.has_cache and cache_status.cache_completeness >= 0.9:
            return RetrievalNeed.CACHED

        # 检查知识边界
        knowledge_coverage = knowledge_state.get("coverage", 1.0)
        if knowledge_coverage < self._config.knowledge_boundary_threshold:
            return RetrievalNeed.REQUIRED

        # 检查不确定性
        uncertainty = knowledge_state.get("uncertainty", 0.0)
        if uncertainty > self._config.uncertainty_threshold:
            return RetrievalNeed.REQUIRED

        # 故障排查通常需要检索
        if analysis.query_type == QueryType.TROUBLESHOOTING:
            return RetrievalNeed.RECOMMENDED

        # 复杂查询建议检索
        if analysis.complexity >= 4:
            return RetrievalNeed.RECOMMENDED

        # 探索性查询可选
        if analysis.query_type == QueryType.EXPLORATORY:
            return RetrievalNeed.OPTIONAL

        return RetrievalNeed.OPTIONAL

    # -----------------------------------------------------------------------
    # 策略选择
    # -----------------------------------------------------------------------

    def _select_strategy(
        self,
        analysis: QueryAnalysis,
        need: RetrievalNeed,
        cache_status: CacheStatus,
    ) -> RetrievalStrategy:
        """选择检索策略"""
        # 不需要检索
        if need == RetrievalNeed.CACHED:
            return RetrievalStrategy.SEMANTIC_BUCKET

        # 故障排查：混合检索
        if analysis.query_type == QueryType.TROUBLESHOOTING:
            return RetrievalStrategy.HYBRID

        # 概念查询：向量优先
        if analysis.query_type == QueryType.CONCEPTUAL:
            return RetrievalStrategy.VECTOR_ONLY

        # 过程查询：关键词优先
        if analysis.query_type == QueryType.PROCEDURAL:
            return RetrievalStrategy.KEYWORD_ONLY

        # 复杂查询：多路召回
        if analysis.complexity >= 4:
            return RetrievalStrategy.MULTI_PATH

        return RetrievalStrategy.HYBRID

    # -----------------------------------------------------------------------
    # 查询生成
    # -----------------------------------------------------------------------

    def _generate_queries(
        self,
        analysis: QueryAnalysis,
        context: dict[str, Any],
    ) -> list[str]:
        """生成检索查询"""
        queries = [analysis.original_query]

        # 添加关键词组合查询
        if len(analysis.keywords) > 1:
            keyword_query = " ".join(analysis.keywords[:3])
            queries.append(keyword_query)

        # 添加实体查询
        for entity in analysis.entities[:2]:
            queries.append(entity)

        # 基于上下文添加查询
        task = context.get("task", "")
        if task:
            queries.append(f"{task} {analysis.intent}")

        return list(set(queries))[:5]

    # -----------------------------------------------------------------------
    # 预估
    # -----------------------------------------------------------------------

    def _estimate(
        self,
        queries: list[str],
        strategy: RetrievalStrategy,
    ) -> tuple[float, float]:
        """预估延迟和成本"""
        # 基础延迟
        base_latency = 50.0  # ms

        # 策略影响
        strategy_factors = {
            RetrievalStrategy.VECTOR_ONLY: 1.0,
            RetrievalStrategy.KEYWORD_ONLY: 0.8,
            RetrievalStrategy.HYBRID: 1.5,
            RetrievalStrategy.MULTI_PATH: 2.0,
        }
        latency = base_latency * len(queries) * strategy_factors.get(strategy, 1.0)

        # 成本（简化）
        cost = len(queries) * 0.001

        return latency, cost

    def _get_reason(
        self,
        need: RetrievalNeed,
        cache_status: CacheStatus,
    ) -> str:
        """获取决策理由"""
        if need == RetrievalNeed.CACHED:
            return "缓存命中，无需重新检索"
        elif need == RetrievalNeed.REQUIRED:
            return "知识边界外，必须检索"
        elif need == RetrievalNeed.RECOMMENDED:
            return "建议检索以提高回答质量"
        elif need == RetrievalNeed.OPTIONAL:
            return "可选检索，已有知识可能足够"
        else:
            return "无需检索"

    # -----------------------------------------------------------------------
    # 限流控制
    # -----------------------------------------------------------------------

    def can_retrieve(self) -> bool:
        """检查是否可以检索（限流控制）"""
        now = datetime.now()

        # 清理过期历史
        cutoff = now - timedelta(minutes=5)
        self._retrieval_history = [
            t for t in self._retrieval_history if t > cutoff
        ]

        # 检查限制
        if len(self._retrieval_history) >= self._config.max_retrieval_per_session:
            return False

        # 检查冷却
        if self._retrieval_history:
            last = self._retrieval_history[-1]
            if (now - last).total_seconds() < self._config.retrieval_cooldown_seconds:
                return False

        return True

    def record_retrieval(self) -> None:
        """记录检索"""
        self._retrieval_history.append(datetime.now())


# ============================================================================
# 工厂函数
# ============================================================================


def create_retrieval_decision_engine(
    cache_max_age_seconds: int = 3600,
) -> RetrievalDecisionEngine:
    """创建检索决策引擎"""
    config = DecisionConfig(cache_max_age_seconds=cache_max_age_seconds)
    return RetrievalDecisionEngine(config=config)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "RetrievalNeed",
    "QueryType",
    "RetrievalStrategy",
    "CacheDecision",
    "QueryAnalysis",
    "CacheStatus",
    "RetrievalDecision",
    "DecisionConfig",
    "RetrievalDecisionEngine",
    "create_retrieval_decision_engine",
]

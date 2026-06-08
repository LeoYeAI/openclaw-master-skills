"""
Agent Memory System - 短期记忆洞察分析器

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
from typing import Any

from pydantic import BaseModel, Field

from .types import (
    ShortTermMemoryItem,
    SemanticBucketType,
)


# ============================================================================
# 短期洞察专用类型
# ============================================================================


class TopicCluster(BaseModel):
    """
    话题簇
    
    由洞察分析器发现的话题集合，包含属于同一话题的记忆项
    """
    
    cluster_id: str
    topic_label: str                    # 话题标签（自动生成）
    items: list[ShortTermMemoryItem] = Field(default_factory=list)
    
    # 洞察分析结果
    keywords: list[str] = Field(default_factory=list)  # 核心关键词
    priority: float = Field(ge=0.0, le=1.0, default=0.5)  # 提炼优先级
    coherence: float = Field(ge=0.0, le=1.0, default=0.5)  # 簇内聚性
    
    # 提炼决策
    should_extract: bool = True         # 是否应该提炼
    skip_reason: str = ""               # 跳过原因
    should_merge: bool = False          # 是否需要与其他簇合并
    merge_with: list[str] = Field(default_factory=list)  # 合并目标ID
    
    # 元数据
    dominant_bucket: SemanticBucketType | None = None  # 主导桶类型
    avg_relevance: float = Field(ge=0.0, le=1.0, default=0.5)
    
    class Config:
        arbitrary_types_allowed = True


class TopicRelation(BaseModel):
    """话题关联"""
    
    source_cluster: str                 # 源簇ID
    target_cluster: str                 # 目标簇ID
    relation_type: str                  # 关联类型: dependency, similar, parent_child
    strength: float = Field(ge=0.0, le=1.0)  # 关联强度
    evidence: list[str] = Field(default_factory=list)  # 证据（共享关键词等）


class ExtractionDecision(BaseModel):
    """
    提炼决策
    
    由短期洞察分析器生成的结构化决策，指导提炼器如何精准提炼
    """
    
    decision_id: str
    clusters: list[TopicCluster] = Field(default_factory=list)
    relations: list[TopicRelation] = Field(default_factory=list)
    extraction_order: list[str] = Field(default_factory=list)  # 提炼顺序
    
    # 统计
    total_items: int = Field(default=0)
    items_to_extract: int = Field(default=0)
    items_to_skip: int = Field(default=0)
    clusters_to_merge: int = Field(default=0)
    
    # 决策质量
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class ShortTermInsightResult(BaseModel):
    """
    短期洞察结果
    
    完整的短期记忆洞察分析结果，供提炼器使用
    """
    
    insight_id: str
    decision: ExtractionDecision
    
    # 分析摘要（供日志/调试）
    summary: str = ""
    
    def format_for_extractor(self) -> dict[str, Any]:
        """
        格式化为提炼器可用的结构
        
        Returns:
            提炼器可直接使用的决策数据
        """
        return {
            "decision_id": self.decision.decision_id,
            "clusters": [
                {
                    "cluster_id": c.cluster_id,
                    "topic": c.topic_label,
                    "item_ids": [item.item_id for item in c.items],
                    "keywords": c.keywords,
                    "priority": c.priority,
                    "should_extract": c.should_extract,
                    "skip_reason": c.skip_reason,
                    "should_merge": c.should_merge,
                    "merge_with": c.merge_with,
                    "dominant_bucket": c.dominant_bucket.value if c.dominant_bucket else None,
                }
                for c in self.decision.clusters
            ],
            "relations": [
                {
                    "source": r.source_cluster,
                    "target": r.target_cluster,
                    "type": r.relation_type,
                    "strength": r.strength,
                }
                for r in self.decision.relations
            ],
            "extraction_order": self.decision.extraction_order,
            "stats": {
                "total_items": self.decision.total_items,
                "to_extract": self.decision.items_to_extract,
                "to_skip": self.decision.items_to_skip,
                "to_merge": self.decision.clusters_to_merge,
            },
            "confidence": self.decision.confidence,
        }


# ============================================================================
# 短期记忆洞察分析器
# ============================================================================


class ShortTermInsightAnalyzer:
    """
    短期记忆洞察分析器
    
    核心职责：分析短期记忆，发现话题模式，生成提炼决策
    
    设计理念：
    - 不预设话题，让话题自然涌现
    - 利用洞察能力发现模式
    - 输出结构化决策，指导精准提炼
    """
    
    def __init__(self) -> None:
        """初始化分析器"""
        # 相似度阈值
        self._similarity_threshold: float = 0.25
        
        # 提炼阈值
        self._priority_threshold: float = 0.35
        self._coherence_threshold: float = 0.3
        
        # 关键词权重（技术领域）
        self._domain_keywords: set[str] = {
            # 业务领域
            "电商", "支付", "订单", "用户", "商品", "库存", "物流",
            "营销", "会员", "积分", "优惠券", "购物车",
            # 技术领域
            "数据库", "前端", "后端", "API", "接口", "微服务",
            "架构", "缓存", "消息队列", "分布式", "容器",
            # 框架工具
            "MySQL", "PostgreSQL", "Redis", "Kafka", "Docker",
            "Vue", "React", "Node", "Spring", "Django",
            # 通用概念
            "系统", "模块", "功能", "流程", "设计", "实现",
            "性能", "安全", "测试", "部署", "监控",
        }
    
    def analyze(
        self,
        items: list[ShortTermMemoryItem],
    ) -> ShortTermInsightResult:
        """
        分析短期记忆项，生成洞察决策
        
        Args:
            items: 短期记忆项列表
            
        Returns:
            短期洞察结果
        """
        if not items:
            return self._create_empty_result()
        
        # 1. 提取关键词
        item_keywords: dict[str, set[str]] = {}
        for item in items:
            item_keywords[item.item_id] = self._extract_keywords(item.content)
        
        # 2. 话题聚类（核心：让话题自然涌现）
        clusters = self._cluster_by_topic(items, item_keywords)
        
        # 3. 评估簇质量
        self._evaluate_clusters(clusters)
        
        # 4. 发现话题关联
        relations = self._discover_relations(clusters, item_keywords)
        
        # 5. 生成提炼决策
        self._make_extraction_decisions(clusters)
        
        # 6. 确定提炼顺序
        extraction_order = self._determine_order(clusters, relations)
        
        # 7. 统计
        total_items = sum(len(c.items) for c in clusters)
        items_to_extract = sum(
            len(c.items) for c in clusters if c.should_extract
        )
        items_to_skip = total_items - items_to_extract
        clusters_to_merge = sum(1 for c in clusters if c.should_merge)
        
        # 8. 生成决策
        decision = ExtractionDecision(
            decision_id=f"ed_{uuid.uuid4().hex[:8]}",
            clusters=clusters,
            relations=relations,
            extraction_order=extraction_order,
            total_items=total_items,
            items_to_extract=items_to_extract,
            items_to_skip=items_to_skip,
            clusters_to_merge=clusters_to_merge,
            confidence=self._calculate_confidence(clusters),
        )
        
        # 9. 生成摘要
        summary = self._generate_summary(decision)
        
        return ShortTermInsightResult(
            insight_id=f"sti_{uuid.uuid4().hex[:8]}",
            decision=decision,
            summary=summary,
        )
    
    def _extract_keywords(self, content: str) -> set[str]:
        """
        提取关键词
        
        采用简单的关键词匹配，未来可扩展为NLP提取
        """
        keywords: set[str] = set()
        
        for kw in self._domain_keywords:
            if kw.lower() in content.lower():
                keywords.add(kw)
        
        return keywords
    
    def _cluster_by_topic(
        self,
        items: list[ShortTermMemoryItem],
        item_keywords: dict[str, set[str]],
    ) -> list[TopicCluster]:
        """
        话题聚类
        
        核心算法：基于关键词相似度的凝聚聚类
        让话题自然涌现，不预设分类
        """
        clusters: list[TopicCluster] = []
        used_item_ids: set[str] = set()
        
        # 按桶类型分组，同类型更容易聚在一起
        items_by_bucket: dict[SemanticBucketType, list[ShortTermMemoryItem]] = {}
        for item in items:
            if item.bucket_type not in items_by_bucket:
                items_by_bucket[item.bucket_type] = []
            items_by_bucket[item.bucket_type].append(item)
        
        # 对每个桶内的项进行聚类
        for bucket_type, bucket_items in items_by_bucket.items():
            bucket_used: set[str] = set()
            
            for item in bucket_items:
                if item.item_id in bucket_used:
                    continue
                
                # 找相似项形成簇
                cluster_items = [item]
                cluster_keywords = item_keywords[item.item_id].copy()
                bucket_used.add(item.item_id)
                
                for other in bucket_items:
                    if other.item_id in bucket_used:
                        continue
                    
                    # 计算与当前簇的相似度
                    other_keywords = item_keywords[other.item_id]
                    similarity = self._calculate_similarity(
                        cluster_keywords, other_keywords
                    )
                    
                    if similarity >= self._similarity_threshold:
                        cluster_items.append(other)
                        cluster_keywords.update(other_keywords)
                        bucket_used.add(other.item_id)
                
                # 生成话题标签
                topic_label = self._generate_topic_label(cluster_keywords)
                
                # 创建簇
                cluster = TopicCluster(
                    cluster_id=f"cluster_{uuid.uuid4().hex[:6]}",
                    topic_label=topic_label,
                    items=cluster_items,
                    keywords=list(cluster_keywords)[:5],  # 最多5个关键词
                    dominant_bucket=bucket_type,
                )
                clusters.append(cluster)
            
            used_item_ids.update(bucket_used)
        
        return clusters
    
    def _calculate_similarity(
        self, keywords1: set[str], keywords2: set[str]
    ) -> float:
        """计算关键词集合的相似度（Jaccard系数）"""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_topic_label(self, keywords: set[str]) -> str:
        """生成话题标签"""
        if not keywords:
            return "未分类话题"
        
        # 取前3个关键词作为标签
        top_keywords = list(keywords)[:3]
        return "、".join(top_keywords)
    
    def _evaluate_clusters(self, clusters: list[TopicCluster]) -> None:
        """评估每个簇的质量"""
        for cluster in clusters:
            # 计算平均相关性
            avg_relevance = sum(
                item.relevance_score for item in cluster.items
            ) / len(cluster.items)
            cluster.avg_relevance = avg_relevance
            
            # 计算簇内聚性（项目间的相似度）
            coherence = self._calculate_coherence(cluster)
            cluster.coherence = coherence
            
            # 计算优先级
            priority = self._calculate_priority(cluster)
            cluster.priority = priority
    
    def _calculate_coherence(self, cluster: TopicCluster) -> float:
        """计算簇内聚性"""
        if len(cluster.items) <= 1:
            return 1.0
        
        # 提取所有项的关键词
        all_keywords: list[set[str]] = []
        for item in cluster.items:
            all_keywords.append(self._extract_keywords(item.content))
        
        # 计算两两相似度的平均值
        similarities: list[float] = []
        for i, kw1 in enumerate(all_keywords):
            for kw2 in all_keywords[i+1:]:
                similarities.append(self._calculate_similarity(kw1, kw2))
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _calculate_priority(self, cluster: TopicCluster) -> float:
        """计算提炼优先级"""
        factors: list[float] = []
        
        # 1. 平均相关性权重 (40%)
        factors.append(cluster.avg_relevance * 0.4)
        
        # 2. 簇内聚性权重 (20%)
        factors.append(cluster.coherence * 0.2)
        
        # 3. 项目数量权重 (20%) - 越多越重要
        count_factor = min(len(cluster.items) / 5.0, 1.0)
        factors.append(count_factor * 0.2)
        
        # 4. 桶类型权重 (20%)
        bucket_weights: dict[SemanticBucketType, float] = {
            SemanticBucketType.TASK_CONTEXT: 0.95,
            SemanticBucketType.USER_INTENT: 0.90,
            SemanticBucketType.DECISION_CONTEXT: 0.85,
            SemanticBucketType.KNOWLEDGE_GAP: 0.75,
            SemanticBucketType.EMOTIONAL_TRACE: 0.60,
        }
        bucket_weight = bucket_weights.get(
            cluster.dominant_bucket, 0.5
        ) if cluster.dominant_bucket else 0.5
        factors.append(bucket_weight * 0.2)
        
        return sum(factors)
    
    def _discover_relations(
        self,
        clusters: list[TopicCluster],
        item_keywords: dict[str, set[str]],
    ) -> list[TopicRelation]:
        """发现话题间的关联"""
        relations: list[TopicRelation] = []
        
        for i, cluster1 in enumerate(clusters):
            for cluster2 in clusters[i+1:]:
                # 计算簇间相似度
                kw1 = set(cluster1.keywords)
                kw2 = set(cluster2.keywords)
                similarity = self._calculate_similarity(kw1, kw2)
                
                # 发现关联
                if similarity >= 0.3:
                    # 判断关联类型
                    relation_type = self._determine_relation_type(
                        cluster1, cluster2, similarity
                    )
                    
                    relations.append(TopicRelation(
                        source_cluster=cluster1.cluster_id,
                        target_cluster=cluster2.cluster_id,
                        relation_type=relation_type,
                        strength=similarity,
                        evidence=list(kw1 & kw2)[:3],
                    ))
        
        return relations
    
    def _determine_relation_type(
        self,
        cluster1: TopicCluster,
        cluster2: TopicCluster,
        similarity: float,
    ) -> str:
        """判断关联类型"""
        # 高相似度 → 相似关系
        if similarity >= 0.5:
            return "similar"
        
        # 根据桶类型判断依赖关系
        dependency_pairs = [
            (SemanticBucketType.USER_INTENT, SemanticBucketType.DECISION_CONTEXT),
            (SemanticBucketType.TASK_CONTEXT, SemanticBucketType.KNOWLEDGE_GAP),
            (SemanticBucketType.TASK_CONTEXT, SemanticBucketType.DECISION_CONTEXT),
        ]
        
        if cluster1.dominant_bucket and cluster2.dominant_bucket:
            for t1, t2 in dependency_pairs:
                if (cluster1.dominant_bucket == t1 and cluster2.dominant_bucket == t2):
                    return "dependency"
                if (cluster2.dominant_bucket == t1 and cluster1.dominant_bucket == t2):
                    return "dependency"
        
        return "related"
    
    def _make_extraction_decisions(
        self, clusters: list[TopicCluster]
    ) -> None:
        """生成提炼决策"""
        for cluster in clusters:
            # 决策1: 优先级过低 → 跳过
            if cluster.priority < self._priority_threshold:
                cluster.should_extract = False
                cluster.skip_reason = f"优先级过低 ({cluster.priority:.2f})"
                continue
            
            # 决策2: 内聚性过低且项目少 → 跳过
            if cluster.coherence < self._coherence_threshold and len(cluster.items) < 3:
                cluster.should_extract = False
                cluster.skip_reason = f"内聚性过低 ({cluster.coherence:.2f}) 且上下文不足"
                continue
            
            # 决策3: 相关性过低 → 跳过
            if cluster.avg_relevance < 0.3:
                cluster.should_extract = False
                cluster.skip_reason = f"相关性过低 ({cluster.avg_relevance:.2f})"
                continue
    
    def _determine_order(
        self,
        clusters: list[TopicCluster],
        relations: list[TopicRelation],
    ) -> list[str]:
        """确定提炼顺序"""
        # 只考虑需要提炼的簇
        valid_clusters = [c for c in clusters if c.should_extract]
        
        # 按优先级排序
        valid_clusters.sort(key=lambda x: x.priority, reverse=True)
        
        # 考虑依赖关系：被依赖的先提炼
        order: list[str] = []
        added: set[str] = set()
        
        # 构建依赖图
        dependents: dict[str, list[str]] = {}
        for r in relations:
            if r.relation_type == "dependency":
                if r.target_cluster not in dependents:
                    dependents[r.target_cluster] = []
                dependents[r.target_cluster].append(r.source_cluster)
        
        # 拓扑排序
        def add_with_dependencies(cluster_id: str) -> None:
            if cluster_id in added:
                return
            
            # 先添加依赖项
            if cluster_id in dependents:
                for dep_id in dependents[cluster_id]:
                    add_with_dependencies(dep_id)
            
            order.append(cluster_id)
            added.add(cluster_id)
        
        for cluster in valid_clusters:
            add_with_dependencies(cluster.cluster_id)
        
        return order
    
    def _calculate_confidence(self, clusters: list[TopicCluster]) -> float:
        """计算决策置信度"""
        if not clusters:
            return 0.0
        
        valid_clusters = [c for c in clusters if c.should_extract]
        if not valid_clusters:
            return 0.0
        
        # 基于平均优先级和内聚性
        avg_priority = sum(c.priority for c in valid_clusters) / len(valid_clusters)
        avg_coherence = sum(c.coherence for c in valid_clusters) / len(valid_clusters)
        
        return (avg_priority * 0.6 + avg_coherence * 0.4)
    
    def _generate_summary(self, decision: ExtractionDecision) -> str:
        """生成分析摘要"""
        parts: list[str] = []
        
        parts.append(f"分析完成：发现 {len(decision.clusters)} 个话题簇")
        parts.append(f"待提炼 {decision.items_to_extract} 项")
        
        if decision.items_to_skip > 0:
            parts.append(f"跳过 {decision.items_to_skip} 项低价值内容")
        
        if decision.clusters_to_merge > 0:
            parts.append(f"{decision.clusters_to_merge} 个簇建议合并")
        
        if decision.relations:
            parts.append(f"发现 {len(decision.relations)} 个话题关联")
        
        return "，".join(parts)
    
    def _create_empty_result(self) -> ShortTermInsightResult:
        """创建空结果"""
        return ShortTermInsightResult(
            insight_id=f"sti_{uuid.uuid4().hex[:8]}",
            decision=ExtractionDecision(
                decision_id=f"ed_{uuid.uuid4().hex[:8]}",
            ),
            summary="无记忆项需要分析",
        )

    def get_stats(self) -> dict[str, Any]:
        """
        获取分析器统计信息
        
        Returns:
            统计信息字典，包含：
            - similarity_threshold: 相似度阈值
            - priority_threshold: 优先级阈值
            - coherence_threshold: 内聚性阈值
            - domain_keywords_count: 领域关键词数量
        """
        return {
            "similarity_threshold": self._similarity_threshold,
            "priority_threshold": self._priority_threshold,
            "coherence_threshold": self._coherence_threshold,
            "domain_keywords_count": len(self._domain_keywords),
        }


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "TopicCluster",
    "TopicRelation",
    "ExtractionDecision",
    "ShortTermInsightResult",
    "ShortTermInsightAnalyzer",
]

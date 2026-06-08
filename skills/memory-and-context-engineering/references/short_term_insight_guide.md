# 短期记忆洞察分析器指南

## 目录

1. [概述](#概述)
2. [设计理念](#设计理念)
3. [核心概念](#核心概念)
4. [工作流程](#工作流程)
5. [话题聚类算法](#话题聚类算法)
6. [提炼决策机制](#提炼决策机制)
7. [使用示例](#使用示例)
8. [最佳实践](#最佳实践)

---

## 概述

短期记忆洞察分析器是 Agent Memory System 的关键组件，负责分析短期记忆并生成提炼决策。

### 核心价值

```
┌─────────────────────────────────────────────────────────────┐
│              短期记忆洞察 = 话题分类引擎                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【不是】给模型的建议                                        │
│  【而是】给提炼器的输入                                      │
│                                                             │
│  核心能力：                                                  │
│  ├── 话题自然涌现（无需预设）                               │
│  ├── 优先级评估（价值判断）                                 │
│  ├── 关联发现（结构化识别）                                 │
│  └── 质量预判（过滤低价值）                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 设计理念

### 为什么不用预设话题？

| 预设话题的问题 | 洞察驱动的优势 |
|---------------|---------------|
| 话题无穷无尽，无法穷举 | 话题自然涌现，无需预设 |
| 边界模糊，分类困难 | 智能聚类，自动发现边界 |
| 需要持续维护话题库 | 持续学习，越用越准 |
| 新话题无法识别 | 自动发现新模式 |

### 核心原则

1. **自然涌现**：从内容中发现话题，而非预设分类
2. **质量导向**：优先提炼高价值内容
3. **关联感知**：发现话题间的依赖关系
4. **精准提炼**：过滤低价值，保证长期记忆质量

---

## 核心概念

### TopicCluster（话题簇）

```python
class TopicCluster(BaseModel):
    """话题簇"""
    cluster_id: str              # 唯一标识
    topic_label: str             # 话题标签（自动生成）
    items: list[ShortTermMemoryItem]  # 属于该话题的记忆项
    
    # 洞察分析结果
    keywords: list[str]          # 核心关键词
    priority: float              # 提炼优先级 (0-1)
    coherence: float             # 簇内聚性 (0-1)
    
    # 提炼决策
    should_extract: bool         # 是否应该提炼
    skip_reason: str             # 跳过原因
    should_merge: bool           # 是否需要合并
    merge_with: list[str]        # 合并目标ID
```

### TopicRelation（话题关联）

```python
class TopicRelation(BaseModel):
    """话题关联"""
    source_cluster: str          # 源簇ID
    target_cluster: str          # 目标簇ID
    relation_type: str           # 关联类型
    strength: float              # 关联强度
    evidence: list[str]          # 证据（共享关键词）
```

关联类型：
- `similar`：高相似度话题
- `dependency`：依赖关系（如任务→决策）
- `related`：一般关联

### ExtractionDecision（提炼决策）

```python
class ExtractionDecision(BaseModel):
    """提炼决策"""
    clusters: list[TopicCluster]     # 话题簇列表
    relations: list[TopicRelation]   # 话题关联列表
    extraction_order: list[str]      # 提炼顺序
    
    # 统计
    total_items: int                 # 总项数
    items_to_extract: int            # 待提炼项数
    items_to_skip: int               # 跳过项数
```

---

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    短期洞察工作流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：短期记忆项列表                                        │
│      ↓                                                      │
│  【1. 关键词提取】                                           │
│      → 识别领域关键词                                       │
│      ↓                                                      │
│  【2. 话题聚类】                                             │
│      → 基于关键词相似度凝聚聚类                             │
│      → 让话题自然涌现                                       │
│      ↓                                                      │
│  【3. 质量评估】                                             │
│      → 计算簇优先级                                         │
│      → 计算簇内聚性                                         │
│      ↓                                                      │
│  【4. 关联发现】                                             │
│      → 发现话题间相似性                                     │
│      → 识别依赖关系                                         │
│      ↓                                                      │
│  【5. 提炼决策】                                             │
│      → 判断是否提炼                                         │
│      → 判断是否合并                                         │
│      → 确定提炼顺序                                         │
│      ↓                                                      │
│  输出：ExtractionDecision                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 话题聚类算法

### 算法：基于关键词相似度的凝聚聚类

```python
def _cluster_by_topic(self, items, item_keywords):
    """
    核心思想：
    1. 不预设话题，让话题自然涌现
    2. 同一桶内的项优先聚在一起
    3. 基于关键词重叠判断相似性
    """
    clusters = []
    
    # 按桶类型分组
    items_by_bucket = group_by_bucket(items)
    
    for bucket_type, bucket_items in items_by_bucket.items():
        used = set()
        
        for item in bucket_items:
            if item in used:
                continue
            
            # 找相似项形成簇
            cluster_items = [item]
            cluster_keywords = item_keywords[item]
            
            for other in bucket_items:
                if other in used:
                    continue
                
                # 计算相似度（Jaccard系数）
                similarity = jaccard(cluster_keywords, item_keywords[other])
                
                if similarity >= threshold:
                    cluster_items.append(other)
                    cluster_keywords.update(item_keywords[other])
            
            # 生成话题标签
            topic_label = generate_label(cluster_keywords)
            
            clusters.append(TopicCluster(
                topic_label=topic_label,
                items=cluster_items,
                keywords=list(cluster_keywords),
            ))
    
    return clusters
```

### 相似度计算

```python
def jaccard(set1, set2):
    """Jaccard 相似系数"""
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)
```

---

## 提炼决策机制

### 优先级计算

```python
priority = (
    avg_relevance * 0.4 +    # 平均相关性权重
    coherence * 0.2 +        # 簇内聚性权重
    count_factor * 0.2 +     # 项目数量权重
    bucket_weight * 0.2      # 桶类型权重
)
```

### 跳过条件

| 条件 | 阈值 | 原因 |
|------|------|------|
| 优先级过低 | < 0.35 | 价值不足 |
| 内聚性低 + 项目少 | < 0.3 & < 3 | 上下文不足 |
| 相关性过低 | < 0.3 | 信息质量差 |

### 合并条件

当两个簇满足以下条件时建议合并：
- 关键词相似度 ≥ 0.5
- 存在依赖关系（如任务→决策）

### 提炼顺序

采用拓扑排序考虑依赖关系：
1. 被依赖的簇先提炼
2. 同层级按优先级排序

---

## 使用示例

### 基本使用

```python
from scripts.short_term_insight import ShortTermInsightAnalyzer
from scripts.short_term import ShortTermMemoryManager

# 创建管理器和分析器
stm = ShortTermMemoryManager()
analyzer = ShortTermInsightAnalyzer()

# 存储一些记忆
stm.store("电商系统需要用户管理模块", SemanticBucketType.TASK_CONTEXT, 0.9)
stm.store("支付接口怎么对接？", SemanticBucketType.DECISION_CONTEXT, 0.85)
stm.store("数据库选MySQL还是PostgreSQL？", SemanticBucketType.DECISION_CONTEXT, 0.8)
stm.store("对了，我最近在看微服务架构", SemanticBucketType.KNOWLEDGE_GAP, 0.5)

# 分析
items = stm.get_all_items()
insight = analyzer.analyze(items)

# 查看结果
print(insight.summary)
# 输出：分析完成：发现 2 个话题簇，待提炼 3 项，跳过 1 项低价值内容

print(insight.format_for_extractor())
# 输出结构化的提炼决策
```

### 与提炼器集成

```python
from scripts.short_term import AsynchronousExtractor

# 提炼器自动使用洞察分析
extractor = AsynchronousExtractor(stm, ltm)

# 执行提炼
result = extractor.extract()

print(result["summary"])
# 输出：分析完成：发现 2 个话题簇...

print(f"提炼了 {result['items_extracted']} 项")
print(f"跳过了 {result['items_skipped']} 项低价值内容")
```

---

## 最佳实践

### 1. 关键词维护

```python
# 根据业务领域扩展关键词
analyzer._domain_keywords.update([
    "你的业务关键词1",
    "你的业务关键词2",
])
```

### 2. 阈值调优

```python
# 根据实际情况调整阈值
analyzer._similarity_threshold = 0.3   # 聚类相似度阈值
analyzer._priority_threshold = 0.4     # 提炼优先级阈值
analyzer._coherence_threshold = 0.35   # 内聚性阈值
```

### 3. 查看洞察结果

```python
# 获取最近一次提炼的洞察
insight = extractor.get_last_insight()

# 查看话题簇
for cluster in insight.decision.clusters:
    print(f"话题: {cluster.topic_label}")
    print(f"  项目数: {len(cluster.items)}")
    print(f"  优先级: {cluster.priority:.2f}")
    print(f"  提炼: {'是' if cluster.should_extract else '否'}")
```

---

## 总结

短期记忆洞察分析器实现了：

1. ✅ **话题自然涌现**：无需预设，从内容中发现
2. ✅ **质量优先**：过滤低价值，保证长期记忆质量
3. ✅ **关联感知**：发现话题间依赖关系
4. ✅ **精准提炼**：按优先级和依赖顺序提炼

形成了完整的质量闭环：
```
短期洞察 → 精准提炼 → 高质量长期记忆 → 高质量长期洞察
```

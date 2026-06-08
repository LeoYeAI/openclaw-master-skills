# Agent Memory System - 记忆索引与增量同步指南

## 目录

1. [概述](#概述)
2. [记忆索引器](#记忆索引器)
3. [增量同步器](#增量同步器)
4. [短期记忆跨层索引](#短期记忆跨层索引)
5. [与短期记忆的集成](#与短期记忆的集成)
6. [性能优化](#性能优化)
7. [最佳实践](#最佳实践)
8. [API 参考](#api-参考)

---

## 概述

### 问题背景

多轮对话场景下，历史记录动辄几十轮，每次全量读取会消耗大量资源。记忆索引与增量同步机制解决了这个问题：

| 问题 | 解决方案 |
|------|----------|
| 如何快速找到相关对话？ | **记忆索引器** - 倒排索引 + 语义分类 |
| 如何避免重复读取？ | **增量同步器** - 标记已提炼内容 |
| 如何减少读取量？ | 分层读取：热/温/冷数据 |
| 短期记忆如何找到相关长期记忆？ | **跨层关联索引** - 双向链接 |

### 性能指标

| 指标 | 数值 |
|------|------|
| 索引查找时间 | < 1ms |
| 1000 条记忆检索 | < 5ms |
| 内存占用 | ~1MB / 1000 条记忆 |
| 命中率预期 | 60-90% |
| 跨层关联检索 | < 2ms |

---

## 记忆索引器

### 核心结构

```
┌─────────────────────────────────────────────────────────────┐
│                    MemoryIndexer                            │
├─────────────────────────────────────────────────────────────┤
│  倒排索引                                                    │
│  ├── keyword_index: {关键词 → 记忆ID集合}                   │
│  ├── entity_index: {实体 → 记忆ID集合}                      │
│  └── topic_index: {主题 → 记忆ID集合}                       │
│                                                             │
│  正排索引                                                    │
│  └── memory_cache: {记忆ID → 记忆文档}                      │
└─────────────────────────────────────────────────────────────┘
```

### 使用示例

```python
from scripts.memory_index import MemoryIndexer

# 创建索引器（路径由调用方指定）
indexer = MemoryIndexer(storage_path="./memory_data/memory_index")

# 索引记忆
indexer.index(
    memory_id="mem_001",
    content="用户想要实现数据库优化方案",
    topics=["database", "optimization"],
    metadata={"session_id": "sess_001"}
)

# 检索
results = indexer.search("数据库优化", top_k=5)
for r in results:
    print(f"{r.memory_id}: score={r.score}")

# 按关键词检索
ids = indexer.search_by_keywords(["数据库", "优化"])

# 按主题检索
ids = indexer.search_by_topic("database")

# 获取记忆内容
doc = indexer.get_memory("mem_001")
```

### 关键词提取

自动提取中英文关键词：

```python
from scripts.memory_index import TextProcessor

keywords = TextProcessor.extract_keywords("用户想要实现数据库优化 API 设计")
# ['用户', '想要', '实现', '数据', '据库', '库优', '优化', 'api', '设计']

entities = TextProcessor.extract_entities('讨论了"数据库优化"方案，涉及 JWT 认证')
# ['数据库优化', 'JWT']
```

---

## 增量同步器

### 核心结构

```
┌─────────────────────────────────────────────────────────────┐
│                    IncrementalSync                          │
├─────────────────────────────────────────────────────────────┤
│  同步状态                                                    │
│  └── sync_states: {记忆ID → SyncState}                      │
│                                                             │
│  状态类型                                                    │
│  ├── PENDING: 待提炼                                        │
│  ├── EXTRACTING: 提炼中                                     │
│  ├── EXTRACTED: 已提炼 ✓                                    │
│  ├── SKIPPED: 已跳过                                        │
│  └── FAILED: 提炼失败                                       │
└─────────────────────────────────────────────────────────────┘
```

### 使用示例

```python
from scripts.incremental_sync import IncrementalSync, SyncStatus

# 创建同步器（路径由调用方指定）
sync = IncrementalSync(storage_path="./memory_data/sync_state")

# 注册新记忆
sync.register("mem_001", priority=0.8)

# 检查状态
if sync.should_skip("mem_001"):
    print("已提炼，跳过")
elif sync.is_pending("mem_001"):
    print("待提炼")

# 标记提炼
sync.mark_extracting("mem_001")
# ... 执行提炼 ...
sync.mark_extracted("mem_001", target_category="procedural", quality=0.9)

# 获取待提炼列表
unextracted = sync.get_unextracted(limit=10)

# 获取进度
progress = sync.get_extraction_progress()
print(f"提炼进度: {progress:.0%}")
```

### 状态流转

```
PENDING ──→ EXTRACTING ──→ EXTRACTED
    │            │
    │            └──→ FAILED ──→ (重试) ──→ PENDING
    │
    └──→ SKIPPED
```

---

## 短期记忆跨层索引

### 核心问题

```
用户说："继续上次那个电商系统"

┌─────────────────────────────────────────────────────────────┐
│                    跨层关联检索需求                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  当前会话（短期记忆）                                        │
│  └── 无"电商系统"上下文（新会话）                           │
│                                                             │
│  历史会话（长期记忆）                                        │
│  └── 有"电商系统"相关记忆                                   │
│                                                             │
│  需求：                                                      │
│  1. 短期记忆能快速检索相关长期记忆                          │
│  2. 建立双向关联索引                                        │
│  3. 激活历史上下文                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 双向关联索引结构

```
┌─────────────────────────────────────────────────────────────┐
│                    跨层关联索引                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  短期记忆管理器                                              │
│  ├── _stm_to_ltm_links: {stm_id → [ltm_id, ...]}           │
│  │   └── 短期记忆 → 相关长期记忆                            │
│  │                                                          │
│  └── _ltm_to_stm_links: {ltm_id → [stm_id, ...]}           │
│      └── 长期记忆 → 关联的短期记忆                          │
│                                                             │
│  记忆索引器                                                  │
│  └── 提供检索能力                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 使用示例

```python
from scripts.short_term import ShortTermMemoryManager
from scripts.memory_index import MemoryIndexer

# 初始化
stm = ShortTermMemoryManager()
indexer = MemoryIndexer()

# 关联索引器
stm.set_memory_indexer(indexer)

# 方式1: 存储后手动关联
item_id = stm.store("继续电商系统开发", SemanticBucketType.TASK_CONTEXT, 0.9)
# 检索相关长期记忆
results = stm.search_long_term_memory("电商系统", top_k=5)
# 建立关联
for result in results:
    stm.link_to_long_term(item_id, result["memory_id"])

# 方式2: 存储时自动关联（推荐）
item_id, linked_ids = stm.store_with_auto_link(
    content="继续电商系统开发",
    bucket_type=SemanticBucketType.TASK_CONTEXT,
    relevance_score=0.9,
    auto_link_threshold=0.3,  # 相似度阈值
)

# 查看关联
related_ltm = stm.get_related_long_term_memories(item_id)
print(f"关联了 {len(related_ltm)} 条长期记忆")

# 查看统计
stats = stm.get_cross_layer_stats()
print(f"总关联数: {stats['total_links']}")
```

### 典型场景

#### 场景1: 新会话继续旧话题

```python
# 用户: "继续上次那个电商系统"

# 1. 检索长期记忆
results = stm.search_long_term_memory("电商系统", top_k=3)

# 2. 存储当前意图并关联
item_id, linked_ids = stm.store_with_auto_link(
    content="继续电商系统开发",
    bucket_type=SemanticBucketType.USER_INTENT,
    relevance_score=0.9,
)

# 3. 激活相关长期记忆
activated_memories = [indexer.get_memory(mid) for mid in linked_ids]
```

#### 场景2: 追踪话题演化

```python
# 用户多次提到同一话题

# 存储3次相关内容
item1, _ = stm.store_with_auto_link("电商系统用户管理", TASK_CONTEXT, 0.8)
item2, _ = stm.store_with_auto_link("电商系统订单模块", TASK_CONTEXT, 0.8)
item3, _ = stm.store_with_auto_link("电商系统支付接口", TASK_CONTEXT, 0.8)

# 查看某条长期记忆被多少短期记忆关联
ltm_id = linked_ids[0]
related_stm = stm.get_related_short_term_items(ltm_id)
print(f"该长期记忆被 {len(related_stm)} 条短期记忆关联")
# 可以用于计算话题热度
```

---

## 与短期记忆的集成

### 集成模式

```python
from scripts.short_term import ShortTermMemoryManager
from scripts.memory_index import MemoryIndexer
from scripts.incremental_sync import IncrementalSync

class EnhancedShortTermMemory:
    """增强的短期记忆管理器"""

    def __init__(self):
        self.manager = ShortTermMemoryManager()
        self.indexer = MemoryIndexer()
        self.sync = IncrementalSync()

    def add_memory(self, content: str, semantic_type: str) -> str:
        """添加记忆（自动索引）"""
        # 添加到短期记忆
        item_id, _ = self.manager.classify_and_store(content)

        # 建立索引
        self.indexer.index(
            memory_id=item_id,
            content=content,
            topics=[semantic_type],
        )

        # 注册同步状态
        self.sync.register(item_id)

        return item_id

    def search_relevant(self, query: str, top_k: int = 5) -> list:
        """检索相关记忆"""
        results = self.indexer.search(query, top_k=top_k)

        # 过滤已提炼的
        return [
            r for r in results
            if not self.sync.should_skip(r.memory_id)
        ]

    def get_unextracted_for_extraction(self, limit: int = 10) -> list:
        """获取待提炼的记忆（用于异步提炼）"""
        unextracted_ids = self.sync.get_unextracted(limit=limit)

        memories = []
        for mem_id in unextracted_ids:
            doc = self.indexer.get_memory(mem_id)
            if doc:
                memories.append(doc)

        return memories

    def mark_extracted(self, memory_id: str, target: str):
        """标记已提炼"""
        self.sync.mark_extracted(memory_id, target)
```

---

## 性能优化

### 1. 内存缓存

```python
# 启动时加载所有记忆到内存
indexer = MemoryIndexer()

# 检索时只访问内存，无文件 I/O
results = indexer.search("查询内容")
```

### 2. 增量更新

```python
# 只更新变化的记忆
indexer.index(new_memory_id, new_content)  # 添加
indexer.remove(old_memory_id)  # 删除

# 不需要重建全量索引
```

### 3. 批量处理

```python
# 批量索引
for mem in memories:
    indexer.index(mem.id, mem.content, mem.topics)

# 批量检索
all_results = []
for query in queries:
    results = indexer.search(query, top_k=3)
    all_results.extend(results)
```

### 4. 分层读取

```python
def get_context_for_task(query: str):
    # 第1层：最近 5 轮（必读）
    recent = get_recent_conversations(5)

    # 第2层：检索命中的历史
    relevant = indexer.search(query, top_k=5)

    # 第3层：相关长期记忆
    long_term = get_long_term_memory(query)

    # 过滤已提炼的
    unextracted = [r for r in relevant if not sync.should_skip(r.memory_id)]

    return recent + unextracted + long_term
```

---

## 最佳实践

### 1. 索引时机

```python
# ✓ 推荐：添加记忆时立即索引
def add_memory(content):
    mem_id = store.save(content)
    indexer.index(mem_id, content)
    return mem_id

# ✗ 不推荐：定期批量重建
def rebuild_all():
    all_memories = store.get_all()
    indexer.clear()
    for mem in all_memories:
        indexer.index(mem.id, mem.content)
```

### 2. 同步状态管理

```python
# 提炼流程
def extract_memory(mem_id):
    # 1. 检查状态
    if sync.should_skip(mem_id):
        return None

    # 2. 标记提炼中
    sync.mark_extracting(mem_id)

    try:
        # 3. 执行提炼
        result = do_extraction(mem_id)

        # 4. 标记完成
        sync.mark_extracted(mem_id, result.category)
        return result

    except Exception as e:
        sync.mark_failed(mem_id, str(e))
        return None
```

### 3. 检索策略

```python
def smart_search(query: str):
    # 多条件组合
    keywords = TextProcessor.extract_keywords(query)
    entities = TextProcessor.extract_entities(query)

    # 关键词检索
    by_kw = indexer.search_by_keywords(keywords, mode="or")

    # 实体检索（更精准）
    by_ent = indexer.search_by_entities(entities)

    # 合并结果，实体匹配权重更高
    results = merge_with_weights(by_kw, by_ent, kw_weight=1.0, ent_weight=2.0)

    return results
```

---

## API 参考

### MemoryIndexer

#### 初始化

```python
MemoryIndexer(storage_path: str = "./memory_index")
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `index(memory_id, content, topics?, metadata?)` | 记忆ID, 内容, 主题, 元数据 | `None` | 索引单个记忆 |
| `remove(memory_id)` | 记忆ID | `bool` | 移除索引 |
| `search(query, top_k?, mode?)` | 查询文本, 数量, 模式 | `list[SearchResult]` | 检索 |
| `search_by_keywords(keywords, mode?)` | 关键词列表, 模式 | `list[str]` | 按关键词检索 |
| `search_by_entities(entities)` | 实体列表 | `list[str]` | 按实体检索 |
| `search_by_topic(topic)` | 主题 | `list[str]` | 按主题检索 |
| `get_memory(memory_id)` | 记忆ID | `MemoryDocument \| None` | 获取记忆文档 |
| `get_stats()` | 无 | `IndexStats` | 获取统计 |
| `clear()` | 无 | `None` | 清空索引 |

### IncrementalSync

#### 初始化

```python
IncrementalSync(storage_path: str = "./sync_state")
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `register(memory_id, priority?)` | 记忆ID, 优先级 | `None` | 注册记忆 |
| `mark_extracting(memory_id)` | 记忆ID | `bool` | 标记提炼中 |
| `mark_extracted(memory_id, target, quality?, notes?)` | 记忆ID, 目标, 质量, 备注 | `bool` | 标记已提炼 |
| `mark_skipped(memory_id, reason?)` | 记忆ID, 原因 | `bool` | 标记已跳过 |
| `mark_failed(memory_id, error?)` | 记忆ID, 错误 | `bool` | 标记失败 |
| `should_skip(memory_id)` | 记忆ID | `bool` | 是否应跳过 |
| `is_pending(memory_id)` | 记忆ID | `bool` | 是否待提炼 |
| `get_unextracted(limit?)` | 数量限制 | `list[str]` | 获取未提炼列表 |
| `get_extracted()` | 无 | `list[str]` | 获取已提炼列表 |
| `get_extraction_progress()` | 无 | `float` | 获取提炼进度 |
| `get_stats()` | 无 | `SyncStats` | 获取统计 |

---

## 总结

记忆索引与增量同步机制解决了多轮对话场景下的核心问题：

1. **快速检索**：倒排索引实现 O(1) 关键词查找
2. **避免重复**：增量同步标记已提炼内容
3. **分层读取**：热/温/冷数据分层处理

这些机制确保了系统在长对话、多任务场景下的高效运行。

"""
Agent Memory System - 记忆索引模块

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

性能说明：
- 倒排索引查找: O(1) ~ O(min(m,n))
- 1000 条记忆检索: < 5ms
- 内存占用: ~1MB / 1000 条记忆
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# 常量定义
# ============================================================================

# 停用词（中英文常见）
STOPWORDS: set[str] = {
    # 中文
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
    "自己", "这", "那", "什么", "怎么", "这个", "那个", "可以", "可能", "应该",
    # 英文
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "this", "that", "these", "those", "what", "which", "who", "whom",
    "and", "or", "but", "if", "then", "else", "when", "where", "why", "how",
    "for", "to", "of", "in", "on", "at", "by", "with", "from", "about",
}

# 最小关键词长度
MIN_KEYWORD_LENGTH: int = 2

# 实体识别模式
ENTITY_PATTERNS: list[str] = [
    r'"([^"]+)"',           # 双引号内容
    r"'([^']+)'",           # 单引号内容
    r'【([^】]+)】',         # 中文方括号
    r'《([^》]+)》',         # 中文书名号
    r'[A-Z][a-z]+[A-Z]\w+',  # CamelCase
    r'\b[A-Z]{2,}\b',        # 大写缩写（如 API, HTTP）
]


# ============================================================================
# 数据模型
# ============================================================================


class IndexStats(BaseModel):
    """索引统计"""

    total_memories: int = 0
    total_keywords: int = 0
    total_entities: int = 0
    total_topics: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)


class SearchResult(BaseModel):
    """检索结果"""

    memory_id: str
    score: float
    matched_keywords: list[str] = Field(default_factory=list)
    matched_entities: list[str] = Field(default_factory=list)
    matched_topics: list[str] = Field(default_factory=list)


class MemoryDocument(BaseModel):
    """记忆文档（用于索引）"""

    memory_id: str
    content: str
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 文本处理工具
# ============================================================================


class TextProcessor:
    """
    文本处理器

    提供关键词提取、实体识别等功能
    """

    # 中文分词正则（简单实现）
    _chinese_pattern: re.Pattern[str] = re.compile(r'[\u4e00-\u9fff]+')
    _word_pattern: re.Pattern[str] = re.compile(r'\b[a-zA-Z][a-zA-Z0-9_-]*\b')

    @classmethod
    def extract_keywords(cls, text: str, min_length: int = MIN_KEYWORD_LENGTH) -> list[str]:
        """
        提取关键词

        Args:
            text: 文本内容
            min_length: 最小关键词长度

        Returns:
            关键词列表
        """
        keywords: list[str] = []

        # 提取中文词汇（简单分词：连续中文字符）
        chinese_matches: list[str] = cls._chinese_pattern.findall(text)
        for match in chinese_matches:
            # 对长中文串进行切分（每 2-4 字作为一个可能的词）
            if len(match) <= 4:
                word: str = match.lower()
                if len(word) >= min_length and word not in STOPWORDS:
                    keywords.append(word)
            else:
                # 滑动窗口切分
                for i in range(len(match) - 1):
                    word = match[i:i + 2].lower()
                    if word not in STOPWORDS:
                        keywords.append(word)

        # 提取英文单词
        english_matches: list[str] = cls._word_pattern.findall(text)
        for word in english_matches:
            word_lower: str = word.lower()
            if len(word_lower) >= min_length and word_lower not in STOPWORDS:
                keywords.append(word_lower)

        # 去重并保持顺序
        seen: set[str] = set()
        unique_keywords: list[str] = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords

    @classmethod
    def extract_entities(cls, text: str) -> list[str]:
        """
        提取实体

        Args:
            text: 文本内容

        Returns:
            实体列表
        """
        entities: list[str] = []

        for pattern in ENTITY_PATTERNS:
            matches: list[tuple[str, ...]] = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    entities.extend(match)
                else:
                    entities.append(match)

        # 去重
        return list(set(entities))

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """
        标准化文本

        Args:
            text: 原始文本

        Returns:
            标准化后的文本
        """
        # 转小写
        text = text.lower()
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


# ============================================================================
# 记忆索引器
# ============================================================================


class MemoryIndexer:
    """
    记忆索引器

    提供高效的倒排索引和检索能力
    """

    def __init__(
        self,
        storage_path: str,
    ) -> None:
        """
        初始化记忆索引器

        Args:
            storage_path: 索引存储路径（由调用方指定，无默认值）
        """
        self.storage_path: Path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 倒排索引
        self._keyword_index: dict[str, set[str]] = {}
        self._entity_index: dict[str, set[str]] = {}
        self._topic_index: dict[str, set[str]] = {}

        # 正排索引（记忆缓存）
        self._memory_cache: dict[str, MemoryDocument] = {}

        # 统计
        self._stats: IndexStats = IndexStats()

        # 加载已有索引
        self._load_index()

    def _load_index(self) -> None:
        """加载已有索引"""
        index_file: Path = self.storage_path / "index.json"

        if not index_file.exists():
            return

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            # 恢复索引
            for kw, ids in data.get("keyword_index", {}).items():
                self._keyword_index[kw] = set(ids)

            for ent, ids in data.get("entity_index", {}).items():
                self._entity_index[ent] = set(ids)

            for topic, ids in data.get("topic_index", {}).items():
                self._topic_index[topic] = set(ids)

            # 恢复缓存
            for mem_id, doc_data in data.get("memory_cache", {}).items():
                self._memory_cache[mem_id] = MemoryDocument.model_validate(doc_data)

            # 更新统计
            self._stats = IndexStats(
                total_memories=len(self._memory_cache),
                total_keywords=len(self._keyword_index),
                total_entities=len(self._entity_index),
                total_topics=len(self._topic_index),
            )

        except (json.JSONDecodeError, ValueError):
            pass

    def _save_index(self) -> None:
        """保存索引"""
        index_file: Path = self.storage_path / "index.json"

        data: dict[str, Any] = {
            "keyword_index": {k: list(v) for k, v in self._keyword_index.items()},
            "entity_index": {k: list(v) for k, v in self._entity_index.items()},
            "topic_index": {k: list(v) for k, v in self._topic_index.items()},
            "memory_cache": {
                k: v.model_dump(mode="json") for k, v in self._memory_cache.items()
            },
            "stats": self._stats.model_dump(mode="json"),
        }

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def index(
        self,
        memory_id: str,
        content: str,
        topics: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        索引单个记忆

        Args:
            memory_id: 记忆ID
            content: 记忆内容
            topics: 主题列表（可选）
            metadata: 元数据（可选）
        """
        # 如果已存在，先移除旧索引
        if memory_id in self._memory_cache:
            self.remove(memory_id)

        # 提取关键词和实体
        keywords: list[str] = TextProcessor.extract_keywords(content)
        entities: list[str] = TextProcessor.extract_entities(content)
        topic_list: list[str] = topics or []

        # 创建文档
        doc: MemoryDocument = MemoryDocument(
            memory_id=memory_id,
            content=content,
            keywords=keywords,
            entities=entities,
            topics=topic_list,
            metadata=metadata or {},
        )

        # 更新倒排索引
        for kw in keywords:
            self._keyword_index.setdefault(kw, set()).add(memory_id)

        for ent in entities:
            self._entity_index.setdefault(ent, set()).add(memory_id)

        for topic in topic_list:
            self._topic_index.setdefault(topic, set()).add(memory_id)

        # 更新缓存
        self._memory_cache[memory_id] = doc

        # 更新统计
        self._stats.total_memories = len(self._memory_cache)
        self._stats.total_keywords = len(self._keyword_index)
        self._stats.total_entities = len(self._entity_index)
        self._stats.total_topics = len(self._topic_index)
        self._stats.last_updated = datetime.now()

        # 保存
        self._save_index()

    def remove(self, memory_id: str) -> bool:
        """
        移除记忆索引

        Args:
            memory_id: 记忆ID

        Returns:
            是否成功
        """
        if memory_id not in self._memory_cache:
            return False

        doc: MemoryDocument = self._memory_cache[memory_id]

        # 从倒排索引中移除
        for kw in doc.keywords:
            if kw in self._keyword_index:
                self._keyword_index[kw].discard(memory_id)
                if not self._keyword_index[kw]:
                    del self._keyword_index[kw]

        for ent in doc.entities:
            if ent in self._entity_index:
                self._entity_index[ent].discard(memory_id)
                if not self._entity_index[ent]:
                    del self._entity_index[ent]

        for topic in doc.topics:
            if topic in self._topic_index:
                self._topic_index[topic].discard(memory_id)
                if not self._topic_index[topic]:
                    del self._topic_index[topic]

        # 从缓存中移除
        del self._memory_cache[memory_id]

        # 更新统计
        self._stats.total_memories = len(self._memory_cache)
        self._stats.total_keywords = len(self._keyword_index)
        self._stats.total_entities = len(self._entity_index)
        self._stats.total_topics = len(self._topic_index)

        # 保存
        self._save_index()

        return True

    def search(
        self,
        query: str,
        top_k: int = 10,
        mode: str = "and",
    ) -> list[SearchResult]:
        """
        检索相关记忆

        Args:
            query: 查询文本
            top_k: 返回数量
            mode: 检索模式（"and" 或 "or"）

        Returns:
            检索结果列表
        """
        # 提取查询关键词
        query_keywords: list[str] = TextProcessor.extract_keywords(query)
        query_entities: list[str] = TextProcessor.extract_entities(query)

        if not query_keywords and not query_entities:
            return []

        # 收集候选记忆
        candidate_scores: dict[str, float] = {}
        matched_info: dict[str, dict[str, list[str]]] = {}

        # 关键词匹配
        for kw in query_keywords:
            mem_ids: set[str] | None = self._keyword_index.get(kw)
            if mem_ids:
                for mem_id in mem_ids:
                    if mem_id not in candidate_scores:
                        candidate_scores[mem_id] = 0.0
                        matched_info[mem_id] = {"keywords": [], "entities": [], "topics": []}
                    candidate_scores[mem_id] += 1.0
                    matched_info[mem_id]["keywords"].append(kw)

        # 实体匹配（权重更高）
        for ent in query_entities:
            mem_ids_ent: set[str] | None = self._entity_index.get(ent)
            if mem_ids_ent:
                for mem_id in mem_ids_ent:
                    if mem_id not in candidate_scores:
                        candidate_scores[mem_id] = 0.0
                        matched_info[mem_id] = {"keywords": [], "entities": [], "topics": []}
                    candidate_scores[mem_id] += 2.0  # 实体权重更高
                    matched_info[mem_id]["entities"].append(ent)

        # AND 模式：只保留匹配所有关键词的记忆
        if mode == "and" and query_keywords:
            required_keywords: set[str] = set(query_keywords)
            filtered_scores: dict[str, float] = {}
            for mem_id, score in candidate_scores.items():
                doc: MemoryDocument | None = self._memory_cache.get(mem_id)
                if doc:
                    doc_keywords: set[str] = set(doc.keywords)
                    if required_keywords.issubset(doc_keywords):
                        filtered_scores[mem_id] = score
            candidate_scores = filtered_scores

        # 归一化分数
        max_score: float = max(candidate_scores.values()) if candidate_scores else 1.0

        # 构建结果
        results: list[SearchResult] = []
        for mem_id, score in candidate_scores.items():
            normalized_score: float = score / max_score
            info: dict[str, list[str]] = matched_info.get(mem_id, {"keywords": [], "entities": [], "topics": []})

            results.append(
                SearchResult(
                    memory_id=mem_id,
                    score=normalized_score,
                    matched_keywords=info["keywords"],
                    matched_entities=info["entities"],
                    matched_topics=info["topics"],
                )
            )

        # 排序并返回 top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def search_by_keywords(
        self,
        keywords: list[str],
        mode: str = "or",
    ) -> list[str]:
        """
        按关键词检索

        Args:
            keywords: 关键词列表
            mode: 检索模式

        Returns:
            记忆ID列表
        """
        if not keywords:
            return []

        result_sets: list[set[str]] = []

        for kw in keywords:
            kw_lower: str = kw.lower()
            mem_ids: set[str] | None = self._keyword_index.get(kw_lower)
            if mem_ids:
                result_sets.append(mem_ids)

        if not result_sets:
            return []

        if mode == "and":
            intersection: set[str] = result_sets[0]
            for rs in result_sets[1:]:
                intersection = intersection & rs
            return list(intersection)
        else:
            union: set[str] = set()
            for rs in result_sets:
                union = union | rs
            return list(union)

    def search_by_entities(
        self,
        entities: list[str],
    ) -> list[str]:
        """
        按实体检索

        Args:
            entities: 实体列表

        Returns:
            记忆ID列表
        """
        if not entities:
            return []

        result_sets: list[set[str]] = []

        for ent in entities:
            mem_ids: set[str] | None = self._entity_index.get(ent)
            if mem_ids:
                result_sets.append(mem_ids)

        if not result_sets:
            return []

        # 取交集
        intersection_ent: set[str] = result_sets[0]
        for rs in result_sets[1:]:
            intersection_ent = intersection_ent & rs

        return list(intersection_ent)

    def search_by_topic(
        self,
        topic: str,
    ) -> list[str]:
        """
        按主题检索

        Args:
            topic: 主题

        Returns:
            记忆ID列表
        """
        mem_ids_topic: set[str] | None = self._topic_index.get(topic)
        return list(mem_ids_topic) if mem_ids_topic else []

    def get_memory(self, memory_id: str) -> Optional[MemoryDocument]:
        """
        获取记忆文档

        Args:
            memory_id: 记忆ID

        Returns:
            记忆文档
        """
        return self._memory_cache.get(memory_id)

    def get_all_memory_ids(self) -> list[str]:
        """
        获取所有记忆ID

        Returns:
            记忆ID列表
        """
        return list(self._memory_cache.keys())

    def get_stats(self) -> IndexStats:
        """
        获取索引统计

        Returns:
            索引统计
        """
        return self._stats

    def clear(self) -> None:
        """
        清空索引
        """
        self._keyword_index.clear()
        self._entity_index.clear()
        self._topic_index.clear()
        self._memory_cache.clear()
        self._stats = IndexStats()
        self._save_index()

    def get_keywords_for_memory(self, memory_id: str) -> list[str]:
        """
        获取记忆的关键词

        Args:
            memory_id: 记忆ID

        Returns:
            关键词列表
        """
        doc: MemoryDocument | None = self._memory_cache.get(memory_id)
        return doc.keywords if doc else []

    def get_entities_for_memory(self, memory_id: str) -> list[str]:
        """
        获取记忆的实体

        Args:
            memory_id: 记忆ID

        Returns:
            实体列表
        """
        doc_ent: MemoryDocument | None = self._memory_cache.get(memory_id)
        return doc_ent.entities if doc_ent else []


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "TextProcessor",
    "MemoryIndexer",
    "MemoryDocument",
    "SearchResult",
    "IndexStats",
    "STOPWORDS",
    "MIN_KEYWORD_LENGTH",
]

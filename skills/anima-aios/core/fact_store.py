#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 Anima-AIOS Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Anima AIOS v6.0 - Fact Store

统一的事实存储层，管理 L2（episodic）和 L3（semantic）记忆的读写。
移植自 Z 的 fact-store.js，扩展支持质量评估和衰减元数据。

Author: 清禾
Date: 2026-03-23
Version: 6.0.0
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Literal

logger = logging.getLogger(__name__)

FactType = Literal["episodic", "semantic"]
QualityGrade = Literal["S", "A", "B", "C", "pending"]


class Fact:
    """单条事实记录"""
    
    def __init__(self, fact_id: str, fact_type: FactType, content: str,
                 quality: QualityGrade = "pending", tags: List[str] = None,
                 source: str = "", agent: str = "", created_at: str = "",
                 metadata: Dict = None):
        self.fact_id = fact_id
        self.fact_type = fact_type
        self.content = content
        self.quality = quality
        self.tags = tags or []
        self.source = source
        self.agent = agent
        self.created_at = created_at or datetime.now().isoformat()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "fact_id": self.fact_id,
            "type": self.fact_type,
            "content": self.content,
            "quality": self.quality,
            "tags": self.tags,
            "source": self.source,
            "agent": self.agent,
            "created_at": self.created_at,
            "metadata": self.metadata
        }
    
    def to_markdown(self) -> str:
        """序列化为 Markdown 文件格式"""
        tags_str = json.dumps(self.tags, ensure_ascii=False)
        meta_lines = [
            "---",
            f"type: {self.fact_type}",
            f"quality: {self.quality}",
            f"source: {self.source}",
            f"agent: {self.agent}",
            f"created_at: {self.created_at}",
            f"tags: {tags_str}",
        ]
        if self.metadata:
            for k, v in self.metadata.items():
                meta_lines.append(f"{k}: {v}")
        meta_lines.append("---")
        meta_lines.append("")
        meta_lines.append(self.content)
        return '\n'.join(meta_lines)
    
    @classmethod
    def from_file(cls, filepath: Path) -> Optional['Fact']:
        """从 Markdown 文件解析 Fact"""
        try:
            text = filepath.read_text(encoding='utf-8')
            
            # 解析 frontmatter
            if not text.startswith('---'):
                return cls(
                    fact_id=filepath.stem,
                    fact_type="episodic",
                    content=text.strip(),
                    source=str(filepath)
                )
            
            parts = text.split('---', 2)
            if len(parts) < 3:
                return None
            
            frontmatter = parts[1].strip()
            content = parts[2].strip()
            
            meta = {}
            for line in frontmatter.splitlines():
                if ':' in line:
                    key, _, value = line.partition(':')
                    key = key.strip()
                    value = value.strip()
                    meta[key] = value
            
            # 解析 tags
            tags = []
            tags_raw = meta.get('tags', '[]')
            try:
                tags = json.loads(tags_raw)
            except Exception:
                tags = [t.strip() for t in tags_raw.strip('[]').split(',') if t.strip()]
            
            return cls(
                fact_id=filepath.stem,
                fact_type=meta.get('type', 'episodic'),
                content=content,
                quality=meta.get('quality', 'pending'),
                tags=tags,
                source=meta.get('source', ''),
                agent=meta.get('agent', ''),
                created_at=meta.get('created_at', ''),
                metadata={k: v for k, v in meta.items()
                          if k not in ('type', 'quality', 'source', 'agent', 'created_at', 'tags')}
            )
        except Exception as e:
            logger.warning(f"解析 fact 文件失败 {filepath}: {e}")
            return None


class FactStore:
    """
    事实存储管理器
    
    管理 L2（episodic）和 L3（semantic）的读写操作。
    """
    
    def __init__(self, agent_name: str, facts_base: str = None):
        self.agent_name = agent_name
        self.base_dir = Path(facts_base) / agent_name / "facts"
        self.episodic_dir = self.base_dir / "episodic"
        self.semantic_dir = self.base_dir / "semantic"
        
        # 确保目录存在
        self.episodic_dir.mkdir(parents=True, exist_ok=True)
        self.semantic_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_dir(self, fact_type: FactType) -> Path:
        return self.episodic_dir if fact_type == "episodic" else self.semantic_dir
    
    def write(self, fact: Fact) -> str:
        """
        写入一条 fact
        
        Returns:
            写入的文件路径
        """
        target_dir = self._get_dir(fact.fact_type)
        filepath = target_dir / f"{fact.fact_id}.md"
        filepath.write_text(fact.to_markdown(), encoding='utf-8')
        logger.debug(f"写入 fact: {fact.fact_id} ({fact.fact_type})")
        return str(filepath)
    
    def read(self, fact_id: str, fact_type: FactType) -> Optional[Fact]:
        """读取一条 fact"""
        target_dir = self._get_dir(fact_type)
        filepath = target_dir / f"{fact_id}.md"
        if not filepath.exists():
            return None
        return Fact.from_file(filepath)
    
    def list_facts(self, fact_type: FactType, quality: Optional[QualityGrade] = None,
                   limit: int = 100) -> List[Fact]:
        """
        列出 facts
        
        Args:
            fact_type: episodic 或 semantic
            quality: 按质量过滤（可选）
            limit: 最大返回数量
        """
        target_dir = self._get_dir(fact_type)
        facts = []
        
        for filepath in sorted(target_dir.glob("*.md"), reverse=True):
            if len(facts) >= limit:
                break
            
            fact = Fact.from_file(filepath)
            if fact is None:
                continue
            
            if quality and fact.quality != quality:
                continue
            
            facts.append(fact)
        
        return facts
    
    def update_quality(self, fact_id: str, fact_type: FactType, quality: QualityGrade):
        """更新 fact 的质量评级"""
        fact = self.read(fact_id, fact_type)
        if fact is None:
            logger.warning(f"Fact 不存在: {fact_id}")
            return
        
        fact.quality = quality
        self.write(fact)
        logger.debug(f"更新质量: {fact_id} → {quality}")
    
    def create_semantic(self, content: str, source_facts: List[str],
                        tags: List[str] = None, quality: QualityGrade = "B") -> Fact:
        """
        创建 L3 语义记忆（从 L2 提炼而来）
        
        Args:
            content: 提炼后的知识内容
            source_facts: 来源的 L2 fact_id 列表
            tags: 标签
            quality: 质量等级
        
        Returns:
            创建的 Fact
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        fact_id = f"semantic_{timestamp}_{content_hash}"
        
        fact = Fact(
            fact_id=fact_id,
            fact_type="semantic",
            content=content,
            quality=quality,
            tags=tags or [],
            source="distill_engine",
            agent=self.agent_name,
            metadata={"source_facts": json.dumps(source_facts, ensure_ascii=False)}
        )
        
        self.write(fact)
        return fact
    
    def count(self, fact_type: FactType) -> int:
        """统计 fact 数量"""
        target_dir = self._get_dir(fact_type)
        return len(list(target_dir.glob("*.md")))
    
    def search(self, query: str, fact_type: Optional[FactType] = None,
               limit: int = 10) -> List[Fact]:
        """
        简单关键词搜索
        
        Args:
            query: 搜索关键词
            fact_type: 限定类型（可选）
            limit: 最大返回数
        """
        results = []
        query_lower = query.lower()
        
        dirs = []
        if fact_type is None or fact_type == "episodic":
            dirs.append(self.episodic_dir)
        if fact_type is None or fact_type == "semantic":
            dirs.append(self.semantic_dir)
        
        for d in dirs:
            for filepath in sorted(d.glob("*.md"), reverse=True):
                if len(results) >= limit:
                    break
                fact = Fact.from_file(filepath)
                if fact and query_lower in fact.content.lower():
                    results.append(fact)
        
        return results[:limit]

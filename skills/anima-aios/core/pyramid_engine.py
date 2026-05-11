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
Anima AIOS v6.0 - Pyramid Engine

金字塔知识组织引擎。实现自底向上的知识提炼：
  实例层（instances）← 具体事件
    → 规则层（rules）← 从多个实例提炼的规律
      → 模式层（patterns）← 跨领域通用方法论
        → 本体层（ontology）← 核心概念和认知框架

移植自 Z 的 pyramid-abstract.js，适配 Python + LLM。

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

PyramidLevel = Literal["instances", "rules", "patterns", "ontology"]


class PyramidEntry:
    """金字塔条目"""
    
    def __init__(self, entry_id: str, level: PyramidLevel, content: str,
                 topic: str = "", source_ids: List[str] = None,
                 created_at: str = "", metadata: Dict = None):
        self.entry_id = entry_id
        self.level = level
        self.content = content
        self.topic = topic
        self.source_ids = source_ids or []
        self.created_at = created_at or datetime.now().isoformat()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "id": self.entry_id,
            "level": self.level,
            "content": self.content,
            "topic": self.topic,
            "source_ids": self.source_ids,
            "created_at": self.created_at,
            "metadata": self.metadata
        }


class PyramidEngine:
    """
    金字塔知识组织引擎
    
    管理四层知识结构，支持自底向上的自动提炼。
    """
    
    LEVELS = ["instances", "rules", "patterns", "ontology"]
    LEVEL_UP = {"instances": "rules", "rules": "patterns", "patterns": "ontology"}
    
    # 同一主题达到此数量时触发自动提炼
    AUTO_DISTILL_THRESHOLD = 3
    
    def __init__(self, agent_name: str, facts_base: str = None,
                 auto_distill: bool = False, llm_config: Dict = None):
        self.agent_name = agent_name
        self.pyramid_dir = Path(facts_base) / agent_name / "pyramid"
        self.auto_distill = auto_distill
        
        # LLM 客户端（可选）
        self.llm = None
        if llm_config:
            try:
                from distill_engine import LLMClient
                self.llm = LLMClient(llm_config)
            except ImportError:
                pass
        
        # 确保目录
        self.pyramid_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化各层文件
        for level in self.LEVELS:
            filepath = self.pyramid_dir / f"{level}.jsonl"
            if not filepath.exists():
                filepath.touch()
    
    def _get_file(self, level: PyramidLevel) -> Path:
        return self.pyramid_dir / f"{level}.jsonl"
    
    def _read_entries(self, level: PyramidLevel) -> List[PyramidEntry]:
        """读取某一层的所有条目"""
        filepath = self._get_file(level)
        entries = []
        
        if not filepath.exists():
            return entries
        
        for line in filepath.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append(PyramidEntry(
                    entry_id=data.get("id", ""),
                    level=data.get("level", level),
                    content=data.get("content", ""),
                    topic=data.get("topic", ""),
                    source_ids=data.get("source_ids", []),
                    created_at=data.get("created_at", ""),
                    metadata=data.get("metadata", {})
                ))
            except json.JSONDecodeError:
                continue
        
        return entries
    
    def _append_entry(self, entry: PyramidEntry):
        """追加写入一个条目"""
        filepath = self._get_file(entry.level)
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')
    
    def add_instance(self, content: str, topic: str, fact_id: str = "") -> PyramidEntry:
        """
        添加实例（最底层）
        
        Args:
            content: 实例内容
            topic: 主题分类
            fact_id: 关联的 fact ID
        """
        entry_id = f"inst_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(content.encode()).hexdigest()[:6]}"
        
        entry = PyramidEntry(
            entry_id=entry_id,
            level="instances",
            content=content,
            topic=topic,
            source_ids=[fact_id] if fact_id else []
        )
        
        self._append_entry(entry)
        logger.debug(f"添加实例: {entry_id} (topic={topic})")
        
        # 检查是否触发自动提炼
        if self.auto_distill:
            self._check_auto_distill(topic, "instances")
        
        return entry
    
    def _check_auto_distill(self, topic: str, current_level: PyramidLevel):
        """检查是否达到自动提炼阈值"""
        entries = self._read_entries(current_level)
        topic_entries = [e for e in entries if e.topic == topic]
        
        if len(topic_entries) >= self.AUTO_DISTILL_THRESHOLD:
            next_level = self.LEVEL_UP.get(current_level)
            if next_level:
                logger.info(f"主题 '{topic}' 在 {current_level} 层达到 {len(topic_entries)} 条，触发提炼到 {next_level}")
                self.distill_up(topic, current_level)
    
    def distill_up(self, topic: str, from_level: PyramidLevel) -> Optional[PyramidEntry]:
        """
        向上提炼：从当前层提炼到上一层
        
        Args:
            topic: 主题
            from_level: 源层级
        
        Returns:
            新创建的上层条目
        """
        to_level = self.LEVEL_UP.get(from_level)
        if not to_level:
            logger.warning(f"已经是最高层: {from_level}")
            return None
        
        # 获取该主题在源层的所有条目
        entries = self._read_entries(from_level)
        topic_entries = [e for e in entries if e.topic == topic]
        
        if not topic_entries:
            return None
        
        # 提炼内容
        knowledge = self._distill_content(topic_entries, from_level, to_level)
        if not knowledge:
            return None
        
        # 创建上层条目
        entry_id = f"{to_level[:4]}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(knowledge.encode()).hexdigest()[:6]}"
        
        entry = PyramidEntry(
            entry_id=entry_id,
            level=to_level,
            content=knowledge,
            topic=topic,
            source_ids=[e.entry_id for e in topic_entries]
        )
        
        self._append_entry(entry)
        logger.info(f"提炼完成: {from_level} → {to_level} (topic={topic})")
        
        return entry
    
    def _distill_content(self, entries: List[PyramidEntry],
                         from_level: str, to_level: str) -> Optional[str]:
        """
        提炼内容（优先 LLM，降级规则）
        """
        combined = "\n".join([e.content[:200] for e in entries[:5]])
        
        level_desc = {
            "rules": "从多个具体案例中提炼出的规律和准则",
            "patterns": "跨领域的通用方法论和思维模式",
            "ontology": "最核心的概念定义和认知框架"
        }
        
        if self.llm:
            prompt = f"""请从以下多条 {from_level} 级知识中，提炼出 {to_level} 级的知识。

{to_level} 的定义：{level_desc.get(to_level, '更高层次的抽象')}

源知识：
{combined}

请用简洁的语言总结，不超过 200 字。直接输出提炼结果。"""
            
            response = self.llm.call(prompt, task="distill", max_tokens=300)
            if response and len(response) > 10:
                return response
        
        # 规则降级：合并摘要
        summaries = [e.content[:80] for e in entries[:3]]
        return f"[{to_level}] 从 {len(entries)} 条 {from_level} 中提炼：\n" + "\n- ".join([""] + summaries)
    
    def query(self, topic: Optional[str] = None, level: Optional[PyramidLevel] = None) -> List[Dict]:
        """
        查询金字塔知识
        
        Args:
            topic: 按主题过滤
            level: 按层级过滤
        """
        results = []
        levels = [level] if level else self.LEVELS
        
        for lv in levels:
            entries = self._read_entries(lv)
            for entry in entries:
                if topic and entry.topic != topic:
                    continue
                results.append(entry.to_dict())
        
        return results
    
    def get_topics(self) -> Dict[str, Dict[str, int]]:
        """获取所有主题及其在各层的分布"""
        topics = {}
        
        for level in self.LEVELS:
            entries = self._read_entries(level)
            for entry in entries:
                t = entry.topic or "_untagged"
                if t not in topics:
                    topics[t] = {lv: 0 for lv in self.LEVELS}
                topics[t][level] += 1
        
        return topics
    
    def get_stats(self) -> Dict:
        """获取金字塔统计"""
        stats = {"agent": self.agent_name, "levels": {}, "total": 0}
        
        for level in self.LEVELS:
            count = len(self._read_entries(level))
            stats["levels"][level] = count
            stats["total"] += count
        
        stats["topics"] = self.get_topics()
        stats["auto_distill"] = self.auto_distill
        
        return stats

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
Memora v4.0 - Dimension Calculator

五维认知分数计算器

基于认知科学理论（Bloom 认知分类、Dreyfus 技能习得模型）
计算 5 个维度的原始分数：
1. 知识内化 (Understanding)
2. 知识应用 (Application)
3. 知识创造 (Creation)
4. 元认知 (Metacognition)
5. 协作认知 (Collaboration)

Author: 枢衡
Date: 2026-03-22
Version: 5.0.3
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta


class DimensionCalculator:
    """五维认知分数计算器"""
    
    # EXP 权重配置（基于 Bloom 认知分类）
    # 维度权重（与 normalization_engine.py 保持一致）
    # creation 权重最高 (0.25)，鼓励知识创造
    # metacognition 权重最低 (0.15)，但仍是重要的
    DIMENSION_WEIGHTS = {
        'understanding': 0.20,
        'application': 0.20,
        'creation': 0.25,
        'metacognition': 0.15,
        'collaboration': 0.20
    }
    
    EXP_WEIGHTS = {
        # 知识内化维度 (权重 0.20)
        'write_episodic_fact': {'dimension': 'understanding', 'exp': 1},
        'write_semantic_fact': {'dimension': 'understanding', 'exp': 2},  # 双倍，鼓励知识沉淀
        'fact_length_bonus': {'dimension': 'understanding', 'exp': 0.5},  # >200 字
        'use_tags': {'dimension': 'understanding', 'exp': 0.5},
        
        # 知识应用维度 (权重 0.20)
        'memory_search': {'dimension': 'application', 'exp': 2},
        'search_then_complete_task': {'dimension': 'application', 'exp': 10},
        'knowledge_reuse': {'dimension': 'application', 'exp': 3},
        
        # 知识创造维度 (权重 0.25 - 最高，鼓励创造)
        'share_to_shared': {'dimension': 'creation', 'exp': 6},  # +20% (权重奖励)
        'create_skill': {'dimension': 'creation', 'exp': 12},    # +20%
        'knowledge_synthesis': {'dimension': 'creation', 'exp': 5},  # +25%
        'knowledge_cited': {'dimension': 'creation', 'exp': 2},  # 被他人引用
        
        # 元认知维度 (权重 0.15 - 最低，但仍重要)
        'weekly_review': {'dimension': 'metacognition', 'exp': 5},
        'self_reflection_fact': {'dimension': 'metacognition', 'exp': 2},
        'goal_setting': {'dimension': 'metacognition', 'exp': 3},
        'progress_tracking': {'dimension': 'metacognition', 'exp': 2},
        
        # 协作认知维度 (权重 0.20)
        'help_others': {'dimension': 'collaboration', 'exp': 3},
        'seek_help': {'dimension': 'collaboration', 'exp': 1},
        'collab_task': {'dimension': 'collaboration', 'exp': 4},
        'code_review': {'dimension': 'collaboration', 'exp': 3},
    }
    
    def __init__(self, agent_name: str, facts_base: str = None):
        """
        初始化维度计算器
        
        Args:
            agent_name: Agent 名称
            facts_base: facts 基础路径
        """
        self.agent_name = agent_name
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                import sys as _s; _s.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / 'config')); from path_config import get_config
            facts_base = str(get_config().facts_base)
        self.facts_base = Path(facts_base)
        self.agent_dir = self.facts_base / agent_name
        self.facts_dir = self.agent_dir / 'facts'
        self.shared_dir = self.facts_base / 'shared'
    
    def calculate_all_dimensions(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, float]:
        """
        计算所有维度的原始分数
        
        Args:
            start_date: 开始日期（YYYY-MM-DD），不传则从开始统计
            end_date: 结束日期（YYYY-MM-DD），不传则统计到今天
        
        Returns:
            {'understanding': 45.5, 'application': 30.0, ...}
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 统计各维度分数
        scores = {
            'understanding': self._calculate_understanding(start_date, end_date),
            'application': self._calculate_application(start_date, end_date),
            'creation': self._calculate_creation(start_date, end_date),
            'metacognition': self._calculate_metacognition(start_date, end_date),
            'collaboration': self._calculate_collaboration(start_date, end_date)
        }
        
        return scores
    
    def _calculate_understanding(self, start_date: Optional[str], end_date: str) -> float:
        """
        计算知识内化维度分数
        
        指标：
        - semantic facts 数量（权重 2.0）
        - episodic facts 数量（权重 1.0）
        - 内容长度奖励（>200 字 +0.5）
        - 标签使用（+0.5）
        """
        score = 0.0
        
        if not self.facts_dir.exists():
            return score
        
        # 遍历 facts 目录
        for fact_type in ['episodic', 'semantic']:
            type_dir = self.facts_dir / fact_type
            if not type_dir.exists():
                continue
            
            # 支持.md 和.json 格式
            for fact_file in list(type_dir.glob('*.md')) + list(type_dir.glob('*.json')):
                # 检查日期范围
                file_date = self._extract_date_from_filename(fact_file.name)
                if file_date and start_date and file_date < start_date:
                    continue
                if file_date and file_date > end_date:
                    continue
                
                # 基础分数
                if fact_type == 'semantic':
                    score += 2.0
                else:
                    score += 1.0
                
                # 读取内容，检查长度
                try:
                    content = fact_file.read_text(encoding='utf-8')
                    if len(content) > 200:
                        score += 0.5  # 长度奖励
                    
                    # 检查是否有标签
                    if '#tag=' in content or '## 标签' in content:
                        score += 0.5
                except Exception:
                    pass
        
        return score
    
    def _calculate_application(self, start_date: Optional[str], end_date: str) -> float:
        """
        计算知识应用维度分数
        
        指标：
        - memory_search 次数（权重 2.0）
        - 搜索后完成任务（+10）
        - 知识复用（+3.0）
        """
        score = 0.0
        
        # 统计 memory_search 次数（从 exp_history 中读取）
        exp_history_file = self.agent_dir / 'exp_history.jsonl'
        if exp_history_file.exists():
            with open(exp_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        record_date = record.get('date', '')
                        
                        # 检查日期范围
                        if start_date and record_date < start_date:
                            continue
                        if record_date > end_date:
                            continue
                        
                        # 统计 application 相关行为
                        if record.get('dimension') == 'application':
                            action = record.get('action', '')
                            if action == 'memory_search':
                                score += 2.0
                            elif action == 'search_then_complete_task':
                                score += 10.0
                            elif action == 'knowledge_reuse':
                                score += 3.0
                    except Exception:
                        continue
        
        return score
    
    def _calculate_creation(self, start_date: Optional[str], end_date: str) -> float:
        """
        计算知识创造维度分数
        
        指标：
        - 分享到 shared/ 次数（权重 5.0）
        - 创建技能（+10）
        - 知识整合（+4.0）
        - 被他人引用（+2.0）
        """
        score = 0.0
        
        # 统计分享到 shared/ 的次数
        if self.shared_dir.exists():
            for shared_file in self.shared_dir.glob('*.md'):
                # 检查作者
                try:
                    content = shared_file.read_text(encoding='utf-8')
                    if self.agent_name in content:
                        file_date = self._extract_date_from_filename(shared_file.name)
                        if file_date and start_date and file_date < start_date:
                            continue
                        if file_date and file_date > end_date:
                            continue
                        
                        score += 5.0
                except Exception:
                    pass
        
        # 从 exp_history 统计其他创造行为
        exp_history_file = self.agent_dir / 'exp_history.jsonl'
        if exp_history_file.exists():
            with open(exp_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        record_date = record.get('date', '')
                        
                        if start_date and record_date < start_date:
                            continue
                        if record_date > end_date:
                            continue
                        
                        if record.get('dimension') == 'creation':
                            action = record.get('action', '')
                            if action == 'create_skill':
                                score += 10.0
                            elif action == 'knowledge_synthesis':
                                score += 4.0
                            elif action == 'knowledge_cited':
                                score += 2.0
                    except Exception:
                        continue
        
        return score
    
    def _calculate_metacognition(self, start_date: Optional[str], end_date: str) -> float:
        """
        计算元认知维度分数
        
        v6.1 增强：除了 exp_history 记录外，自动从以下来源采集：
        - memory/ 日志中包含反思/总结/复盘关键词（+2.0/篇）
        - MEMORY.md 存在且有内容（+3.0）
        - 认知画像查看记录（+1.0/次）
        - 每日任务完成（+2.0/个）
        - 周报文件（+5.0/篇）
        """
        score = 0.0
        
        # 1. 周报文件
        reports_dir = self.agent_dir / 'reports'
        if reports_dir.exists():
            for report_file in reports_dir.glob('weekly_*.md'):
                file_date = self._extract_date_from_filename(report_file.name)
                if file_date and start_date and file_date < start_date:
                    continue
                if file_date and file_date > end_date:
                    continue
                score += 5.0
        
        # 2. 自动采集：memory/ 中的反思类内容
        openclaw_base = Path(os.path.expanduser("~/.openclaw"))
        for ws in openclaw_base.glob("workspace*"):
            memory_dir = ws / "memory"
            if not memory_dir.exists():
                continue
            # 检查 workspace 是否属于当前 agent（支持中文名 vs 英文目录）
            ws_name = ws.name.replace("workspace-", "").replace("workspace", "main")
            matched = (ws_name == self.agent_name or self.agent_name in str(ws))
            if not matched:
                # 尝试从 SOUL.md/IDENTITY.md 解析中文名匹配
                try:
                    try:
                        from .agent_resolver import parse_soul_file, parse_identity_file
                    except ImportError:
                        from agent_resolver import parse_soul_file, parse_identity_file
                    soul = ws / "SOUL.md"
                    if soul.exists():
                        cn_name = parse_soul_file(soul)
                        if cn_name == self.agent_name:
                            matched = True
                    if not matched:
                        identity = ws / "IDENTITY.md"
                        if identity.exists():
                            cn_name = parse_identity_file(identity)
                            if cn_name == self.agent_name:
                                matched = True
                except ImportError:
                    pass
            if not matched:
                continue
            
            for md_file in memory_dir.glob("*.md"):
                file_date = self._extract_date_from_filename(md_file.name)
                if file_date and start_date and file_date < start_date:
                    continue
                if file_date and file_date > end_date:
                    continue
                try:
                    content = md_file.read_text(encoding='utf-8', errors='ignore')
                    # 包含反思关键词的加分
                    reflection_keywords = ['反思', '总结', '复盘', '教训', '改进', '反省', 'review', 'reflection', 'lesson']
                    if any(kw in content.lower() for kw in reflection_keywords):
                        score += 2.0
                except Exception:
                    pass
            
            # MEMORY.md 存在且有实质内容
            memory_md = ws / "MEMORY.md"
            if memory_md.exists():
                try:
                    content = memory_md.read_text(encoding='utf-8', errors='ignore')
                    if len(content) > 100:  # 不是空模板
                        score += 3.0
                except Exception:
                    pass
            break  # 只处理匹配的第一个 workspace
        
        # 3. 从 exp_history 统计显式的元认知行为
        exp_history_file = self.agent_dir / 'exp_history.jsonl'
        if exp_history_file.exists():
            with open(exp_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        record_date = record.get('date', '')
                        if start_date and record_date < start_date:
                            continue
                        if record_date > end_date:
                            continue
                        if record.get('dimension') == 'metacognition':
                            action = record.get('action', '')
                            if action == 'weekly_review':
                                score += 5.0
                            elif action == 'self_reflection_fact':
                                score += 2.0
                            elif action == 'goal_setting':
                                score += 3.0
                            elif action == 'progress_tracking':
                                score += 2.0
                            elif action == 'quest_complete':
                                score += 2.0
                            elif action == 'view_profile':
                                score += 1.0
                    except Exception:
                        continue
        
        return score
    
    def _calculate_collaboration(self, start_date: Optional[str], end_date: str) -> float:
        """
        计算协作认知维度分数
        
        v6.1 增强：除了 exp_history 记录外，自动从以下来源采集：
        - shared/ 目录贡献（知识共享，+5.0/篇）
        - Vega 消息记录（与其他 Agent 沟通，+1.0/条）
        - 协作任务（+4.0）
        - Code Review（+3.0）
        """
        score = 0.0
        
        # 1. 分享到 shared/ 的知识（也计入 collaboration）
        if self.shared_dir.exists():
            for shared_file in self.shared_dir.glob('*.md'):
                try:
                    content = shared_file.read_text(encoding='utf-8', errors='ignore')
                    if self.agent_name in content:
                        file_date = self._extract_date_from_filename(shared_file.name)
                        if file_date and start_date and file_date < start_date:
                            continue
                        if file_date and file_date > end_date:
                            continue
                        score += 5.0
                except Exception:
                    pass
        
        # 2. 自动采集：Vega 消息（与其他 Agent 的沟通）
        try:
            from ..config.path_config import get_config
            cfg = get_config()
            outbox = cfg.facts_base.parent / '消息队列' / 'outbox' / self.agent_name
            if outbox.exists():
                for msg_file in outbox.glob('*.json'):
                    file_date = self._extract_date_from_filename(msg_file.name)
                    if file_date and start_date and file_date < start_date:
                        continue
                    if file_date and file_date > end_date:
                        continue
                    score += 1.0
            
            # 收到的消息也算（别人主动找你协作）
            inbox = cfg.facts_base.parent / '消息队列' / 'inbox' / self.agent_name
            if inbox.exists():
                for msg_file in inbox.glob('*.json'):
                    if msg_file.name.startswith('集团通知'):
                        continue  # 跳过广播通知
                    file_date = self._extract_date_from_filename(msg_file.name)
                    if file_date and start_date and file_date < start_date:
                        continue
                    if file_date and file_date > end_date:
                        continue
                    score += 0.5
        except Exception:
            pass
        
        # 3. 从 exp_history 统计显式的协作行为
        exp_history_file = self.agent_dir / 'exp_history.jsonl'
        if exp_history_file.exists():
            with open(exp_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        record_date = record.get('date', '')
                        if start_date and record_date < start_date:
                            continue
                        if record_date > end_date:
                            continue
                        if record.get('dimension') == 'collaboration':
                            action = record.get('action', '')
                            if action == 'help_others':
                                score += 3.0
                            elif action == 'seek_help':
                                score += 1.0
                            elif action == 'collab_task':
                                score += 4.0
                            elif action == 'code_review':
                                score += 3.0
                    except Exception:
                        continue
        
        return score
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """从文件名提取日期（YYYY-MM-DD）"""
        import re
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else None
    
    def get_statistics(self) -> Dict:
        """
        获取统计数据
        
        Returns:
            统计信息字典
        """
        stats = {
            'total_facts': 0,
            'semantic_facts': 0,
            'episodic_facts': 0,
            'memory_searches': 0,
            'shared_knowledge': 0,
            'weekly_reviews': 0,
            'collab_tasks': 0
        }
        
        # 统计 facts 数量（支持.md 和.json 格式，递归子目录）
        if self.facts_dir.exists():
            episodic_dir = self.facts_dir / 'episodic'
            semantic_dir = self.facts_dir / 'semantic'
            
            if episodic_dir.exists():
                md_count = len(list(episodic_dir.rglob('*.md')))
                json_count = len(list(episodic_dir.rglob('*.json')))
                stats['episodic_facts'] = md_count + json_count
                stats['total_facts'] += stats['episodic_facts']
            
            if semantic_dir.exists():
                md_count = len(list(semantic_dir.rglob('*.md')))
                json_count = len(list(semantic_dir.rglob('*.json')))
                stats['semantic_facts'] = md_count + json_count
                stats['total_facts'] += stats['semantic_facts']
        
        # 统计分享到 shared/
        if self.shared_dir.exists():
            stats['shared_knowledge'] = len([
                f for f in self.shared_dir.glob('*.md')
                if f.read_text(encoding='utf-8', errors='ignore').find(self.agent_name) != -1
            ])
        
        # 从 exp_history 统计其他
        exp_history_file = self.agent_dir / 'exp_history.jsonl'
        if exp_history_file.exists():
            with open(exp_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        action = record.get('action', '')
                        if action == 'memory_search':
                            stats['memory_searches'] += 1
                        elif action == 'weekly_review':
                            stats['weekly_reviews'] += 1
                        elif action == 'collab_task':
                            stats['collab_tasks'] += 1
                    except Exception:
                        continue
        
        return stats


def main():
    """测试维度计算器"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 dimension_calculator.py <Agent 名称>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    calculator = DimensionCalculator(agent_name)
    
    # 计算所有维度
    scores = calculator.calculate_all_dimensions()
    
    print(f"\n=== {agent_name} 的认知维度分数 ===\n")
    for dimension, score in scores.items():
        print(f"{dimension:15s}: {score:6.1f}")
    
    print(f"\n总计：{sum(scores.values()):.1f}")
    
    # 统计数据
    stats = calculator.get_statistics()
    print(f"\n=== 统计数据 ===")
    for key, value in stats.items():
        print(f"{key:20s}: {value}")


if __name__ == '__main__':
    main()

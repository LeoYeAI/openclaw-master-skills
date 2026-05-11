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
Memora v4.0 - Cognitive Profile Generator

认知画像生成器

整合维度分数、归一化结果、等级信息，生成完整的认知画像

Author: 枢衡
Date: 2026-03-20
Version: 5.0.0
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

try:
    from .dimension_calculator import DimensionCalculator
except ImportError:
    from dimension_calculator import DimensionCalculator
try:
    from .normalization_engine import NormalizationEngine
except ImportError:
    from normalization_engine import NormalizationEngine
try:
    from .level_system import LevelSystem
except ImportError:
    from level_system import LevelSystem


class CognitiveProfileGenerator:
    """认知画像生成器"""
    
    def __init__(self, agent_name: str, facts_base: str = None, config_path: Optional[str] = None):
        """
        初始化认知画像生成器
        
        Args:
            agent_name: Agent 名称
            facts_base: facts 基础路径
            config_path: 配置文件路径（可选）
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
        self.config_path = config_path
        
        # 初始化计算引擎
        self.calculator = DimensionCalculator(agent_name, facts_base)
        self.normalizer = NormalizationEngine(config_path)
    
    def generate_profile(self, team_scores: Optional[Dict[str, List[float]]] = None, auto_scan: bool = True, auto_save: bool = False) -> Dict:
        """
        生成完整的认知画像（查询时动态计算）
        
        Args:
            team_scores: 团队分数（可选），用于归一化
            auto_scan: 是否自动扫描团队规模（默认 True）
            auto_save: 是否自动保存到文件（默认 False，不保存文件）
        
        Returns:
            完整的认知画像字典
        
        设计理念：
        - 每次查询都动态计算，保证数据实时性
        - 不保存静态文件，避免数据过期问题
        - 本地服务器计算很快，无需缓存
        """
        # 1. 计算原始维度分数
        raw_scores = self.calculator.calculate_all_dimensions()
        
        # 2. 自动扫描团队（如果启用）
        if auto_scan and team_scores is None:
            try:
                from .team_scanner import TeamScanner
            except ImportError:
                from team_scanner import TeamScanner
            scanner = TeamScanner()
            active_agents = scanner.scan_active_agents()
            
            # 如果找到其他活跃 Agent，尝试获取他们的分数
            if len(active_agents) > 1:
                team_scores = self._collect_team_scores(active_agents)
        
        # 3. 归一化
        normalized_scores = self.normalizer.normalize(raw_scores, team_scores)
        
        # 3. 计算综合认知分数
        cognitive_score = self.normalizer.calculate_cognitive_score(normalized_scores)
        
        # 4. 使用等级系统（累积 EXP）计算等级
        level_sys = LevelSystem(self.agent_name, str(self.facts_base))
        level_info_raw = level_sys.get_level_info()
        level_info = {
            'level': level_info_raw['level'],
            'stage': level_sys.get_level_stage(level_info_raw['level']),
            'badge': level_sys.get_level_badge(level_info_raw['level'])
        }
        
        # 5. 获取统计数据
        statistics = self.calculator.get_statistics()
        
        # 6. 计算各维度阶段
        dimension_stages = {}
        for dimension, score in normalized_scores.items():
            dimension_stages[dimension] = {
                'score': score,
                'stage': self.normalizer.get_dimension_stage(dimension, score),
                'raw_score': raw_scores.get(dimension, 0)
            }
        
        # 7. 获取 EXP 信息（修复 FB-007：profile['exp'] KeyError）
        exp_info = level_info_raw.get('total_exp', 0)
        if isinstance(exp_info, dict):
            exp_info = exp_info.get('total', 0)
        
        # 8. 构建完整画像
        profile = {
            'agent': self.agent_name,
            'generated_at': datetime.now().isoformat(),
            
            'dimensions': dimension_stages,
            
            'cognitive_score': cognitive_score,
            'level': level_info['level'],
            'stage': level_info['stage'],
            'badge': level_info['badge'],
            'exp': exp_info,  # FB-007 修复：确保 exp 字段存在
            
            'statistics': statistics,
            
            'team_rank': self._calculate_team_rank(normalized_scores, team_scores) if team_scores else None
        }
        
        # 8. 不保存文件，直接返回（动态计算，实时数据）
        # 设计理念：每次查询都动态计算，保证数据实时性
        # if auto_save:
        #     self.save_profile(profile)  # ← 已废弃，不再保存文件
        
        return profile
    
    def _collect_team_scores(self, active_agents: List[str]) -> Optional[Dict[str, List[float]]]:
        """
        收集团队各 Agent 的维度分数
        
        Args:
            active_agents: 活跃 Agent 列表
        
        Returns:
            团队分数字典
        """
        team_scores = {
            'understanding': [],
            'application': [],
            'creation': [],
            'metacognition': [],
            'collaboration': []
        }
        
        for agent_name in active_agents:
            try:
                # 跳过自己
                if agent_name == self.agent_name:
                    continue
                
                # 尝试读取其他 Agent 的认知画像
                other_agent_dir = self.facts_base / agent_name
                profile_file = other_agent_dir / 'cognitive_profile.json'
                
                if profile_file.exists():
                    import json
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile = json.load(f)
                    
                    dimensions = profile.get('dimensions', {})
                    for dim in team_scores:
                        if dim in dimensions:
                            raw_score = dimensions[dim].get('raw_score', 0)
                            team_scores[dim].append(raw_score)
                else:
                    # 如果没有画像文件，临时计算
                    other_calc = DimensionCalculator(agent_name, str(self.facts_base))
                    other_scores = other_calc.calculate_all_dimensions()
                    for dim in team_scores:
                        if dim in other_scores:
                            team_scores[dim].append(other_scores[dim])
            except Exception as e:
                # 跳过失败的 Agent
                continue
        
        # 添加自己的分数
        raw_scores = self.calculator.calculate_all_dimensions()
        for dim in team_scores:
            if dim in raw_scores:
                team_scores[dim].append(raw_scores[dim])
        
        return team_scores
    
    def _calculate_team_rank(self, normalized_scores: Dict[str, float], team_scores: Dict[str, List[float]]) -> Dict[str, int]:
        """计算团队排名"""
        ranks = {}
        
        for dimension, score in normalized_scores.items():
            if dimension not in team_scores:
                continue
            
            # 计算排名（分数越高排名越靠前）
            rank = 1 + sum(1 for s in team_scores[dimension] if s > score)
            ranks[dimension] = rank
        
        # 综合排名
        total_score = sum(normalized_scores.values())
        team_total_scores = []
        for i in range(len(team_scores[list(team_scores.keys())[0]])):
            team_total = sum(team_scores[dim][i] for dim in team_scores)
            team_total_scores.append(team_total)
        
        overall_rank = 1 + sum(1 for s in team_total_scores if s > total_score)
        ranks['overall'] = overall_rank
        
        return ranks
    
    def save_profile(self, profile: Optional[Dict] = None, output_path: Optional[str] = None) -> str:
        """
        保存认知画像到文件
        
        Args:
            profile: 认知画像字典（可选），不传则重新生成
            output_path: 输出路径（可选），不传则保存到 agent 目录
        
        Returns:
            保存的文件路径
        """
        if profile is None:
            profile = self.generate_profile(auto_save=False)  # 避免无限递归
        
        if output_path is None:
            output_path = self.agent_dir / 'cognitive_profile.json'
        else:
            output_path = Path(output_path)
        
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存 JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def generate_profile_card(self, profile: Optional[Dict] = None) -> str:
        """
        生成可视化的认知画像卡片（Markdown 格式）
        
        Args:
            profile: 认知画像字典（可选），不传则重新生成
        
        Returns:
            Markdown 格式的画像卡片
        """
        if profile is None:
            profile = self.generate_profile()
        
        # 构建卡片
        lines = []
        lines.append(f"# 🧠 认知画像 — {profile['agent']}")
        lines.append("")
        lines.append(f"**综合等级:** Lv.{profile['level']} {profile['badge']} {profile['stage']}")
        lines.append(f"**认知分数:** {profile['cognitive_score']}/100")
        
        if profile.get('team_rank'):
            lines.append(f"**团队排名:** #{profile['team_rank'].get('overall', 'N/A')}")
        
        lines.append("")
        lines.append("## 📊 五维雷达图")
        lines.append("")
        
        # 维度可视化
        dimension_names = {
            'creation': '知识创造',
            'collaboration': '协作认知',
            'understanding': '知识内化',
            'application': '知识应用',
            'metacognition': '元认知'
        }
        
        for dim, name in dimension_names.items():
            dim_data = profile['dimensions'].get(dim, {})
            score = dim_data.get('score', 0)
            raw = dim_data.get('raw_score', 0)
            stage = dim_data.get('stage', '')
            
            # 进度条
            bar_length = int(score / 5)  # 0-20 个 █
            bar = '█' * bar_length + '░' * (20 - bar_length)
            
            # 团队排名
            rank_info = ""
            if profile.get('team_rank') and dim in profile['team_rank']:
                rank_info = f" (团队 #{profile['team_rank'][dim]})"
            
            lines.append(f"{name:8s} {bar} {score:5.1f}{rank_info} - {stage}")
        
        lines.append("")
        lines.append("## 📈 统计数据")
        lines.append("")
        
        stats = profile['statistics']
        lines.append(f"- 总 Facts 数：{stats.get('total_facts', 0)}")
        lines.append(f"- Semantic Facts: {stats.get('semantic_facts', 0)}")
        lines.append(f"- Episodic Facts: {stats.get('episodic_facts', 0)}")
        lines.append(f"- 记忆搜索次数：{stats.get('memory_searches', 0)}")
        lines.append(f"- 知识分享次数：{stats.get('shared_knowledge', 0)}")
        lines.append(f"- 周报/复盘次数：{stats.get('weekly_reviews', 0)}")
        lines.append(f"- 协作任务数：{stats.get('collab_tasks', 0)}")
        
        lines.append("")
        lines.append("---")
        lines.append(f"_生成时间：{profile['generated_at']}_")
        
        return '\n'.join(lines)


def main():
    """测试认知画像生成器"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 cognitive_profile.py <Agent 名称>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    generator = CognitiveProfileGenerator(agent_name)
    
    # 生成画像
    print(f"\n=== 生成 {agent_name} 的认知画像 ===\n")
    
    profile = generator.generate_profile()
    
    # 打印画像卡片
    card = generator.generate_profile_card(profile)
    print(card)
    
    # 保存 JSON
    output_path = generator.save_profile()
    print(f"\n✅ 认知画像已保存到：{output_path}")


if __name__ == '__main__':
    main()

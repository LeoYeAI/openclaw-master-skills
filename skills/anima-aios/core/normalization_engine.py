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
Memora v4.0 - Normalization Engine

认知分数归一化引擎，支持三种模式：
1. 绝对基准归一化（单 Agent）
2. 混合归一化（小团队 2-4 人）
3. 百分位数归一化（大团队 5+ 人）

基于认知科学理论（Dreyfus 模型、Bloom 分类、Ericsson 刻意练习）

Author: 枢衡
Date: 2026-03-20
Version: 5.0.0
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class NormalizationEngine:
    """认知分数归一化引擎"""
    
    # 默认基准值（基于认知科学研究）
    # 参考：Dreyfus 技能习得模型、Ericsson 刻意练习理论
    DEFAULT_BENCHMARKS = {
        'understanding': {
            'novice': 10,      # 0-1 个月，每周 2-3 条 facts
            'beginner': 30,    # 1-3 个月
            'competent': 60,   # 6 个月
            'proficient': 100, # 1 年
            'expert': 200      # 2-3 年
        },
        'application': {
            'novice': 5,
            'beginner': 15,
            'competent': 30,
            'proficient': 60,
            'expert': 120
        },
        'creation': {
            'novice': 0,
            'beginner': 5,
            'competent': 15,
            'proficient': 30,
            'expert': 50
        },
        'metacognition': {
            'novice': 2,
            'beginner': 8,
            'competent': 15,
            'proficient': 30,
            'expert': 60
        },
        'collaboration': {
            'novice': 3,
            'beginner': 10,
            'competent': 25,
            'proficient': 50,
            'expert': 100
        }
    }
    
    # 维度权重
    DEFAULT_WEIGHTS = {
        'understanding': 0.20,
        'application': 0.20,
        'creation': 0.25,
        'metacognition': 0.15,
        'collaboration': 0.20
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化归一化引擎
        
        Args:
            config_path: 配置文件路径（可选，不传则用默认值）
        """
        self.config = self._load_config(config_path)
        self.benchmarks = self.config.get('benchmarks', self.DEFAULT_BENCHMARKS)
        self.weights = self.config.get('weights', self.DEFAULT_WEIGHTS)
        self.mode = self.config.get('normalization', {}).get('mode', 'auto')
        self.use_global_benchmark = self.config.get('normalization', {}).get('use_global_benchmark', False)
        
        # 团队规模阈值
        thresholds = self.config.get('normalization', {}).get('team_size_threshold', {})
        self.percentile_threshold = thresholds.get('percentile', 5)
        self.hybrid_threshold = thresholds.get('hybrid', 2)
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def normalize(self, raw_scores: Dict[str, float], team_scores: Optional[Dict[str, List[float]]] = None) -> Dict[str, float]:
        """
        归一化原始分数
        
        Args:
            raw_scores: 各维度原始分数 {'understanding': 45, 'application': 30, ...}
            team_scores: 团队分数（可选）用于百分位归一化
        
        Returns:
            归一化后的分数 {'understanding': 72.5, 'application': 65.0, ...}
        """
        # 确定团队规模
        team_size = len(team_scores[list(team_scores.keys())[0]]) if team_scores else 1
        
        # 自动选择归一化模式
        if self.mode == 'auto':
            if team_size >= self.percentile_threshold:
                mode = 'percentile'
            elif team_size >= self.hybrid_threshold:
                mode = 'hybrid'
            else:
                mode = 'absolute'
        else:
            mode = self.mode
        
        # 执行归一化
        if mode == 'absolute':
            return self._absolute_normalization(raw_scores)
        elif mode == 'hybrid':
            return self._hybrid_normalization(raw_scores, team_scores)
        elif mode == 'percentile':
            return self._percentile_normalization(raw_scores, team_scores)
        else:
            raise ValueError(f"Unknown normalization mode: {mode}")
    
    def _absolute_normalization(self, raw_scores: Dict[str, float]) -> Dict[str, float]:
        """
        绝对基准归一化（单 Agent 模式）
        
        基于认知科学理论设定的绝对标准
        """
        normalized = {}
        
        for dimension, raw_score in raw_scores.items():
            if dimension not in self.benchmarks:
                continue
            
            threshold = self.benchmarks[dimension]
            
            # 分段线性映射
            if raw_score >= threshold['expert']:
                # 专家级：80-100 分
                score = 80 + min(20, (raw_score - threshold['expert']) * 0.1)
            elif raw_score >= threshold['proficient']:
                # 熟练级：60-80 分
                score = 60 + (raw_score - threshold['proficient']) / (threshold['expert'] - threshold['proficient']) * 20
            elif raw_score >= threshold['competent']:
                # 胜任级：40-60 分
                score = 40 + (raw_score - threshold['competent']) / (threshold['proficient'] - threshold['competent']) * 20
            elif raw_score >= threshold['beginner']:
                # 初学者级：20-40 分
                score = 20 + (raw_score - threshold['beginner']) / (threshold['competent'] - threshold['beginner']) * 20
            else:
                # 新手级：0-20 分
                score = min(20, raw_score / threshold['beginner'] * 20) if threshold['beginner'] > 0 else 0
            
            normalized[dimension] = round(score, 2)
        
        return normalized
    
    def _percentile_normalization(self, raw_scores: Dict[str, float], team_scores: Dict[str, List[float]]) -> Dict[str, float]:
        """
        百分位数归一化（大团队模式）
        
        基于团队百分位，平滑处理避免极端值
        """
        normalized = {}
        
        for dimension, raw_score in raw_scores.items():
            if dimension not in team_scores:
                continue
            
            scores = team_scores[dimension]
            
            # 计算百分位
            rank = sum(1 for s in scores if s < raw_score)
            percentile = rank / len(scores) if len(scores) > 0 else 0
            
            # 平滑处理（映射到 5-95 范围，避免 0 和 100 的极端）
            smoothed = 0.05 + percentile * 0.9
            score = smoothed * 100
            
            normalized[dimension] = round(score, 2)
        
        return normalized
    
    def _hybrid_normalization(self, raw_scores: Dict[str, float], team_scores: Optional[Dict[str, List[float]]]) -> Dict[str, float]:
        """
        混合归一化（小团队模式）
        
        50% 绝对基准 + 50% 团队百分位
        """
        # 50% 来自绝对基准
        absolute_scores = self._absolute_normalization(raw_scores)
        
        # 50% 来自团队百分位
        if team_scores:
            relative_scores = self._percentile_normalization(raw_scores, team_scores)
        else:
            relative_scores = absolute_scores
        
        # 混合
        normalized = {}
        for dimension in absolute_scores:
            absolute = absolute_scores.get(dimension, 0)
            relative = relative_scores.get(dimension, 0)
            normalized[dimension] = round(absolute * 0.5 + relative * 0.5, 2)
        
        return normalized
    
    def calculate_cognitive_score(self, normalized_scores: Dict[str, float]) -> float:
        """
        计算综合认知分数
        
        Args:
            normalized_scores: 归一化后的各维度分数
        
        Returns:
            综合认知分数（0-100）
        """
        total = 0.0
        
        for dimension, score in normalized_scores.items():
            weight = self.weights.get(dimension, 0)
            total += score * weight
        
        return round(total, 2)
    
    def score_to_level(self, cognitive_score: float) -> Dict:
        """
        将认知分数映射到等级（已废弃）
        
        ⚠️ 注意：此方法已废弃！请使用 level_system.py 中的等级系统。
        
        原因：
        - 与 level_system.py 的 EXP 累计等级系统冲突
        - 导致同一用户有两个等级值
        - 统一使用 level_system.py 的 level = int(exp ^ 0.28) 公式
        
        Returns:
            {'level': int, 'stage': str, 'badge': str}
        
        Deprecated:
            请使用 level_system.py 的 LevelSystem.get_level_info()
        """
        # 此方法已废弃，仅保留用于向后兼容
        # 实际等级计算应使用 level_system.py
        return {'level': 0, 'stage': 'Deprecated', 'badge': '⚠️ 已废弃'}
    
    def get_dimension_stage(self, dimension: str, score: float) -> str:
        """
        获取单个维度的阶段描述
        
        Args:
            dimension: 维度名称
            score: 该维度的分数（0-100）
        
        Returns:
            阶段描述
        """
        if score >= 80:
            return 'Expert 专家级'
        elif score >= 60:
            return 'Proficient 熟练级'
        elif score >= 40:
            return 'Competent 胜任级'
        elif score >= 20:
            return 'Advanced Beginner 高级初学者'
        else:
            return 'Novice 新手级'


def main():
    """测试归一化引擎"""
    engine = NormalizationEngine()
    
    # 测试数据
    raw_scores = {
        'understanding': 45,
        'application': 30,
        'creation': 25,
        'metacognition': 12,
        'collaboration': 35
    }
    
    # 单 Agent 模式（绝对基准）
    print("=== 单 Agent 模式（绝对基准归一化） ===")
    normalized = engine.normalize(raw_scores)
    print(f"原始分数：{raw_scores}")
    print(f"归一化后：{normalized}")
    
    cognitive_score = engine.calculate_cognitive_score(normalized)
    level_info = engine.score_to_level(cognitive_score)
    print(f"综合认知分数：{cognitive_score}")
    print(f"等级：Lv.{level_info['level']} - {level_info['stage']} {level_info['badge']}")
    
    # 大团队模式（百分位归一化）
    print("\n=== 大团队模式（百分位数归一化） ===")
    team_scores = {
        'understanding': [20, 35, 45, 60, 80],
        'application': [15, 25, 30, 45, 70],
        'creation': [10, 20, 25, 40, 55],
        'metacognition': [5, 10, 12, 20, 35],
        'collaboration': [18, 30, 35, 50, 65]
    }
    normalized_team = engine.normalize(raw_scores, team_scores)
    print(f"归一化后：{normalized_team}")
    
    cognitive_score_team = engine.calculate_cognitive_score(normalized_team)
    level_info_team = engine.score_to_level(cognitive_score_team)
    print(f"综合认知分数：{cognitive_score_team}")
    print(f"等级：Lv.{level_info_team['level']} - {level_info_team['stage']} {level_info_team['badge']}")


if __name__ == '__main__':
    main()

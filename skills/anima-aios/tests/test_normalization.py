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
Anima-AIOS v5.0 - Normalization Engine Tests

测试归一化引擎的三种模式
"""

import sys
import unittest
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from normalization_engine import NormalizationEngine


class TestNormalizationEngine(unittest.TestCase):
    """归一化引擎测试"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = NormalizationEngine()
        
        # 测试数据
        self.raw_scores = {
            'understanding': 45,
            'application': 30,
            'creation': 25,
            'metacognition': 12,
            'collaboration': 35
        }
    
    def test_absolute_normalization_single_agent(self):
        """测试绝对基准归一化（单 Agent 模式）"""
        normalized = self.engine._absolute_normalization(self.raw_scores)
        
        # 验证归一化结果在 0-100 范围内
        for dimension, score in normalized.items():
            self.assertGreaterEqual(score, 0, f"{dimension} 分数不能为负")
            self.assertLessEqual(score, 100, f"{dimension} 分数不能超过 100")
        
        # 验证专家级分数（200+ 应该接近 100）
        expert_scores = {'understanding': 250, 'application': 150, 'creation': 60}
        expert_normalized = self.engine._absolute_normalization(expert_scores)
        self.assertGreater(expert_normalized['understanding'], 80, "专家级分数应该>80")
    
    def test_percentile_normalization_large_team(self):
        """测试百分位数归一化（大团队模式）"""
        team_scores = {
            'understanding': [20, 35, 45, 60, 80],
            'application': [15, 25, 30, 45, 70],
            'creation': [10, 20, 25, 40, 55],
            'metacognition': [5, 10, 12, 20, 35],
            'collaboration': [18, 30, 35, 50, 65]
        }
        
        normalized = self.engine._percentile_normalization(self.raw_scores, team_scores)
        
        # 验证归一化结果在 5-95 范围内（平滑处理）
        for dimension, score in normalized.items():
            self.assertGreaterEqual(score, 5, f"{dimension} 分数应该>=5（平滑）")
            self.assertLessEqual(score, 95, f"{dimension} 分数应该<=95（平滑）")
        
        # 验证排名：最高分应该接近 95
        top_scores = {
            'understanding': 80,
            'application': 70,
            'creation': 55,
            'metacognition': 35,
            'collaboration': 65
        }
        top_normalized = self.engine._percentile_normalization(top_scores, team_scores)
        self.assertGreater(top_normalized['understanding'], 70, "最高分应该>70")
    
    def test_hybrid_normalization_small_team(self):
        """测试混合归一化（小团队模式）"""
        team_scores = {
            'understanding': [30, 45, 60],
            'application': [20, 30, 45],
            'creation': [15, 25, 40],
            'metacognition': [8, 12, 20],
            'collaboration': [25, 35, 50]
        }
        
        normalized = self.engine._hybrid_normalization(self.raw_scores, team_scores)
        
        # 验证归一化结果在 0-100 范围内
        for dimension, score in normalized.items():
            self.assertGreaterEqual(score, 0, f"{dimension} 分数不能为负")
            self.assertLessEqual(score, 100, f"{dimension} 分数不能超过 100")
    
    def test_auto_mode_selection(self):
        """测试自动模式选择"""
        # 单 Agent
        normalized_single = self.engine.normalize(self.raw_scores, None)
        self.assertIsNotNone(normalized_single)
        
        # 小团队（3 人）
        small_team = {
            'understanding': [30, 45, 60],
            'application': [20, 30, 45],
            'creation': [15, 25, 40],
            'metacognition': [8, 12, 20],
            'collaboration': [25, 35, 50]
        }
        normalized_small = self.engine.normalize(self.raw_scores, small_team)
        self.assertIsNotNone(normalized_small)
        
        # 大团队（5 人）
        large_team = {
            'understanding': [20, 35, 45, 60, 80],
            'application': [15, 25, 30, 45, 70],
            'creation': [10, 20, 25, 40, 55],
            'metacognition': [5, 10, 12, 20, 35],
            'collaboration': [18, 30, 35, 50, 65]
        }
        normalized_large = self.engine.normalize(self.raw_scores, large_team)
        self.assertIsNotNone(normalized_large)
    
    def test_cognitive_score_calculation(self):
        """测试综合认知分数计算"""
        normalized = {
            'understanding': 70,
            'application': 65,
            'creation': 80,
            'metacognition': 55,
            'collaboration': 75
        }
        
        score = self.engine.calculate_cognitive_score(normalized)
        
        # 验证权重计算正确
        expected = (
            70 * 0.20 +  # understanding
            65 * 0.20 +  # application
            80 * 0.25 +  # creation
            55 * 0.15 +  # metacognition
            75 * 0.20    # collaboration
        )
        self.assertAlmostEqual(score, expected, places=2)
    
    def test_dimension_stage(self):
        """测试维度阶段描述"""
        test_cases = [
            (85, 'Expert 专家级'),
            (65, 'Proficient 熟练级'),
            (50, 'Competent 胜任级'),
            (30, 'Advanced Beginner 高级初学者'),
            (10, 'Novice 新手级')
        ]
        
        for score, expected_stage in test_cases:
            result = self.engine.get_dimension_stage('understanding', score)
            self.assertIn(expected_stage, result, f"分数{score}的阶段描述错误")


class TestNormalizationBenchmarks(unittest.TestCase):
    """基准值测试"""
    
    def setUp(self):
        self.engine = NormalizationEngine()
    
    def test_benchmark_completeness(self):
        """测试基准值完整性"""
        required_dimensions = ['understanding', 'application', 'creation', 'metacognition', 'collaboration']
        
        for dim in required_dimensions:
            self.assertIn(dim, self.engine.benchmarks, f"缺少维度{dim}的基准值")
            
            benchmark = self.engine.benchmarks[dim]
            required_levels = ['novice', 'beginner', 'competent', 'proficient', 'expert']
            
            for level in required_levels:
                self.assertIn(level, benchmark, f"维度{dim}缺少{level}基准值")
                self.assertIsInstance(benchmark[level], (int, float), f"维度{dim}的{level}基准值应该是数字")
    
    def test_benchmark_ordering(self):
        """测试基准值递增顺序"""
        for dim, benchmark in self.engine.benchmarks.items():
            levels = ['novice', 'beginner', 'competent', 'proficient', 'expert']
            values = [benchmark[level] for level in levels]
            
            # 验证递增（允许相等）
            for i in range(len(values) - 1):
                self.assertLessEqual(values[i], values[i+1], 
                                   f"维度{dim}的基准值顺序错误：{levels[i]}>{levels[i+1]}")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestNormalizationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestNormalizationBenchmarks))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

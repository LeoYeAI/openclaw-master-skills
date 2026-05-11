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
Anima-AIOS v5.0 - EXP Tracker Tests

测试 EXP 追踪器的核心功能
"""

import sys
import unittest
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from exp_tracker import EXPTracker


class TestEXPTracker(unittest.TestCase):
    """EXP 追踪器测试"""
    
    def setUp(self):
        """测试前准备 - 创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent_name = "TestAgent"
        self.tracker = EXPTracker(self.agent_name, self.temp_dir)
    
    def tearDown(self):
        """测试后清理 - 删除临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_exp_success(self):
        """测试成功添加 EXP"""
        success, message = self.tracker.add_exp(
            dimension='understanding',
            action='write_semantic_fact',
            exp=2,
            details={'fact_id': 'test_001'}
        )
        
        self.assertTrue(success, f"添加 EXP 失败：{message}")
        self.assertIn("添加 EXP", message)
    
    def test_add_exp_with_quality_multiplier(self):
        """测试带质量系数的 EXP 添加"""
        success, message = self.tracker.add_exp(
            dimension='understanding',
            action='write_semantic_fact',
            exp=2,
            details={'fact_id': 'test_002'},
            quality_multiplier=1.5
        )
        
        self.assertTrue(success)
        
        # 验证实际添加的 EXP 是 2 * 1.5 = 3
        history = self.tracker.get_exp_history()
        self.assertEqual(len(history), 1)
        self.assertAlmostEqual(history[0]['exp'], 3.0, places=2)
    
    def test_daily_exp_limit(self):
        """测试每日 EXP 上限"""
        dimension = 'understanding'
        limit = self.tracker.DAILY_EXP_LIMITS[dimension]  # 50
        
        # 添加接近上限的 EXP
        success1, _ = self.tracker.add_exp(
            dimension=dimension,
            action='test_action_1',
            exp=limit - 5,  # 45
            details={'test': 1}
        )
        self.assertTrue(success1)
        
        # 再次添加会超过上限
        success2, message = self.tracker.add_exp(
            dimension=dimension,
            action='test_action_2',
            exp=10,  # 会超过 50
            details={'test': 2}
        )
        
        # 应该只添加到上限
        self.assertTrue(success2)  # 部分成功
        self.assertIn("上限", message)
        
        # 验证总 EXP 不超过上限
        total = self.tracker.get_total_exp()
        self.assertLessEqual(total, limit + 0.1)  # 允许小数误差
    
    def test_exp_history_retrieval(self):
        """测试 EXP 历史记录检索"""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 添加两条记录
        self.tracker.add_exp('understanding', 'action1', 2, {'test': 1}, today)
        self.tracker.add_exp('application', 'action2', 3, {'test': 2}, today)
        self.tracker.add_exp('understanding', 'action3', 4, {'test': 3}, yesterday)
        
        # 获取今天的所有记录
        today_history = self.tracker.get_exp_history(today, today)
        self.assertEqual(len(today_history), 2)
        
        # 获取特定维度的记录
        understanding_history = self.tracker.get_exp_history(today, today, 'understanding')
        self.assertEqual(len(understanding_history), 1)
        self.assertEqual(understanding_history[0]['exp'], 2)
    
    def test_total_exp_calculation(self):
        """测试总 EXP 计算"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 添加多条记录
        self.tracker.add_exp('understanding', 'action1', 2, {}, today)
        self.tracker.add_exp('application', 'action2', 3, {}, today)
        self.tracker.add_exp('creation', 'action3', 5, {}, today)
        
        # 计算总 EXP
        total = self.tracker.get_total_exp(today, today)
        self.assertEqual(total, 10)
    
    def test_daily_summary(self):
        """测试每日摘要"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 添加 EXP
        self.tracker.add_exp('understanding', 'action1', 2, {}, today)
        self.tracker.add_exp('application', 'action2', 3, {}, today)
        
        # 获取摘要
        summary = self.tracker.get_daily_summary(today)
        
        self.assertEqual(summary['date'], today)
        self.assertAlmostEqual(summary['total'], 5, places=2)
        self.assertIn('understanding', summary['dimensions'])
        self.assertIn('application', summary['dimensions'])
    
    def test_quality_multiplier_calculation(self):
        """测试质量系数计算"""
        # 短内容（<50 字）
        short_content = "A" * 30
        multiplier = self.tracker.calculate_quality_multiplier(short_content)
        self.assertEqual(multiplier, 0.3)
        
        # 正常内容（50-200 字）
        normal_content = "B" * 100
        multiplier = self.tracker.calculate_quality_multiplier(normal_content)
        self.assertEqual(multiplier, 1.0)
        
        # 长内容（>200 字）
        long_content = "C" * 300
        multiplier = self.tracker.calculate_quality_multiplier(long_content)
        self.assertEqual(multiplier, 1.5)
    
    def test_duplicate_detection(self):
        """测试重复检测（简化版）"""
        # 重复检测是可选功能，取决于实现细节
        # 这里只测试接口存在
        details = {'fact_id': 'unique_123'}
        is_duplicate = self.tracker.check_duplicate('write_fact', details)
        self.assertIsInstance(is_duplicate, bool)
    
    def test_exp_report_export(self):
        """测试 EXP 报告导出"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 添加一些 EXP
        self.tracker.add_exp('understanding', 'action1', 2, {}, today)
        self.tracker.add_exp('application', 'action2', 3, {}, today)
        
        # 导出报告
        output_path = Path(self.temp_dir) / 'test_report.json'
        result_path = self.tracker.export_exp_report(str(output_path), today, today)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(result_path))
        
        # 验证内容
        with open(result_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        self.assertEqual(report['agent'], self.agent_name)
        self.assertEqual(report['total_exp'], 5)
        self.assertEqual(report['record_count'], 2)


class TestEXPTrackerPersistence(unittest.TestCase):
    """EXP 追踪器持久化测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.agent_name = "PersistTest"
        self.tracker = EXPTracker(self.agent_name, self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_data_persistence(self):
        """测试数据持久化"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 添加 EXP
        self.tracker.add_exp('understanding', 'action1', 2, {'test': 1}, today)
        
        # 创建新的 tracker 实例（模拟重启）
        tracker2 = EXPTracker(self.agent_name, self.temp_dir)
        
        # 验证数据还在
        history = tracker2.get_exp_history(today, today)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['action'], 'action1')


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestEXPTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestEXPTrackerPersistence))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

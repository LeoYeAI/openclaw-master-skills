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
Anima-AIOS v5.0 - Daily Quest System Tests

测试每日任务系统
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

from daily_quest import DailyQuestSystem


class TestDailyQuestSystem(unittest.TestCase):
    """每日任务系统测试"""
    
    def setUp(self):
        """测试前准备 - 创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent_name = "TestAgent"
        self.quest_system = DailyQuestSystem(self.agent_name, self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_quests(self):
        """测试任务生成"""
        today = datetime.now().strftime('%Y-%m-%d')
        quests_data = self.quest_system._generate_quests(today)
        
        # 验证基本结构
        self.assertEqual(quests_data['date'], today)
        self.assertEqual(quests_data['agent'], self.agent_name)
        self.assertIn('quests', quests_data)
        self.assertIn('total_exp_available', quests_data)
        self.assertIn('total_exp_earned', quests_data)
        
        # 验证有 4 个任务
        self.assertEqual(len(quests_data['quests']), 4)
        
        # 验证任务模板
        quest_ids = [q['id'] for q in quests_data['quests']]
        self.assertIn('write_fact', quest_ids)
        self.assertIn('memory_search', quest_ids)
        self.assertIn('complete_task', quest_ids)
        self.assertIn('collaboration', quest_ids)
    
    def test_get_today_quests(self):
        """测试获取今日任务"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 第一次获取（应该生成新任务）
        quests1 = self.quest_system.get_today_quests(today)
        self.assertEqual(len(quests1['quests']), 4)
        
        # 第二次获取（应该读取已有任务）
        quests2 = self.quest_system.get_today_quests(today)
        self.assertEqual(quests1['date'], quests2['date'])
    
    def test_quest_progress_check(self):
        """测试任务进度检查"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 生成任务
        quests_data = self.quest_system.get_today_quests(today)
        
        # 初始状态：所有任务未完成
        for quest in quests_data['quests']:
            self.assertFalse(quest['completed'])
            self.assertEqual(quest['current_count'], 0)
        
        # 检查进度（应该还是未完成，因为没有实际行为）
        updated_quests = self.quest_system.check_quest_progress(today)
        
        # 验证结构
        self.assertIn('total_exp_earned', updated_quests)
        self.assertEqual(updated_quests['total_exp_earned'], 0)
    
    def test_quest_card_generation(self):
        """测试任务卡片生成"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        card = self.quest_system.get_quest_card(today)
        
        # 验证卡片内容
        self.assertIn(today, card)
        self.assertIn(self.agent_name, card)
        self.assertIn('写 1 条事实', card)
        self.assertIn('搜索 1 次记忆', card)
        self.assertIn('完成 1 个任务', card)
        self.assertIn('参与 1 次协作', card)
        self.assertIn('EXP', card)
    
    def test_refresh_quests(self):
        """测试任务刷新"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 生成任务
        quests1 = self.quest_system.get_today_quests(today)
        generated_at1 = quests1['generated_at']
        
        # 刷新任务
        import time
        time.sleep(0.1)  # 确保时间戳不同
        quests2 = self.quest_system.refresh_quests(today)
        generated_at2 = quests2['generated_at']
        
        # 验证时间戳更新
        self.assertNotEqual(generated_at1, generated_at2)
    
    def test_all_quests_completion_bonus(self):
        """测试全部完成额外奖励"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 生成任务
        quests_data = self.quest_system.get_today_quests(today)
        
        # 手动标记所有任务为完成
        for quest in quests_data['quests']:
            quest['completed'] = True
            quest['completed_at'] = datetime.now().isoformat()
            quest['current_count'] = quest['target_count']
        
        # 保存
        quest_file = self.quest_system.quests_dir / f'{today}.json'
        with open(quest_file, 'w', encoding='utf-8') as f:
            json.dump(quests_data, f, ensure_ascii=False, indent=2)
        
        # 检查进度（应该触发额外奖励）
        updated_quests = self.quest_system.check_quest_progress(today)
        
        # 验证全部完成标志
        self.assertTrue(updated_quests['all_completed'])
        
        # 验证额外奖励已计入
        expected_total = sum(q['exp_reward'] for q in updated_quests['quests'])
        expected_total += self.quest_system.ALL_COMPLETE_BONUS
        self.assertEqual(updated_quests['total_exp_earned'], expected_total)
    
    def test_quest_templates_completeness(self):
        """测试任务模板完整性"""
        required_fields = ['id', 'title', 'description', 'dimension', 'exp_reward', 
                          'target_count', 'check_method', 'icon']
        
        for quest_id, template in self.quest_system.QUEST_TEMPLATES.items():
            for field in required_fields:
                self.assertIn(field, template, f"任务{quest_id}缺少字段{field}")
    
    def test_exp_reward_values(self):
        """测试 EXP 奖励值合理性"""
        # 验证 EXP 奖励在合理范围内
        for quest_id, template in self.quest_system.QUEST_TEMPLATES.items():
            exp = template['exp_reward']
            self.assertGreater(exp, 0, f"任务{quest_id}的 EXP 奖励应该>0")
            self.assertLessEqual(exp, 50, f"任务{quest_id}的 EXP 奖励应该<=50")
        
        # 验证额外奖励合理性
        self.assertGreater(self.quest_system.ALL_COMPLETE_BONUS, 0)
        self.assertLessEqual(self.quest_system.ALL_COMPLETE_BONUS, 100)


class TestQuestProgressDetection(unittest.TestCase):
    """任务进度检测测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.agent_name = "DetectTest"
        self.quest_system = DailyQuestSystem(self.agent_name, self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_count_facts(self):
        """测试 facts 计数"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 创建测试 facts 目录
        facts_dir = Path(self.temp_dir) / self.agent_name / 'facts'
        episodic_dir = facts_dir / 'episodic'
        episodic_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建测试 fact 文件
        fact_file = episodic_dir / f'test_fact_{today}.md'
        fact_file.write_text('Test content', encoding='utf-8')
        
        # 计数
        count = self.quest_system._count_facts_today(today)
        self.assertEqual(count, 1)
    
    def test_count_searches(self):
        """测试搜索次数计数"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 创建测试 exp_history
        agent_dir = Path(self.temp_dir) / self.agent_name
        exp_history_file = agent_dir / 'exp_history.jsonl'
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # 写入测试记录
        with open(exp_history_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps({
                'date': today,
                'dimension': 'application',
                'action': 'memory_search',
                'exp': 2
            }) + '\n')
        
        # 计数
        count = self.quest_system._count_searches_today(today)
        self.assertEqual(count, 1)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDailyQuestSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestProgressDetection))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

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
Memora v4.0 - Daily Quest System

每日任务系统

支持：
- 4 个通用基础任务
- 05:00 自动刷新
- 自动检测任务完成
- 全部完成额外奖励
- 每日推送通知（可选）

Author: 枢衡
Date: 2026-03-20
Version: 5.0.0
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from .exp_tracker import EXPTracker
except ImportError:
    from exp_tracker import EXPTracker


class DailyQuestSystem:
    """每日任务系统"""
    
    # 4 个通用基础任务配置
    QUEST_TEMPLATES = {
        'write_fact': {
            'id': 'write_fact',
            'title': '写 1 条事实',
            'description': '记录今天的工作或学习（episodic 或 semantic）',
            'dimension': 'understanding',
            'exp_reward': 1,
            'target_count': 1,
            'check_method': 'count_facts',
            'icon': '📝'
        },
        'memory_search': {
            'id': 'memory_search',
            'title': '搜索 1 次记忆',
            'description': '主动检索已有知识（使用 memory_search）',
            'dimension': 'application',
            'exp_reward': 2,
            'target_count': 1,
            'check_method': 'count_searches',
            'icon': '🔍'
        },
        'complete_task': {
            'id': 'complete_task',
            'title': '完成 1 个任务',
            'description': '完成任何工作任务（Vega 任务、代码任务等）',
            'dimension': 'application',
            'exp_reward': 30,
            'target_count': 1,
            'check_method': 'count_completed_tasks',
            'icon': '✅'
        },
        'collaboration': {
            'id': 'collaboration',
            'title': '参与 1 次协作',
            'description': '写入 shared/ 或读取他人知识，或协助他人',
            'dimension': 'collaboration',
            'exp_reward': 15,
            'target_count': 1,
            'check_method': 'count_collaboration',
            'icon': '💬'
        }
    }
    
    # 全部完成额外奖励
    ALL_COMPLETE_BONUS = 50
    
    def __init__(self, agent_name: str, facts_base: str = None):
        """
        初始化每日任务系统
        
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
        self.quests_dir = self.agent_dir / 'daily_quests'
        
        # 确保目录存在
        self.quests_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 EXP 追踪器
        self.exp_tracker = EXPTracker(agent_name, facts_base)
    
    def get_today_quests(self, date: Optional[str] = None) -> Dict:
        """
        获取今日任务列表
        
        Args:
            date: 日期（可选），默认今天
        
        Returns:
            任务状态字典
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        quest_file = self.quests_dir / f'{date}.json'
        
        if quest_file.exists():
            # 读取现有任务
            with open(quest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 生成新任务
            return self._generate_quests(date)
    
    def _generate_quests(self, date: str) -> Dict:
        """生成新的任务列表"""
        quests_data = {
            'date': date,
            'agent': self.agent_name,
            'generated_at': datetime.now().isoformat(),
            'quests': [],
            'total_exp_available': 0,
            'total_exp_earned': 0,
            'all_completed': False
        }
        
        # 添加 4 个基础任务
        for quest_id, template in self.QUEST_TEMPLATES.items():
            quest = {
                **template,
                'current_count': 0,
                'completed': False,
                'completed_at': None
            }
            quests_data['quests'].append(quest)
            quests_data['total_exp_available'] += quest['exp_reward']
        
        # 保存
        quest_file = self.quests_dir / f'{date}.json'
        with open(quest_file, 'w', encoding='utf-8') as f:
            json.dump(quests_data, f, ensure_ascii=False, indent=2)
        
        return quests_data
    
    def check_quest_progress(self, date: Optional[str] = None) -> Dict:
        """
        检查任务进度
        
        Args:
            date: 日期（可选）
        
        Returns:
            更新后的任务状态
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        quests_data = self.get_today_quests(date)
        
        # 检查每个任务的进度
        for quest in quests_data['quests']:
            if quest['completed']:
                continue  # 已完成的任务跳过
            
            # 根据 check_method 检查进度
            method = quest.get('check_method', '')
            
            if method == 'count_facts':
                count = self._count_facts_today(date)
                quest['current_count'] = count
            
            elif method == 'count_searches':
                count = self._count_searches_today(date)
                quest['current_count'] = count
            
            elif method == 'count_completed_tasks':
                count = self._count_completed_tasks_today(date)
                quest['current_count'] = count
            
            elif method == 'count_collaboration':
                count = self._count_collaboration_today(date)
                quest['current_count'] = count
            
            # 检查是否完成
            if quest['current_count'] >= quest['target_count']:
                quest['completed'] = True
                quest['completed_at'] = datetime.now().isoformat()
                
                # 发放 EXP 奖励
                self._award_exp(quest, date)
        
        # 检查是否全部完成
        all_completed = all(q['completed'] for q in quests_data['quests'])
        
        if all_completed and not quests_data['all_completed']:
            # 发放额外奖励
            quests_data['all_completed'] = True
            self._award_bonus(date)
        
        # 更新总 EXP
        quests_data['total_exp_earned'] = sum(
            q['exp_reward'] for q in quests_data['quests'] if q['completed']
        )
        if quests_data['all_completed']:
            quests_data['total_exp_earned'] += self.ALL_COMPLETE_BONUS
        
        # 保存更新
        quest_file = self.quests_dir / f'{date}.json'
        with open(quest_file, 'w', encoding='utf-8') as f:
            json.dump(quests_data, f, ensure_ascii=False, indent=2)
        
        return quests_data
    
    def _count_facts_today(self, date: str) -> int:
        """统计今天写的 facts 数量"""
        facts_dir = self.agent_dir / 'facts'
        if not facts_dir.exists():
            return 0
        
        count = 0
        for fact_type in ['episodic', 'semantic']:
            type_dir = facts_dir / fact_type
            if type_dir.exists():
                for fact_file in type_dir.glob(f'*{date}*.md'):
                    count += 1
        
        return count
    
    def _count_searches_today(self, date: str) -> int:
        """统计今天的记忆搜索次数（BUG-017 修复：多源统计）"""
        exp_history = self.exp_tracker.get_exp_history(date, date, 'application')
        # 匹配所有可能的搜索相关 action
        search_actions = (
            'memory_search', 'import_from_sessions',
            'knowledge_reuse', 'search_then_complete_task',
        )
        count = sum(1 for r in exp_history if r.get('action') in search_actions)

        # fallback: 如果没有精确匹配，至少算有 application 维度的 EXP 存在
        if count == 0 and len(exp_history) > 0:
            count = 1  # 有 application 记录就至少算 1 次

        return count
    
    def _count_completed_tasks_today(self, date: str) -> int:
        """统计今天完成的任务数"""
        # 从 exp_history 统计
        exp_history = self.exp_tracker.get_exp_history(date, date)
        return sum(1 for r in exp_history if r.get('action') == 'complete_task')
    
    def _count_collaboration_today(self, date: str) -> int:
        """统计今天的协作次数"""
        # 检查 shared/ 目录
        shared_dir = self.facts_base / 'shared'
        count = 0
        
        if shared_dir.exists():
            for shared_file in shared_dir.glob(f'*{date}*.md'):
                try:
                    content = shared_file.read_text(encoding='utf-8')
                    if self.agent_name in content:
                        count += 1
                except Exception:
                    continue
        
        # 从 exp_history 统计协作行为
        exp_history = self.exp_tracker.get_exp_history(date, date, 'collaboration')
        count += len(exp_history)
        
        return count
    
    def _award_exp(self, quest: Dict, date: str):
        """发放任务 EXP 奖励"""
        dimension = quest['dimension']
        exp = quest['exp_reward']
        
        self.exp_tracker.add_exp(
            dimension=dimension,
            action=f'complete_quest_{quest["id"]}',
            exp=exp,
            details={'quest_id': quest['id'], 'quest_title': quest['title']},
            date=date
        )
    
    def _award_bonus(self, date: str):
        """发放全部完成额外奖励"""
        self.exp_tracker.add_exp(
            dimension='application',  # 额外奖励计入应用维度
            action='all_quests_completed',
            exp=self.ALL_COMPLETE_BONUS,
            details={'bonus': 'all_quests_completed'},
            date=date
        )
    
    def refresh_quests(self, date: Optional[str] = None) -> Dict:
        """
        刷新任务（生成新一天的任务）
        
        Args:
            date: 日期（可选）
        
        Returns:
            新的任务列表
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 删除旧任务（如果存在）
        quest_file = self.quests_dir / f'{date}.json'
        if quest_file.exists():
            quest_file.unlink()
        
        # 生成新任务
        return self._generate_quests(date)
    
    def get_quest_card(self, date: Optional[str] = None) -> str:
        """
        生成任务卡片（Markdown 格式）
        
        Args:
            date: 日期（可选）
        
        Returns:
            Markdown 格式的任务卡片
        """
        quests_data = self.get_today_quests(date)
        
        lines = []
        lines.append(f"📅 每日任务 — {quests_data['date']}")
        lines.append("")
        lines.append(f"**Agent:** {self.agent_name}")
        lines.append("")
        
        # 任务列表
        for quest in quests_data['quests']:
            icon = quest.get('icon', '⬜')
            status = '✅' if quest['completed'] else '⬜'
            progress = f"{quest['current_count']}/{quest['target_count']}"
            
            lines.append(f"{status} {icon} **{quest['title']}** (+{quest['exp_reward']} EXP)")
            lines.append(f"   {quest['description']}")
            lines.append(f"   进度：{progress}")
            lines.append("")
        
        # 总结
        lines.append("---")
        lines.append("")
        
        earned = quests_data['total_exp_earned']
        available = quests_data['total_exp_available']
        
        if quests_data['all_completed']:
            lines.append(f"🎉 **全部完成！** 获得额外奖励 +{self.ALL_COMPLETE_BONUS} EXP")
        
        lines.append(f"**今日获得:** {earned}/{available} EXP")
        lines.append("")
        
        return '\n'.join(lines)


def main():
    """测试每日任务系统"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 daily_quest.py <Agent 名称> [命令]")
        print("命令：status, refresh, check")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    quest_system = DailyQuestSystem(agent_name)
    
    command = sys.argv[2] if len(sys.argv) > 2 else 'status'
    
    if command == 'status':
        # 显示今日任务
        card = quest_system.get_quest_card()
        print(card)
    
    elif command == 'refresh':
        # 刷新任务
        quests = quest_system.refresh_quests()
        print(f"✅ 任务已刷新（{quests['date']}）")
        print(quest_system.get_quest_card())
    
    elif command == 'check':
        # 检查进度
        quests = quest_system.check_quest_progress()
        print(f"✅ 进度已更新")
        print(quest_system.get_quest_card())
    
    else:
        print(f"未知命令：{command}")


if __name__ == '__main__':
    main()

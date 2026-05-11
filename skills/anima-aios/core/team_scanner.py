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
Memora v4.0 - Team Scanner

自动扫描活跃 Agent，无需手动配置团队规模

判断标准：
- 存在 facts 目录
- 最近 N 天有活动（写 facts、exp 记录等）
- 排除特殊目录（shared、模板等）

Author: 枢衡
Date: 2026-03-20
Version: 5.0.0
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime, timedelta


class TeamScanner:
    """团队扫描器"""
    
    # 默认活跃度判断窗口（天）
    DEFAULT_ACTIVE_DAYS = 30
    
    # 排除的目录名
    EXCLUDED_DIRS = {'shared', 'templates', 'backup', 'archive'}
    
    def __init__(self, facts_base: str = None, active_days: int = DEFAULT_ACTIVE_DAYS):
        """
        初始化团队扫描器
        
        Args:
            facts_base: facts 基础路径
            active_days: 活跃度判断窗口（天）
        """
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                import sys as _s; _s.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / 'config')); from path_config import get_config
            facts_base = str(get_config().facts_base)
        self.facts_base = Path(facts_base)
        self.active_days = active_days
    
    def scan_active_agents(self) -> List[str]:
        """
        扫描活跃的 Agent 列表
        
        Returns:
            活跃 Agent 名称列表
        """
        if not self.facts_base.exists():
            return []
        
        active_agents = []
        
        for agent_dir in self.facts_base.iterdir():
            # 跳过非目录
            if not agent_dir.is_dir():
                continue
            
            # 跳过排除目录
            if agent_dir.name in self.EXCLUDED_DIRS:
                continue
            
            # 跳过隐藏目录
            if agent_dir.name.startswith('.'):
                continue
            
            # 检查是否活跃
            if self._is_agent_active(agent_dir):
                active_agents.append(agent_dir.name)
        
        return sorted(active_agents)
    
    def _is_agent_active(self, agent_dir: Path) -> bool:
        """
        判断 Agent 是否活跃
        
        Args:
            agent_dir: Agent 目录
        
        Returns:
            True 表示活跃
        """
        # 检查最后活动时间
        last_activity = self._get_last_activity_date(agent_dir)
        
        if last_activity is None:
            return False
        
        # 判断是否在活跃窗口内
        days_since_activity = (datetime.now() - last_activity).days
        return days_since_activity <= self.active_days
    
    def _get_last_activity_date(self, agent_dir: Path) -> Optional[datetime]:
        """
        获取 Agent 最后活动日期
        
        检查来源：
        1. facts 目录（episodic/semantic）
        2. exp_history.jsonl
        3. daily_quests 目录
        4. cognitive_profile.json
        
        Args:
            agent_dir: Agent 目录
        
        Returns:
            最后活动日期，无活动返回 None
        """
        last_date = None
        
        # 1. 检查 facts 目录
        facts_dir = agent_dir / 'facts'
        if facts_dir.exists():
            for fact_type in ['episodic', 'semantic']:
                type_dir = facts_dir / fact_type
                if type_dir.exists():
                    for fact_file in type_dir.glob('*.md'):
                        file_date = self._extract_date_from_file(fact_file)
                        if file_date and (last_date is None or file_date > last_date):
                            last_date = file_date
        
        # 2. 检查 exp_history.jsonl
        exp_history_file = agent_dir / 'exp_history.jsonl'
        if exp_history_file.exists():
            try:
                with open(exp_history_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        # 读取最后一行
                        last_line = lines[-1].strip()
                        if last_line:
                            import json
                            record = json.loads(last_line)
                            date_str = record.get('date', '')
                            if date_str:
                                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                                if last_date is None or file_date > last_date:
                                    last_date = file_date
            except Exception:
                pass
        
        # 3. 检查 daily_quests 目录
        quests_dir = agent_dir / 'daily_quests'
        if quests_dir.exists():
            for quest_file in quests_dir.glob('*.json'):
                file_date = self._extract_date_from_file(quest_file)
                if file_date and (last_date is None or file_date > last_date):
                    last_date = file_date
        
        # 4. 检查 cognitive_profile.json
        profile_file = agent_dir / 'cognitive_profile.json'
        if profile_file.exists():
            try:
                import json
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    generated_at = profile.get('generated_at', '')
                    if generated_at:
                        # ISO 格式：2026-03-20T10:30:00.123456
                        file_date = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                        # 转换为本地日期
                        file_date = file_date.replace(tzinfo=None)
                        if last_date is None or file_date > last_date:
                            last_date = file_date
            except Exception:
                pass
        
        return last_date
    
    def _extract_date_from_file(self, file_path: Path) -> Optional[datetime]:
        """从文件名提取日期"""
        import re
        
        filename = file_path.name
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d')
            except Exception:
                pass
        
        # 尝试从文件修改时间
        try:
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime)
        except Exception:
            pass
        
        return None
    
    def get_team_statistics(self) -> Dict:
        """
        获取团队统计信息
        
        Returns:
            统计信息字典
        """
        active_agents = self.scan_active_agents()
        
        stats = {
            'total_agents': len(active_agents),
            'active_agents': active_agents,
            'scan_time': datetime.now().isoformat(),
            'active_window_days': self.active_days
        }
        
        # 各 Agent 最后活动时间
        agent_activity = {}
        for agent_name in active_agents:
            agent_dir = self.facts_base / agent_name
            last_date = self._get_last_activity_date(agent_dir)
            agent_activity[agent_name] = last_date.isoformat() if last_date else None
        
        stats['agent_last_activity'] = agent_activity
        
        return stats
    
    def get_team_size_for_normalization(self) -> int:
        """
        获取用于归一化的团队规模
        
        Returns:
            团队规模（整数）
        """
        return len(self.scan_active_agents())


def main():
    """测试团队扫描器"""
    import sys
    
    scanner = TeamScanner()
    
    print("\n=== 团队扫描结果 ===\n")
    
    # 扫描活跃 Agent
    active_agents = scanner.scan_active_agents()
    
    if not active_agents:
        print("⚠️  未检测到活跃的 Agent")
        print(f"   检查路径：{scanner.facts_base}")
        print(f"   活跃窗口：{scanner.active_days} 天")
    else:
        print(f"活跃 Agent 数量：{len(active_agents)}")
        print(f"活跃窗口：{scanner.active_days} 天")
        print("\n活跃 Agent 列表:")
        for agent in active_agents:
            print(f"  - {agent}")
        
        # 详细统计
        print("\n=== 详细统计 ===\n")
        stats = scanner.get_team_statistics()
        
        for agent, last_activity in stats['agent_last_activity'].items():
            if last_activity:
                days_ago = (datetime.now() - datetime.fromisoformat(last_activity)).days
                print(f"{agent:15s}: 最后活动 {last_activity[:10]} ({days_ago} 天前)")
            else:
                print(f"{agent:15s}: 未知")
        
        # 归一化建议
        print("\n=== 归一化模式建议 ===\n")
        team_size = stats['total_agents']
        
        if team_size >= 5:
            print("建议模式：百分位数归一化（大团队）")
        elif team_size >= 2:
            print("建议模式：混合归一化（小团队）")
        else:
            print("建议模式：绝对基准归一化（单 Agent）")
    
    print()


if __name__ == '__main__':
    main()

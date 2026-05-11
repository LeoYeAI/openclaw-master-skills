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
Memora v4.0 - Level System

等级系统（累积制）

等级基于累计 EXP，只增不减：
- EXP 只增不减（累积制）
- 等级基于 EXP 总量
- 每天继续积累，不会掉级

EXP 获取：
- 写 episodic fact: +1 EXP
- 写 semantic fact: +2 EXP
- 搜索记忆：+2 EXP
- 分享知识到 shared/: +5 EXP
- 写周报/复盘：+5 EXP
- 协作任务：+3 EXP

等级公式：
exp_to_level = base_exp * (level ** 1.5)
Level 1→2: 100 EXP
Level 10→20: 316 EXP
Level 20→30: 1000 EXP
Level 30→40: 2000 EXP

Author: 枢衡
Date: 2026-03-20
Version: 5.0.0
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class LevelSystem:
    """等级系统（累积制）"""
    
    # EXP 配置
    EXP_RULES = {
        'write_episodic_fact': 1,
        'write_semantic_fact': 2,
        'memory_search': 2,
        'share_knowledge': 5,
        'weekly_review': 5,
        'collab_task': 3,
    }
    
    # 等级公式参数
    # 新公式：level = max(1, int(exp ^ 0.28))
    # 
    # 设计理念：
    # - 人生是一场漫长的游戏，升级要慢
    # - 第一天：努力能看到进步（Lv.1-3）
    # - 第一周：持续成长（Lv.5-8）
    # - 第一月：长期坚持（Lv.12-15）
    # - 第一年：长期目标（Lv.25-30）
    # - 满级：需要数年修行（Lv.100，约 1400 万 EXP）
    #
    # 等级需求:
    # - 2 EXP → Lv.1（新手起步）
    # - 10 EXP → Lv.1（持续努力）
    # - 85 EXP → Lv.3（遥遥领先）
    # - 1000 EXP → Lv.6（第 1 周）
    # - 10000 EXP → Lv.13（第 1 月）
    # - 100000 EXP → Lv.25（第 1 年）
    # - 1000000 EXP → Lv.47（数年修行）
    # - 14000000 EXP → Lv.100（终身成就）
    
    LEVEL_FORMULA_POWER = 0.28
    MAX_LEVEL = 100
    
    def __init__(self, agent_name: str, facts_base: str = None):
        """
        初始化等级系统
        
        Args:
            agent_name: Agent 名称
            facts_base: facts 基础路径
        """
        self.agent_name = agent_name
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                import sys as _s
                from pathlib import Path as _P
                _s.path.insert(0, str(_P(__file__).parent.parent / 'config'))
                from path_config import get_config
            facts_base = str(get_config().facts_base)
        self.agent_dir = Path(facts_base) / agent_name
        self.exp_file = self.agent_dir / 'exp_history.jsonl'
        self.level_file = self.agent_dir / 'level.json'
        
        # 确保目录存在
        self.agent_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_total_exp(self) -> int:
        """
        计算累计总 EXP
        
        Returns:
            累计 EXP 总量
        """
        total_exp = 0
        
        if not self.exp_file.exists():
            return total_exp
        
        with open(self.exp_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    exp = record.get('exp', 0)
                    total_exp += exp
                except Exception:
                    continue
        
        return total_exp
    
    def exp_to_level(self, total_exp: int) -> int:
        """
        根据 EXP 计算等级
        
        新公式：level = max(1, int(exp ^ 0.28))
        
        设计理念：
        - 人生是一场漫长的游戏，升级要慢
        - 第一天：努力能看到进步（Lv.1-3）
        - 第一周：持续成长（Lv.5-8）
        - 第一月：长期坚持（Lv.12-15）
        - 第一年：长期目标（Lv.25-30）
        - 满级：需要数年修行（Lv.100，约 1400 万 EXP）
        
        等级需求:
        - 2 EXP → Lv.1（新手起步）
        - 10 EXP → Lv.1（持续努力）
        - 85 EXP → Lv.3（遥遥领先）
        - 1000 EXP → Lv.6（第 1 周）
        - 10000 EXP → Lv.13（第 1 月）
        - 100000 EXP → Lv.25（第 1 年）
        - 1000000 EXP → Lv.47（数年修行）
        - 14000000 EXP → Lv.100（终身成就）
        
        Args:
            total_exp: 累计总 EXP
        
        Returns:
            等级（1-100）
        """
        if total_exp <= 0:
            return 1
        
        # 新公式：0.28 次方曲线（更慢）
        level = int(total_exp ** self.LEVEL_FORMULA_POWER)
        
        # 限制最低等级为 1，最高等级为 100
        return max(1, min(level, self.MAX_LEVEL))
    
    def get_level_info(self) -> Dict:
        """
        获取等级信息
        
        Returns:
            {
                'level': int,
                'total_exp': int,
                'exp_to_next_level': int,
                'progress': float (0-1)
            }
        """
        total_exp = self.calculate_total_exp()
        current_level = self.exp_to_level(total_exp)
        
        # 计算下一级需要的 EXP（反向公式）
        # level = exp ^ 0.28 → exp = level ^ (1/0.28) ≈ level ^ 3.57
        next_level = current_level + 1
        next_level_exp = int(next_level ** (1 / self.LEVEL_FORMULA_POWER))
        current_level_exp = int(current_level ** (1 / self.LEVEL_FORMULA_POWER)) if current_level > 0 else 0
        
        # 计算进度
        exp_in_level = total_exp - current_level_exp
        exp_needed = next_level_exp - current_level_exp
        progress = exp_in_level / exp_needed if exp_needed > 0 else 0
        
        return {
            'level': current_level,
            'total_exp': total_exp,
            'exp_to_next_level': next_level_exp,
            'current_level_exp': current_level_exp,
            'progress': round(progress, 2),
            'updated_at': datetime.now().isoformat()
        }
    
    def add_exp(self, action: str, exp: int, details: Optional[Dict] = None):
        """
        添加 EXP 记录
        
        Args:
            action: 行为类型
            exp: EXP 数量
            details: 详细信息
        """
        record = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'action': action,
            'exp': exp,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            record['details'] = details
        
        # 追加到 JSONL 文件
        with open(self.exp_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def save_level(self):
        """保存等级信息"""
        level_info = self.get_level_info()
        
        with open(self.level_file, 'w', encoding='utf-8') as f:
            json.dump(level_info, f, ensure_ascii=False, indent=2)
    
    def get_level_badge(self, level: int) -> str:
        """
        获取等级徽章
        
        Args:
            level: 等级
        
        Returns:
            徽章 emoji
        """
        if level >= 90:
            return '👑 Legendary'
        elif level >= 80:
            return '🏆 Master'
        elif level >= 60:
            return '🌳 Expert'
        elif level >= 40:
            return '🌿 Advanced'
        else:
            return '🌱 Novice'
    
    def get_level_stage(self, level: int) -> str:
        """
        获取等级阶段名称
        
        Args:
            level: 等级
        
        Returns:
            阶段名称
        """
        if level >= 90:
            return 'Expert 专家'
        elif level >= 80:
            return 'Proficient 熟练者'
        elif level >= 60:
            return 'Competent 胜任者'
        elif level >= 40:
            return 'Advanced Beginner 高级初学者'
        else:
            return 'Novice 新手'


def main():
    """测试等级系统"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 level_system.py <Agent 名称>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    level_sys = LevelSystem(agent_name)
    
    # 计算等级
    level_info = level_sys.get_level_info()
    
    print(f"\n=== {agent_name} 的等级信息 ===\n")
    print(f"等级：Lv.{level_info['level']} {level_sys.get_level_badge(level_info['level'])}")
    print(f"阶段：{level_sys.get_level_stage(level_info['level'])}")
    print(f"累计 EXP: {level_info['total_exp']}")
    print(f"下一级需要：{level_info['exp_to_next_level']} EXP")
    print(f"当前等级进度：{level_info['progress']*100:.0f}%")
    print()


if __name__ == '__main__':
    main()

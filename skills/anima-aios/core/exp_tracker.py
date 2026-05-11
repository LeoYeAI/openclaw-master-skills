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
Memora v4.0 - EXP Tracker v2

多维度 EXP 追踪引擎

支持：
- 5 个认知维度的 EXP 记录
- 每日 EXP 上限（防刷）
- EXP 历史记录（JSONL 格式）
- 质量系数（基于内容长度、类型）

Author: 枢衡
Date: 2026-03-22
Version: 5.0.3
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import hashlib


class EXPTracker:
    """多维度 EXP 追踪引擎"""
    
    # 每日 EXP 上限（防刷）
    DAILY_EXP_LIMITS = {
        'understanding': 50,
        'application': 40,
        'creation': 60,
        'metacognition': 30,
        'collaboration': 50
    }
    
    # 质量系数配置
    QUALITY_THRESHOLDS = {
        'fact': {
            'short': 50,      # <50 字，质量系数 0.3
            'normal': 200,    # 50-200 字，质量系数 1.0
            'long': 200       # >200 字，质量系数 1.5
        }
    }
    
    def __init__(self, agent_name: str, facts_base: str = None):
        """
        初始化 EXP 追踪器
        
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
        
        # 确保目录存在
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        
        # EXP 历史文件路径
        self.exp_history_file = self.agent_dir / 'exp_history.jsonl'
        self.daily_exp_file = self.agent_dir / 'daily_exp.json'
    
    def add_exp(self, dimension: str, action: str, exp: float, details: Optional[Dict] = None, 
                date: Optional[str] = None, quality_multiplier: float = 1.0) -> Tuple[bool, str]:
        """
        添加 EXP 记录
        
        Args:
            dimension: 认知维度
            action: 行为类型
            exp: 基础 EXP 值
            details: 详细信息（可选）
            date: 日期（可选），默认今天
            quality_multiplier: 质量系数（可选）
        
        Returns:
            (success, message)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 检查每日上限（先检查基础 EXP，质量奖励作为额外奖励）
        current_exp = self._get_daily_exp(dimension, date)
        limit = self.DAILY_EXP_LIMITS.get(dimension, 50)
        
        # 修复 Bug 006：质量系数不应导致更容易触达上限
        # 修复 Bug v5.0.3：质量系数 <1 时不惩罚，保证最小 base_exp
        # 基础 EXP 计入上限，质量奖励作为额外奖励（不占上限）
        base_exp_to_add = min(exp, limit - current_exp)  # 基础 EXP 受上限限制
        
        # v5.0.3 修复：质量系数只奖励不惩罚
        # quality_multiplier > 1 时才有奖励，< 1 时只是没有奖励（但不扣减）
        if quality_multiplier > 1.0:
            quality_bonus = exp * (quality_multiplier - 1.0)  # 质量奖励部分
        else:
            quality_bonus = 0.0  # 质量系数 <1 时不惩罚，保证 base_exp
        
        # 质量奖励也受剩余空间限制，但不影响基础 EXP
        if current_exp + base_exp_to_add >= limit:
            # 基础 EXP 已达上限，质量奖励也无法添加
            remaining = limit - current_exp
            if remaining <= 0:
                return False, f"今日 {dimension} 维度 EXP 已达上限 ({limit})"
            final_exp = remaining
            message = f"添加 EXP {final_exp:.1f}（达到今日上限）"
        else:
            # 基础 EXP 未达上限，可以添加质量奖励
            remaining_after_base = limit - (current_exp + base_exp_to_add)
            quality_bonus_to_add = min(quality_bonus, remaining_after_base)
            final_exp = base_exp_to_add + quality_bonus_to_add
            if quality_bonus > 0:
                message = f"添加 EXP {final_exp:.1f}（基础 {base_exp_to_add:.1f} + 质量奖励 {quality_bonus_to_add:.1f}）"
            else:
                message = f"添加 EXP {final_exp:.1f}（基础 EXP，质量系数 {quality_multiplier}）"
        
        # 创建记录
        record = {
            'date': date,
            'dimension': dimension,
            'action': action,
            'exp': round(final_exp, 2),
            'base_exp': exp,
            'quality_multiplier': quality_multiplier,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            record['details'] = details
        
        # 追加到 JSONL 文件
        try:
            with open(self.exp_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            # 更新每日 EXP 统计
            self._update_daily_exp(dimension, date, final_exp)
            
            return True, message
        except Exception as e:
            return False, f"写入失败：{str(e)}"
    
    def _get_daily_exp(self, dimension: str, date: str) -> float:
        """获取指定日期的 EXP 总和"""
        total = 0.0
        
        if not self.exp_history_file.exists():
            return total
        
        with open(self.exp_history_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get('date') == date and record.get('dimension') == dimension:
                        total += record.get('exp', 0)
                except Exception:
                    continue
        
        return total
    
    def _update_daily_exp(self, dimension: str, date: str, exp: float):
        """更新每日 EXP 统计文件"""
        # 加载现有数据
        daily_exp = {}
        if self.daily_exp_file.exists():
            try:
                with open(self.daily_exp_file, 'r', encoding='utf-8') as f:
                    daily_exp = json.load(f)
            except Exception:
                daily_exp = {}
        
        # 更新
        if date not in daily_exp:
            daily_exp[date] = {}
        
        if dimension not in daily_exp[date]:
            daily_exp[date][dimension] = 0.0
        
        daily_exp[date][dimension] += exp
        
        # 保存
        with open(self.daily_exp_file, 'w', encoding='utf-8') as f:
            json.dump(daily_exp, f, ensure_ascii=False, indent=2)
    
    def get_exp_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                        dimension: Optional[str] = None) -> List[Dict]:
        """
        获取 EXP 历史记录
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            dimension: 维度过滤
        
        Returns:
            EXP 记录列表
        """
        history = []
        
        if not self.exp_history_file.exists():
            return history
        
        with open(self.exp_history_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    record_date = record.get('date', '')
                    
                    # 过滤日期
                    if start_date and record_date < start_date:
                        continue
                    if end_date and record_date > end_date:
                        continue
                    
                    # 过滤维度
                    if dimension and record.get('dimension') != dimension:
                        continue
                    
                    history.append(record)
                except Exception:
                    continue
        
        return history
    
    def get_total_exp(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                      dimension: Optional[str] = None) -> float:
        """获取总 EXP"""
        history = self.get_exp_history(start_date, end_date, dimension)
        return sum(record.get('exp', 0) for record in history)
    
    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """
        获取每日 EXP 摘要
        
        Args:
            date: 日期（默认今天）
        
        Returns:
            每日摘要字典
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        summary = {
            'date': date,
            'dimensions': {},
            'total': 0.0
        }
        
        if self.daily_exp_file.exists():
            try:
                with open(self.daily_exp_file, 'r', encoding='utf-8') as f:
                    daily_exp = json.load(f)
                
                if date in daily_exp:
                    summary['dimensions'] = daily_exp[date]
                    summary['total'] = sum(daily_exp[date].values())
            except Exception:
                pass
        
        return summary
    
    def calculate_quality_multiplier(self, content: str, content_type: str = 'fact') -> float:
        """
        计算质量系数
        
        Args:
            content: 内容
            content_type: 内容类型
        
        Returns:
            质量系数（0.3 - 1.5）
        """
        thresholds = self.QUALITY_THRESHOLDS.get(content_type, {})
        
        if not thresholds:
            return 1.0
        
        length = len(content)
        
        if length < thresholds.get('short', 50):
            return 0.3  # 太短，可能无效
        elif length < thresholds.get('normal', 200):
            return 1.0  # 正常
        else:
            return 1.5  # 深度内容
    
    def check_duplicate(self, action: str, details: Dict, date: Optional[str] = None) -> bool:
        """
        检查重复行为（防刷）
        
        Args:
            action: 行为类型
            details: 详细信息
            date: 日期
        
        Returns:
            True 表示重复，False 表示不重复
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 生成内容哈希
        content_hash = hashlib.md5(
            json.dumps(details, sort_keys=True).encode()
        ).hexdigest()
        
        # 检查最近记录
        history = self.get_exp_history(date, date)
        
        for record in history:
            if record.get('action') == action:
                record_details = record.get('details', {})
                record_hash = record_details.get('content_hash', '')
                
                if record_hash == content_hash:
                    return True  # 重复
        
        return False
    
    def export_exp_report(self, output_path: str, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> str:
        """
        导出 EXP 报告
        
        Args:
            output_path: 输出路径
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            输出文件路径
        """
        history = self.get_exp_history(start_date, end_date)
        
        # 按维度汇总
        dimension_summary = {}
        daily_summary = {}
        
        for record in history:
            dim = record.get('dimension', 'unknown')
            date = record.get('date', 'unknown')
            exp = record.get('exp', 0)
            
            if dim not in dimension_summary:
                dimension_summary[dim] = 0.0
            dimension_summary[dim] += exp
            
            if date not in daily_summary:
                daily_summary[date] = 0.0
            daily_summary[date] += exp
        
        # 生成报告
        report = {
            'agent': self.agent_name,
            'period': {
                'start': start_date or 'all',
                'end': end_date or 'today'
            },
            'total_exp': sum(dimension_summary.values()),
            'dimension_summary': dimension_summary,
            'daily_summary': dict(sorted(daily_summary.items())),
            'record_count': len(history)
        }
        
        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(output_path)


def main():
    """测试 EXP 追踪器"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 exp_tracker.py <Agent 名称> [命令] [参数]")
        print("命令：add, summary, history, report")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    tracker = EXPTracker(agent_name)
    
    command = sys.argv[2] if len(sys.argv) > 2 else 'summary'
    
    if command == 'add':
        # 测试添加 EXP
        success, message = tracker.add_exp(
            dimension='understanding',
            action='write_semantic_fact',
            exp=2,
            details={'fact_id': 'test_001'},
            quality_multiplier=1.5
        )
        print(f"{'✅' if success else '❌'} {message}")
    
    elif command == 'summary':
        # 显示今日摘要
        summary = tracker.get_daily_summary()
        print(f"\n=== {agent_name} 今日 EXP 摘要 ===\n")
        print(f"日期：{summary['date']}")
        print(f"总计：{summary['total']:.1f} EXP")
        print("\n各维度:")
        for dim, exp in summary['dimensions'].items():
            print(f"  {dim:15s}: {exp:.1f}")
    
    elif command == 'history':
        # 显示历史记录
        history = tracker.get_exp_history()
        print(f"\n=== {agent_name} EXP 历史记录（最近 10 条）===\n")
        for record in history[-10:]:
            print(f"{record['date']} | {record['dimension']:15s} | {record['action']:20s} | +{record['exp']:.1f} EXP")
    
    elif command == 'report':
        # 导出报告
        output_path = tracker.export_exp_report(f'/tmp/{agent_name}_exp_report.json')
        print(f"✅ EXP 报告已导出到：{output_path}")
    
    else:
        print(f"未知命令：{command}")


if __name__ == '__main__':
    main()

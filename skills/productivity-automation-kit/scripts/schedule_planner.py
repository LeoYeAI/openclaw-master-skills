#!/usr/bin/env python3
"""
日程管理助手脚本
用途: 生成每日/每周日程计划，管理时间块
"""

import json
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Dict, Optional


class SchedulePlanner:
    """日程规划器"""
    
    # 默认时间块配置
    DEFAULT_TIME_BLOCKS = [
        {"start": "06:00", "end": "08:00", "label": "晨间准备 + 深度工作", "energy": "high"},
        {"start": "08:00", "end": "10:00", "label": "高价值任务 (创意/决策)", "energy": "high"},
        {"start": "10:00", "end": "12:00", "label": "会议 + 协作", "energy": "medium"},
        {"start": "12:00", "end": "13:30", "label": "午餐 + 休息", "energy": "low"},
        {"start": "13:30", "end": "15:30", "label": "下午工作 (邮件/琐事)", "energy": "medium"},
        {"start": "15:30", "end": "17:30", "label": "收尾工作 + 明日计划", "energy": "medium"},
        {"start": "17:30", "end": "19:00", "label": "个人时间", "energy": "low"},
        {"start": "19:00", "end": "22:00", "label": "弹性时间 / 副业", "energy": "medium"},
        {"start": "22:00", "end": "06:00", "label": "睡眠", "energy": "rest"},
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.tasks: List[Dict] = []
        self.schedule: List[Dict] = []
    
    def _load_config(self, path: str) -> Dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_task(self, name: str, duration_minutes: int, priority: int = 2,
                 energy_required: str = 'medium', deadline: Optional[str] = None) -> None:
        """添加任务"""
        self.tasks.append({
            'name': name,
            'duration_minutes': duration_minutes,
            'priority': priority,  # 0=最高, 3=最低
            'energy_required': energy_required,
            'deadline': deadline,
            'scheduled': False
        })
    
    def plan_daily(self, date_str: Optional[str] = None, energy_schedule: Optional[Dict] = None) -> str:
        """生成每日日程"""
        date_str = date_str or datetime.now().strftime('%Y-%m-%d')
        energy_schedule = energy_schedule or {}
        
        # 按优先级和能量需求排序任务
        sorted_tasks = sorted(
            [t for t in self.tasks if not t['scheduled']],
            key=lambda x: (x['priority'], -x['duration_minutes'])
        )
        
        report = f"""# 📅 日程计划 - {date_str}

## ⏰ 今日时间块

"""
        
        for block in self.DEFAULT_TIME_BLOCKS:
            start, end = block['start'], block['end']
            label = block['label']
            energy = block['energy']
            
            report += f"| {start}-{end} | {label} | {energy.upper()} |\n"
            
            # 尝试分配任务到这个时间块
            assigned = []
            for task in sorted_tasks:
                if task['scheduled']:
                    continue
                if energy in [task['energy_required'], 'medium']:
                    available_mins = self._calc_duration(start, end)
                    if task['duration_minutes'] <= available_mins:
                        assigned.append(task)
                        task['scheduled'] = True
            
            if assigned:
                for task in assigned:
                    report += f"  → 📌 {task['name']} ({task['duration_minutes']}分钟)\n"
        
        # 未分配的任务
        unscheduled = [t for t in sorted_tasks if not t['scheduled']]
        if unscheduled:
            report += f"\n## ⚠️ 待安排任务\n"
            for task in unscheduled:
                report += f"- [ ] {task['name']} ({task['duration_minutes']}分钟, P{task['priority']})\n"
        
        return report
    
    def plan_weekly(self, start_date: Optional[str] = None) -> str:
        """生成每周计划"""
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else datetime.now()
        
        report = f"""# 📆 周计划 - {start_date.strftime('%Y-%m-%d')} 周

## 本周核心目标 (Top 3)
1. [目标1]
2. [目标2]
3. [目标3]

## 每日安排概要

"""
        
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_name = day.strftime('%A')
            is_weekend = day.weekday() >= 5
            
            report += f"### {day.strftime('%Y-%m-%d')} {day_name}\n"
            
            if is_weekend:
                report += "- 周末：休息 + 充电\n"
            else:
                report += "- [ ] 晨间深度工作 (2h)\n"
                report += "- [ ] 核心任务\n"
                report += "- [ ] 会议/协作\n"
                report += "- [ ] 收尾 + 明日计划\n"
            
            report += "\n"
        
        return report
    
    def _calc_duration(self, start: str, end: str) -> int:
        """计算时间块时长(分钟)"""
        start_h, start_m = map(int, start.split(':'))
        end_h, end_m = map(int, end.split(':'))
        return (end_h * 60 + end_m) - (start_h * 60 + start_m)
    
    def save_schedule(self, output_path: str = 'schedules/') -> None:
        """保存日程"""
        output = Path(output_path)
        output.mkdir(parents=True, exist_ok=True)
        
        date_str = datetime.now().strftime('%Y%m%d')
        
        with open(output / f'schedule_{date_str}.json', 'w', encoding='utf-8') as f:
            json.dump({
                'date': date_str,
                'tasks': self.tasks,
                'time_blocks': self.DEFAULT_TIME_BLOCKS
            }, f, ensure_ascii=False, indent=2)
        
        print(f"日程已保存至: {output_path}")
    
    def get_mit(self) -> List[Dict]:
        """获取今日最重要的3件事"""
        sorted_tasks = sorted(
            [t for t in self.tasks if not t['scheduled']],
            key=lambda x: (x['priority'], x['deadline'] or '9999-12-31')
        )
        return sorted_tasks[:3]


def main():
    # 示例用法
    planner = SchedulePlanner()
    
    # 添加任务
    planner.add_task("完成项目报告", 120, priority=0, energy_required='high')
    planner.add_task("回复重要邮件", 30, priority=1, energy_required='medium')
    planner.add_task("整理会议纪要", 45, priority=2, energy_required='low')
    planner.add_task("学习新技术", 90, priority=1, energy_required='high')
    
    # 生成日程
    print("=== 今日日程 ===")
    print(planner.plan_daily())
    
    print("\n=== 本周计划 ===")
    print(planner.plan_weekly())
    
    print("\n=== 今日Top 3 (MIT) ===")
    for i, task in enumerate(planner.get_mit(), 1):
        print(f"{i}. {task['name']} ({task['duration_minutes']}分钟)")


if __name__ == '__main__':
    main()

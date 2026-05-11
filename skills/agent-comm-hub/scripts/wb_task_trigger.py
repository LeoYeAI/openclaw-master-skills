#!/usr/bin/env python3
"""
wb_task_trigger.py — WorkBuddy 任务触发器

监听 ~/.workbuddy/hub-tasks/ 目录中的触发文件。
当 hub_watcher 写入触发文件时，此脚本通过 FSEvents 检测到变化，
然后触发 WorkBuddy 自动化执行。

实际上我们不需要监听——因为 hub_watcher 已经通过信号文件通知了。
这里用一个简单的方案：通过 launchd 每60秒执行此脚本，
检查是否有未处理的触发文件。

如果 WorkBuddy 自动化已经在处理 Hub 任务了，这个脚本什么都不做。
如果自动化还没轮到，此脚本会尝试直接通知 WorkBuddy。

注意：这个脚本的真正作用是缩短延迟。
最终执行任务的仍然是 WorkBuddy Agent（通过自动化）。
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

TRIGGER_DIR = Path.home() / ".workbuddy" / "hub-tasks"
LOCK_FILE = TRIGGER_DIR / ".poll_lock"


def check_triggers():
    """检查是否有未处理的触发文件"""
    if not TRIGGER_DIR.exists():
        return 0
    
    triggers = list(TRIGGER_DIR.glob("task_*.json"))
    # 排除锁文件
    triggers = [f for f in triggers if not f.name.startswith(".")]
    
    return len(triggers)


def get_trigger_info():
    """获取第一个触发文件的信息"""
    if not TRIGGER_DIR.exists():
        return None
    
    triggers = sorted(TRIGGER_DIR.glob("task_*.json"), key=os.path.getmtime)
    if not triggers:
        return None
    
    try:
        with open(triggers[0], "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


if __name__ == "__main__":
    count = check_triggers()
    if count > 0:
        info = get_trigger_info()
        ts = datetime.now().strftime("%H:%M:%S")
        task_id = info.get("task_id", "?") if info else "?"
        desc = info.get("description", "?")[:40] if info else "?"
        print(f"[{ts}] 等待处理的 Hub 任务: {count} 个")
        print(f"  最新: {task_id} | {desc}")
        # 退出码 0 但有输出 → WorkBuddy 自动化系统会看到输出并触发
        sys.exit(0)
    else:
        sys.exit(0)

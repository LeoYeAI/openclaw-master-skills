#!/usr/bin/env python3
"""执行XGO预设动作"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

# 动作名称和等待时间映射
ACTION_INFO = {
    1: ("趴下", 2), 2: ("站起", 2), 3: ("匍匐前进", 5), 4: ("转圈", 5), 5: ("踏步", 4),
    6: ("蹲起", 4), 7: ("转动Roll", 4), 8: ("转动Pitch", 4), 9: ("转动Yaw", 4), 10: ("三轴转动", 7),
    11: ("撒尿", 7), 12: ("坐下", 5), 13: ("招手", 7), 14: ("伸懒腰", 10), 15: ("波浪", 6),
    16: ("摇摆", 6), 17: ("乞讨", 6), 18: ("找食物", 6), 19: ("握手", 10), 20: ("鸡头", 9),
    21: ("俯卧撑", 8), 22: ("张望", 8), 23: ("跳舞", 6), 255: ("重置", 1)
}

def main():
    parser = argparse.ArgumentParser(description='执行XGO预设动作')
    parser.add_argument('--id', type=int, required=True, help='动作ID (1-23, 255)')
    args = parser.parse_args()
    
    if args.id not in ACTION_INFO:
        print(f"错误: 动作ID {args.id} 无效")
        print("有效动作ID:")
        for aid, (name, _) in ACTION_INFO.items():
            print(f"  {aid}: {name}")
        return
    
    action_name, wait_time = ACTION_INFO[args.id]
    
    dog = XGO()
    print(f"执行XGO动作: {action_name} (ID={args.id})")
    
    dog.action(args.id)
    time.sleep(wait_time)
    
    print(f"✓ XGO动作 {action_name} 完成")

if __name__ == '__main__':
    main()

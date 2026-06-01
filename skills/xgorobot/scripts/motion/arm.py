#!/usr/bin/env python3
"""XGO机械臂快捷控制"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='XGO机械臂快捷控制')
    parser.add_argument('--action', type=str, required=True, choices=['open', 'close', 'up', 'down'], 
                        help='动作类型: open(张开), close(闭合), up(抬起), down(放下)')
    args = parser.parse_args()
    
    dog = XGO()
    action_map = {"open": "张开夹爪", "close": "闭合夹爪", "up": "抬起机械臂", "down": "放下机械臂"}
    print(f"XGO机械臂: {action_map[args.action]}")
    
    # 动作映射
    if args.action == "open":
        dog.claw(255)  # 完全张开
    elif args.action == "close":
        dog.claw(0)    # 完全闭合
    elif args.action == "up":
        dog.arm(80, 80)  # 抬起
    elif args.action == "down":
        dog.arm(80, 0)   # 放下
    
    time.sleep(1.5)
    print(f"✓ XGO机械臂{action_map[args.action]}完成")

if __name__ == '__main__':
    main()

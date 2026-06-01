#!/usr/bin/env python3
"""执行XGO-Rider预设动作"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

ACTION_NAMES = {
    1: "左右摇摆", 2: "高低起伏", 3: "前进后退",
    4: "四方蛇形", 5: "升降旋转", 6: "圆周晃动",
    255: "重置"
}

def main():
    parser = argparse.ArgumentParser(description='执行XGO-Rider预设动作')
    parser.add_argument('--id', type=int, required=True, help='动作ID: 1=左右摇摆, 2=高低起伏, 3=前进后退, 4=四方蛇形, 5=升降旋转, 6=圆周晃动, 255=重置')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_action(args.id, wait=True)
    action_name = ACTION_NAMES.get(args.id, f"动作{args.id}")
    print(f"Rider执行动作: {action_name}")

if __name__ == '__main__':
    main()

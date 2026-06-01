#!/usr/bin/env python3
"""调整XGO机身姿态角度"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='调整XGO机身姿态角度')
    parser.add_argument('--roll', type=float, default=None, help='横滚角 [-20, 20]，左右倾斜')
    parser.add_argument('--pitch', type=float, default=None, help='俯仰角 [-22, 22]，正值抬头，负值低头')
    parser.add_argument('--yaw', type=float, default=None, help='偏航角 [-16, 16]，左右转头')
    args = parser.parse_args()
    
    dog = XGO()
    
    # 收集非None的参数
    directions = []
    values = []
    if args.roll is not None:
        directions.append('r')
        values.append(args.roll)
    if args.pitch is not None:
        directions.append('p')
        values.append(args.pitch)
    if args.yaw is not None:
        directions.append('y')
        values.append(args.yaw)
    
    if not directions:
        print("请至少指定一个姿态参数 (--roll, --pitch, --yaw)")
        return
    
    print(f"XGO姿态调整: {dict(zip(directions, values))}")
    
    if len(directions) == 1:
        dog.attitude(directions[0], values[0])
    else:
        dog.attitude(directions, values)
    
    time.sleep(1.5)
    print(f"✓ XGO姿态调整完成")

if __name__ == '__main__':
    main()

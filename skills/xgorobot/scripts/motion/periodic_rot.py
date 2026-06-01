#!/usr/bin/env python3
"""控制XGO周期性往复旋转运动"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO周期性往复旋转运动')
    parser.add_argument('--axis', type=str, default='r', choices=['r', 'p', 'y'], help='旋转轴向: r(Roll), p(Pitch), y(Yaw)')
    parser.add_argument('--period', type=float, default=2, help='周期时间 [1.5, 8]秒')
    parser.add_argument('--duration', type=float, default=5, help='运动持续时间（秒），0表示持续运动')
    args = parser.parse_args()
    
    dog = XGO()
    direction_map = {"r": "Roll轴", "p": "Pitch轴", "y": "Yaw轴"}
    print(f"XGO{direction_map[args.axis]}周期性旋转: 周期={args.period}秒, 持续={args.duration}秒")
    
    dog.periodic_rot(args.axis, args.period)
    if args.duration > 0:
        time.sleep(args.duration)
        dog.reset()
    
    print(f"✓ XGO周期性旋转完成")

if __name__ == '__main__':
    main()

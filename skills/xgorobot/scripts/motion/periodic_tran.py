#!/usr/bin/env python3
"""控制XGO周期性往复平移运动"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO周期性往复平移运动')
    parser.add_argument('--axis', type=str, default='z', choices=['x', 'y', 'z'], help='平移轴向: x(前后), y(左右), z(上下)')
    parser.add_argument('--period', type=float, default=2, help='周期时间 [1.5, 8]秒')
    parser.add_argument('--duration', type=float, default=5, help='运动持续时间（秒），0表示持续运动')
    args = parser.parse_args()
    
    dog = XGO()
    direction_map = {"x": "前后", "y": "左右", "z": "上下"}
    print(f"XGO{direction_map[args.axis]}方向周期性平移: 周期={args.period}秒, 持续={args.duration}秒")
    
    dog.periodic_tran(args.axis, args.period)
    if args.duration > 0:
        time.sleep(args.duration)
        dog.reset()
    
    print(f"✓ XGO周期性平移完成")

if __name__ == '__main__':
    main()

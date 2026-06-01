#!/usr/bin/env python3
"""控制XGO原地旋转"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO原地旋转')
    parser.add_argument('--speed', type=float, default=50, help='旋转速度 [-100, 100]，正值向左，负值向右')
    parser.add_argument('--duration', type=float, default=1, help='旋转持续时间（秒）')
    args = parser.parse_args()
    
    dog = XGO()
    print(f"XGO旋转: 速度={args.speed}, 持续={args.duration}秒")
    
    dog.turn(args.speed)
    if args.duration > 0:
        time.sleep(args.duration)
        dog.turn(0)
    
    direction = "向左" if args.speed > 0 else "向右"
    print(f"✓ XGO{direction}旋转完成")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""控制XGO原地踏步"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO原地踏步')
    parser.add_argument('--height', type=float, default=20, help='抬腿高度 [10, 35]mm')
    parser.add_argument('--duration', type=float, default=3, help='踏步持续时间（秒）')
    args = parser.parse_args()
    
    dog = XGO()
    print(f"XGO原地踏步: 抬腿高度={args.height}mm, 持续={args.duration}秒")
    
    dog.mark_time(args.height)
    if args.duration > 0:
        time.sleep(args.duration)
        dog.reset()
    
    print(f"✓ XGO原地踏步完成")

if __name__ == '__main__':
    main()

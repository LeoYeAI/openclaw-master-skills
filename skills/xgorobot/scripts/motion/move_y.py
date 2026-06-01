#!/usr/bin/env python3
"""控制XGO在Y轴（左右）方向移动"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO在Y轴（左右）方向移动')
    parser.add_argument('--step', type=float, default=10, help='移动步幅 [-18, 18]，正值向左，负值向右')
    parser.add_argument('--duration', type=float, default=2, help='移动持续时间（秒）')
    args = parser.parse_args()
    
    dog = XGO()
    print(f"XGO Y轴移动: 步幅={args.step}, 持续={args.duration}秒")
    
    dog.move('y', args.step)
    if args.duration > 0:
        time.sleep(args.duration)
        dog.reset()
    
    direction = "向左" if args.step > 0 else "向右"
    print(f"✓ XGO{direction}移动完成")

if __name__ == '__main__':
    main()

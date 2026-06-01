#!/usr/bin/env python3
"""控制XGO在X轴（前后）方向移动"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO在X轴（前后）方向移动')
    parser.add_argument('--step', type=float, default=15, help='移动步幅 [-25, 25]，正值前进，负值后退')
    parser.add_argument('--duration', type=float, default=2, help='移动持续时间（秒）')
    args = parser.parse_args()
    
    dog = XGO()
    print(f"XGO X轴移动: 步幅={args.step}, 持续={args.duration}秒")
    
    dog.move('x', args.step)
    if args.duration > 0:
        time.sleep(args.duration)
        dog.reset()
    
    direction = "前进" if args.step > 0 else "后退"
    print(f"✓ XGO{direction}完成")

if __name__ == '__main__':
    main()

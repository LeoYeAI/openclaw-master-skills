#!/usr/bin/env python3
"""
右移 - 控制机器狗向右平移
用法: python right.py [--step STEP] [--duration DURATION]
参数:
  --step: 步幅 0-18，默认10
  --duration: 持续时间(秒)，默认2秒
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='机器狗右移')
    parser.add_argument('--step', type=int, default=10, help='步幅 0-18')
    parser.add_argument('--duration', type=float, default=2.0, help='持续时间(秒)')
    args = parser.parse_args()
    
    dog = XGO()
    
    step = max(0, min(18, args.step))
    print(f"右移: 步幅={step}, 持续={args.duration}秒")
    
    dog.right(step)
    
    if args.duration > 0:
        time.sleep(args.duration)
        dog.stop()
        print("右移完成")

if __name__ == '__main__':
    main()

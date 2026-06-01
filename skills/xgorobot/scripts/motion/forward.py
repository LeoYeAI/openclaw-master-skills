#!/usr/bin/env python3
"""
前进 - 控制机器狗向前行走
用法: python forward.py [--step STEP] [--duration DURATION]
参数:
  --step: 步幅 0-25，默认15
  --duration: 持续时间(秒)，默认2秒，0表示持续运动
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='机器狗前进')
    parser.add_argument('--step', type=int, default=15, help='步幅 0-25')
    parser.add_argument('--duration', type=float, default=2.0, help='持续时间(秒)')
    args = parser.parse_args()
    
    dog = XGO()
    
    step = max(0, min(25, args.step))
    print(f"前进: 步幅={step}, 持续={args.duration}秒")
    
    dog.forward(step)
    
    if args.duration > 0:
        time.sleep(args.duration)
        dog.stop()
        print("前进完成")

if __name__ == '__main__':
    main()

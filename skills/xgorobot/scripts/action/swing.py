#!/usr/bin/env python3
"""
摇摆 - 机器狗左右摇摆动作
用法: python swing.py [--duration DURATION]
参数:
  --duration: 持续时间(秒)，默认5秒
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='机器狗摇摆')
    parser.add_argument('--duration', type=float, default=5.0, help='持续时间(秒)')
    args = parser.parse_args()
    
    dog = XGO()
    
    print(f"开始摇摆 {args.duration}秒...")
    dog.periodic_rot(['r', 'p'], [3, 3])
    
    time.sleep(args.duration)
    
    dog.periodic_rot(['r', 'p'], [0, 0])
    print("摇摆完成")

if __name__ == '__main__':
    main()

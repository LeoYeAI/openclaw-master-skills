#!/usr/bin/env python3
"""
倾斜 - 控制机器狗身体姿态倾斜
用法: python tilt.py [--roll ROLL] [--pitch PITCH] [--yaw YAW]
参数:
  --roll: 横滚角 -20~20度，默认0
  --pitch: 俯仰角 -22~22度，默认0
  --yaw: 偏航角 -16~16度，默认0
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='机器狗姿态倾斜')
    parser.add_argument('--roll', type=int, default=0, help='横滚角 -20~20')
    parser.add_argument('--pitch', type=int, default=0, help='俯仰角 -22~22')
    parser.add_argument('--yaw', type=int, default=0, help='偏航角 -16~16')
    args = parser.parse_args()
    
    dog = XGO()
    
    roll = max(-20, min(20, args.roll))
    pitch = max(-22, min(22, args.pitch))
    yaw = max(-16, min(16, args.yaw))
    
    print(f"姿态: Roll={roll}, Pitch={pitch}, Yaw={yaw}")
    
    if args.roll != 0:
        dog.attitude('r', roll)
    if args.pitch != 0:
        dog.attitude('p', pitch)
    if args.yaw != 0:
        dog.attitude('y', yaw)

if __name__ == '__main__':
    main()

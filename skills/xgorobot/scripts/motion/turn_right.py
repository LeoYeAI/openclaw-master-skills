#!/usr/bin/env python3
"""
右转 - 控制机器狗向右转动
用法: python turn_right.py [--speed SPEED] [--duration DURATION]
参数:
  --speed: 转动速度 0-100，默认50
  --duration: 持续时间(秒)，默认1秒
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='机器狗右转')
    parser.add_argument('--speed', type=int, default=50, help='转动速度 0-100')
    parser.add_argument('--duration', type=float, default=1.0, help='持续时间(秒)')
    args = parser.parse_args()
    
    dog = XGO()
    
    speed = max(0, min(100, args.speed))
    print(f"右转: 速度={speed}, 持续={args.duration}秒")
    
    dog.turnright(speed)
    
    if args.duration > 0:
        time.sleep(args.duration)
        dog.stop()
        print("右转完成")

if __name__ == '__main__':
    main()

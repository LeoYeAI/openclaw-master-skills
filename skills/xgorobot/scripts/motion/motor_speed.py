#!/usr/bin/env python3
"""设置XGO舵机转动速度"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='设置XGO舵机转动速度')
    parser.add_argument('--speed', type=int, default=128, help='速度值 [1, 255]，值越大速度越快')
    args = parser.parse_args()
    
    if args.speed < 1 or args.speed > 255:
        print("错误: 速度值范围为1-255")
        return
    
    dog = XGO()
    print(f"设置XGO舵机速度: {args.speed}")
    
    dog.motor_speed(args.speed)
    time.sleep(0.2)
    
    print(f"✓ XGO舵机速度设置完成")

if __name__ == '__main__':
    main()

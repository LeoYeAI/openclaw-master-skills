#!/usr/bin/env python3
"""控制XGO-Rider原地旋转"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO-Rider原地旋转')
    parser.add_argument('--speed', type=float, required=True, help='旋转角速度[-360, 360]°/s，正=左转，负=右转')
    parser.add_argument('--runtime', type=float, default=0, help='持续时间(秒)，0=持续旋转')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_turn(args.speed, int(args.runtime))
    direction = "左转" if args.speed > 0 else "右转"
    print(f"Rider{direction}，角速度: {args.speed}°/s")

if __name__ == '__main__':
    main()

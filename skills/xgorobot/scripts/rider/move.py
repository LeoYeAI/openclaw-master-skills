#!/usr/bin/env python3
"""控制XGO-Rider前后移动"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO-Rider前后移动')
    parser.add_argument('--speed', type=float, required=True, help='移动速度[-1.5, 1.5] m/s，正=前进，负=后退')
    parser.add_argument('--runtime', type=float, default=0, help='持续时间(秒)，0=持续移动')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_move_x(args.speed, int(args.runtime))
    direction = "前进" if args.speed > 0 else "后退"
    print(f"Rider{direction}移动，速度: {args.speed}m/s")

if __name__ == '__main__':
    main()

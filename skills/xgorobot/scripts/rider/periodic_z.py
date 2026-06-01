#!/usr/bin/env python3
"""XGO-Rider周期性Z轴升降"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='XGO-Rider周期性Z轴升降')
    parser.add_argument('--period', type=float, required=True, help='周期时间[1, 2]秒')
    parser.add_argument('--duration', type=float, default=0, help='持续时间(秒)，0=持续运动')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_periodic_z(args.period)
    
    if args.duration > 0:
        time.sleep(args.duration)
        dog.rider_periodic_z(0)
        print(f"Rider周期性升降完成，周期: {args.period}秒，持续: {args.duration}秒")
    else:
        print(f"Rider开始周期性升降，周期: {args.period}秒")

if __name__ == '__main__':
    main()

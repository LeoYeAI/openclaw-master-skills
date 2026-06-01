#!/usr/bin/env python3
"""控制XGO-Mini3W四个轮子"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO-Mini3W四个轮子')
    parser.add_argument('--w1', type=int, default=128, help='轮子1速度[0-255]，128为停止')
    parser.add_argument('--w2', type=int, default=128, help='轮子2速度[0-255]，128为停止')
    parser.add_argument('--w3', type=int, default=128, help='轮子3速度[0-255]，128为停止')
    parser.add_argument('--w4', type=int, default=128, help='轮子4速度[0-255]，128为停止')
    args = parser.parse_args()
    
    dog = XGO()
    data = [args.w1, args.w2, args.w3, args.w4]
    dog.wheel_control(data)
    time.sleep(0.3)
    print(f"轮控制已执行: {data}")

if __name__ == '__main__':
    main()

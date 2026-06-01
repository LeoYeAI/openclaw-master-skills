#!/usr/bin/env python3
"""开启/关闭XGO IMU自稳功能"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='开启/关闭XGO IMU自稳功能')
    parser.add_argument('--mode', type=int, default=1, choices=[0, 1], help='IMU模式: 0(关闭), 1(开启)')
    args = parser.parse_args()
    
    dog = XGO()
    status = "开启" if args.mode == 1 else "关闭"
    print(f"XGO IMU自稳: {status}")
    
    dog.imu(args.mode)
    time.sleep(0.3)
    
    print(f"✓ XGO IMU自稳已{status}")

if __name__ == '__main__':
    main()

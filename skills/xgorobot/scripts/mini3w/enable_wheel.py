#!/usr/bin/env python3
"""启用/禁用XGO-Mini3W轮控模式"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='启用/禁用XGO-Mini3W轮控模式')
    parser.add_argument('--mode', type=int, required=True, choices=[0, 1], help='0=启用轮控，1=禁用轮控')
    args = parser.parse_args()
    
    dog = XGO()
    dog.enable_wheel_control(args.mode)
    time.sleep(0.3)
    status = "启用" if args.mode == 0 else "禁用"
    print(f"轮控模式已{status}")

if __name__ == '__main__':
    main()

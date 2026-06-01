#!/usr/bin/env python3
"""控制XGO-Mini3W外接电机位置"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO-Mini3W外接电机位置')
    parser.add_argument('--position', type=int, required=True, help='电机位置，范围[-32768, 32767]')
    args = parser.parse_args()
    
    dog = XGO()
    dog.extern_motor(args.position)
    time.sleep(0.5)
    print(f"外接电机位置设置为: {args.position}")

if __name__ == '__main__':
    main()

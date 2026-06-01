#!/usr/bin/env python3
"""
蹲下 - 降低机器狗身高
用法: python squat.py [--height HEIGHT]
参数:
  --height: 身高 75-120mm，默认80mm
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='机器狗蹲下')
    parser.add_argument('--height', type=int, default=80, help='身高 75-120mm')
    args = parser.parse_args()
    
    dog = XGO()
    
    height = max(75, min(120, args.height))
    print(f"蹲下: 身高={height}mm")
    
    dog.translation('z', height)

if __name__ == '__main__':
    main()

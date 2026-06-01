#!/usr/bin/env python3
"""
站高 - 提高机器狗身高
用法: python stand.py [--height HEIGHT]
参数:
  --height: 身高 75-120mm，默认115mm
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='机器狗站高')
    parser.add_argument('--height', type=int, default=115, help='身高 75-120mm')
    args = parser.parse_args()
    
    dog = XGO()
    
    height = max(75, min(120, args.height))
    print(f"站高: 身高={height}mm")
    
    dog.translation('z', height)

if __name__ == '__main__':
    main()

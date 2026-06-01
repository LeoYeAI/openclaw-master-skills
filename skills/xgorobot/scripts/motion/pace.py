#!/usr/bin/env python3
"""设置XGO步伐频率"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='设置XGO步伐频率')
    parser.add_argument('--mode', type=str, default='normal', choices=['normal', 'slow', 'high'], 
                        help='频率模式: normal(正常), slow(慢速), high(高速)')
    args = parser.parse_args()
    
    dog = XGO()
    mode_map = {"normal": "正常频率", "slow": "慢速频率", "high": "高速频率"}
    print(f"设置XGO步伐频率: {mode_map[args.mode]}")
    
    dog.pace(args.mode)
    time.sleep(0.5)
    
    print(f"✓ XGO步伐频率设置完成")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""设置XGO步态类型"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='设置XGO步态类型')
    parser.add_argument('--mode', type=str, default='trot', choices=['trot', 'walk', 'high_walk', 'slow_trot'], 
                        help='步态模式: trot(小跑), walk(行走), high_walk(高抬腿), slow_trot(慢跑)')
    args = parser.parse_args()
    
    dog = XGO()
    mode_map = {"trot": "小跑步态", "walk": "行走步态", "high_walk": "高抬腿行走", "slow_trot": "慢速小跑"}
    print(f"设置XGO步态: {mode_map[args.mode]}")
    
    dog.gait_type(args.mode)
    time.sleep(0.5)
    
    print(f"✓ XGO步态设置完成")

if __name__ == '__main__':
    main()

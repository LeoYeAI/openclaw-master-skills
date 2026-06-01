#!/usr/bin/env python3
"""控制XGO单个舵机角度"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO单个舵机角度')
    parser.add_argument('--id', type=int, required=True, help='舵机编号: 11-13(左前), 21-23(右前), 31-33(右后), 41-43(左后), 51(机械臂)')
    parser.add_argument('--angle', type=float, required=True, help='舵机角度')
    args = parser.parse_args()
    
    valid_ids = [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43, 51]
    if args.id not in valid_ids:
        print(f"错误: 舵机编号{args.id}无效, 有效范围: {valid_ids}")
        return
    
    dog = XGO()
    print(f"控制XGO舵机{args.id}: 角度={args.angle}°")
    
    dog.motor(args.id, args.angle)
    time.sleep(0.5)
    
    print(f"✓ XGO舵机{args.id}角度设置完成")

if __name__ == '__main__':
    main()

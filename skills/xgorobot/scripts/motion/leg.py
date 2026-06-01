#!/usr/bin/env python3
"""控制XGO单条腿的位置"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO单条腿的位置')
    parser.add_argument('--id', type=int, required=True, choices=[1, 2, 3, 4], help='腿编号: 1(左前), 2(右前), 3(右后), 4(左后)')
    parser.add_argument('--x', type=float, default=0, help='X轴位置 [-35, 35]mm')
    parser.add_argument('--y', type=float, default=0, help='Y轴位置 [-18, 18]mm')
    parser.add_argument('--z', type=float, default=95, help='Z轴位置 [75, 120]mm')
    args = parser.parse_args()
    
    dog = XGO()
    leg_names = {1: "左前腿", 2: "右前腿", 3: "右后腿", 4: "左后腿"}
    print(f"控制XGO{leg_names[args.id]}: X={args.x}, Y={args.y}, Z={args.z}mm")
    
    dog.leg(args.id, [args.x, args.y, args.z])
    time.sleep(0.5)
    
    print(f"✓ XGO{leg_names[args.id]}位置设置完成")

if __name__ == '__main__':
    main()

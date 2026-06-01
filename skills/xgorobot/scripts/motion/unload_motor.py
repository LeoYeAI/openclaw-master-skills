#!/usr/bin/env python3
"""卸载XGO指定腿的舵机（舵机失去力矩，可手动调整）"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='卸载XGO指定腿的舵机')
    parser.add_argument('--leg', type=int, required=True, choices=[1, 2, 3, 4, 5], 
                        help='腿编号: 1(左前), 2(右前), 3(右后), 4(左后), 5(机械臂)')
    args = parser.parse_args()
    
    dog = XGO()
    leg_names = {1: "左前腿", 2: "右前腿", 3: "右后腿", 4: "左后腿", 5: "机械臂"}
    print(f"卸载XGO{leg_names[args.leg]}舵机...")
    
    dog.unload_motor(args.leg)
    time.sleep(0.3)
    
    print(f"✓ XGO{leg_names[args.leg]}舵机已卸载")

if __name__ == '__main__':
    main()

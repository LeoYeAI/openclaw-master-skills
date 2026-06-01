#!/usr/bin/env python3
"""读取XGO所有舵机角度"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO所有舵机的当前角度')
    args = parser.parse_args()
    
    dog = XGO()
    angles = dog.read_motor()
    
    if angles and len(angles) >= 12:
        print("XGO舵机角度:")
        print(f"  左前腿: [{angles[0]:.1f}°, {angles[1]:.1f}°, {angles[2]:.1f}°]")
        print(f"  右前腿: [{angles[3]:.1f}°, {angles[4]:.1f}°, {angles[5]:.1f}°]")
        print(f"  右后腿: [{angles[6]:.1f}°, {angles[7]:.1f}°, {angles[8]:.1f}°]")
        print(f"  左后腿: [{angles[9]:.1f}°, {angles[10]:.1f}°, {angles[11]:.1f}°]")
        if len(angles) >= 13:
            print(f"  机械臂: {angles[12]:.1f}°")
    else:
        print("读取舵机角度失败")

if __name__ == '__main__':
    main()

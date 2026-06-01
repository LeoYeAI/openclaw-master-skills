#!/usr/bin/env python3
"""控制XGO机身位置平移（足端位置不变）"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO机身位置平移')
    parser.add_argument('--axis', type=str, default='z', choices=['x', 'y', 'z'], help='平移轴向: x(前后), y(左右), z(上下/身高)')
    parser.add_argument('--distance', type=float, default=95, help='平移距离(mm), x:[-35,35], y:[-18,18], z:[75,120]')
    args = parser.parse_args()
    
    dog = XGO()
    direction_map = {"x": "前后", "y": "左右", "z": "上下"}
    print(f"XGO机身{direction_map[args.axis]}平移: {args.distance}mm")
    
    dog.translation(args.axis, args.distance)
    time.sleep(1)
    
    print(f"✓ XGO机身平移完成")

if __name__ == '__main__':
    main()

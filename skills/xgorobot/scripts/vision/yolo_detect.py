#!/usr/bin/env python3
"""
目标检测 - YOLO物体检测
用法: python yolo_detect.py [--continuous]
参数:
  --continuous: 持续检测模式，按C键退出
输出: ('物体类别', (x, y)) 或 None
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='YOLO目标检测')
    parser.add_argument('--continuous', action='store_true', help='持续检测模式')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    if args.continuous:
        print("持续目标检测模式... 按C键退出")
        while not edu.xgoButton("c"):
            result = edu.yoloFast()
            if result:
                obj_class, pos = result
                print(f"检测到: {obj_class} 位置=({pos[0]}, {pos[1]})")
            time.sleep(0.2)
        print("检测结束")
    else:
        result = edu.yoloFast()
        if result:
            obj_class, pos = result
            print(f"检测到: {obj_class} 位置=({pos[0]}, {pos[1]})")
        else:
            print("未检测到目标")

if __name__ == '__main__':
    main()

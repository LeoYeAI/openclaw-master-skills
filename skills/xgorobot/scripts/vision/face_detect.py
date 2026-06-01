#!/usr/bin/env python3
"""
人脸检测 - 检测画面中的人脸
用法: python face_detect.py [--continuous]
参数:
  --continuous: 持续检测模式，按C键退出
输出: 人脸位置 [x, y, w, h] 或 None
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='人脸检测')
    parser.add_argument('--continuous', action='store_true', help='持续检测模式')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    if args.continuous:
        print("持续人脸检测模式... 按C键退出")
        while not edu.xgoButton("c"):
            result = edu.face_detect()
            if result:
                print(f"检测到人脸: x={result[0]}, y={result[1]}, w={result[2]}, h={result[3]}")
            time.sleep(0.2)
        print("检测结束")
    else:
        result = edu.face_detect()
        if result:
            print(f"检测到人脸: x={result[0]}, y={result[1]}, w={result[2]}, h={result[3]}")
        else:
            print("未检测到人脸")

if __name__ == '__main__':
    main()

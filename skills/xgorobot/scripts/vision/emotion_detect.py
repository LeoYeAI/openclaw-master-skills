#!/usr/bin/env python3
"""
情绪识别 - 识别人脸表情情绪
用法: python emotion_detect.py [--continuous]
参数:
  --continuous: 持续识别模式，按C键退出
输出: ('情绪', (x, y)) 或 None
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='情绪识别')
    parser.add_argument('--continuous', action='store_true', help='持续识别模式')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    if args.continuous:
        print("持续情绪识别模式... 按C键退出")
        while not edu.xgoButton("c"):
            result = edu.emotion()
            if result:
                print(f"检测到情绪: {result[0]} 位置=({result[1][0]}, {result[1][1]})")
            time.sleep(0.3)
        print("识别结束")
    else:
        result = edu.emotion()
        if result:
            print(f"检测到情绪: {result[0]} 位置=({result[1][0]}, {result[1][1]})")
        else:
            print("未检测到人脸")

if __name__ == '__main__':
    main()

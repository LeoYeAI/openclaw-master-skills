#!/usr/bin/env python3
"""
手势识别 - 识别手势动作
用法: python gesture_detect.py [--continuous]
参数:
  --continuous: 持续识别模式，按C键退出
输出: ('手势', (x, y)) 或 None
手势类型: '1'-'5'(数字), 'Good'(点赞), 'Stone'(拳头), 'Rock'(摇滚), 'Ok'
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='手势识别')
    parser.add_argument('--continuous', action='store_true', help='持续识别模式')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    if args.continuous:
        print("持续手势识别模式... 按C键退出")
        while not edu.xgoButton("c"):
            result = edu.gestureRecognition()
            if result:
                gesture, pos = result
                print(f"检测到手势: {gesture} 位置=({pos[0]}, {pos[1]})")
            time.sleep(0.2)
        print("识别结束")
    else:
        result = edu.gestureRecognition()
        if result:
            gesture, pos = result
            print(f"检测到手势: {gesture} 位置=({pos[0]}, {pos[1]})")
        else:
            print("未检测到手势")

if __name__ == '__main__':
    main()

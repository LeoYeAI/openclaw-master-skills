#!/usr/bin/env python3
"""
颜色识别 - 识别指定颜色物体
用法: python color_detect.py [--color COLOR] [--continuous]
参数:
  --color: 颜色模式 R(红)/G(绿)/B(蓝)/Y(黄)，默认R
  --continuous: 持续识别模式，按C键退出
输出: ((x, y), radius) 坐标和半径
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='颜色识别')
    parser.add_argument('--color', type=str, default='R', choices=['R', 'G', 'B', 'Y'], 
                        help='颜色: R(红)/G(绿)/B(蓝)/Y(黄)')
    parser.add_argument('--continuous', action='store_true', help='持续识别模式')
    args = parser.parse_args()
    
    edu = XGOEDU()
    color_names = {'R': '红色', 'G': '绿色', 'B': '蓝色', 'Y': '黄色'}
    
    if args.continuous:
        print(f"持续识别{color_names[args.color]}... 按C键退出")
        while not edu.xgoButton("c"):
            (x, y), radius = edu.ColorRecognition(mode=args.color)
            if radius > 10:
                print(f"检测到{color_names[args.color]}: 位置=({int(x)}, {int(y)}), 半径={int(radius)}")
            time.sleep(0.1)
        print("识别结束")
    else:
        (x, y), radius = edu.ColorRecognition(mode=args.color)
        if radius > 10:
            print(f"检测到{color_names[args.color]}: 位置=({int(x)}, {int(y)}), 半径={int(radius)}")
        else:
            print(f"未检测到{color_names[args.color]}物体")

if __name__ == '__main__':
    main()

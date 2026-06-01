#!/usr/bin/env python3
"""
巡线检测 - 检测地面线条
用法: python line_detect.py [--color COLOR] [--continuous]
参数:
  --color: 线条颜色 K(黑)/W(白)/R(红)/G(绿)/B(蓝)/Y(黄)，默认K
  --continuous: 持续检测模式，按C键退出
输出: {'x': 线的x坐标, 'angle': 线的角度}
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='巡线检测')
    parser.add_argument('--color', type=str, default='K', 
                        choices=['K', 'W', 'R', 'G', 'B', 'Y'],
                        help='线条颜色: K(黑)/W(白)/R(红)/G(绿)/B(蓝)/Y(黄)')
    parser.add_argument('--continuous', action='store_true', help='持续检测模式')
    args = parser.parse_args()
    
    edu = XGOEDU()
    color_names = {'K': '黑色', 'W': '白色', 'R': '红色', 'G': '绿色', 'B': '蓝色', 'Y': '黄色'}
    
    if args.continuous:
        print(f"持续检测{color_names[args.color]}线... 按C键退出")
        while not edu.xgoButton("c"):
            result = edu.LineRecognition(mode=args.color)
            if result['x'] > 0:
                offset = result['x'] - 160
                print(f"检测到线: x={result['x']}, 偏移={offset}, 角度={result['angle']}")
            time.sleep(0.05)
        print("检测结束")
    else:
        result = edu.LineRecognition(mode=args.color)
        if result['x'] > 0:
            offset = result['x'] - 160
            print(f"检测到线: x={result['x']}, 偏移={offset}, 角度={result['angle']}")
        else:
            print(f"未检测到{color_names[args.color]}线")

if __name__ == '__main__':
    main()

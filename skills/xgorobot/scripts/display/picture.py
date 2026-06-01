#!/usr/bin/env python3
"""XGO屏幕显示本地图片"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='XGO屏幕显示本地图片')
    parser.add_argument('--filename', type=str, required=True, help='图片文件名(jpg格式，位于/home/pi/xgoPictures/)')
    parser.add_argument('--x', type=int, default=0, help='显示位置X坐标，默认0')
    parser.add_argument('--y', type=int, default=0, help='显示位置Y坐标，默认0')
    args = parser.parse_args()
    
    edu = XGOEDU()
    edu.lcd_picture(args.filename, args.x, args.y)
    print(f"已显示图片: {args.filename}")

if __name__ == '__main__':
    main()

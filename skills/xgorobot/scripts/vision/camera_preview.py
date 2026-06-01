#!/usr/bin/env python3
"""
摄像头预览 - 开启摄像头实时预览
用法: python camera_preview.py [--duration DURATION]
参数:
  --duration: 预览时长(秒)，默认10秒，0表示按C键退出
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='摄像头预览')
    parser.add_argument('--duration', type=float, default=10.0, help='预览时长(秒)')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    print("开启摄像头预览... 按C键退出")
    edu.xgoCamera(True)
    
    if args.duration > 0:
        time.sleep(args.duration)
        edu.xgoCamera(False)
        print("预览结束")
    else:
        while not edu.xgoButton("c"):
            time.sleep(0.1)
        edu.xgoCamera(False)
        print("预览结束")

if __name__ == '__main__':
    main()

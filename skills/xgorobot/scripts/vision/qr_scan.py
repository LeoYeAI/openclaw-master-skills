#!/usr/bin/env python3
"""
二维码扫描 - 扫描并识别二维码
用法: python qr_scan.py [--continuous]
参数:
  --continuous: 持续扫描模式，按C键退出
输出: 二维码内容列表
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='二维码扫描')
    parser.add_argument('--continuous', action='store_true', help='持续扫描模式')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    if args.continuous:
        print("持续二维码扫描模式... 按C键退出")
        while not edu.xgoButton("c"):
            result = edu.QRRecognition()
            if result:
                for qr in result:
                    print(f"检测到二维码: {qr}")
            time.sleep(0.2)
        print("扫描结束")
    else:
        result = edu.QRRecognition()
        if result:
            for qr in result:
                print(f"检测到二维码: {qr}")
        else:
            print("未检测到二维码")

if __name__ == '__main__':
    main()

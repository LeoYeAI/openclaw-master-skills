#!/usr/bin/env python3
"""控制XGO-Rider LED灯颜色"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='控制XGO-Rider LED灯颜色')
    parser.add_argument('--index', type=int, required=True, help='LED编号(0-5)')
    parser.add_argument('--r', type=int, required=True, help='红色分量(0-255)')
    parser.add_argument('--g', type=int, required=True, help='绿色分量(0-255)')
    parser.add_argument('--b', type=int, required=True, help='蓝色分量(0-255)')
    args = parser.parse_args()
    
    if not (0 <= args.index <= 5):
        print("LED编号错误，范围为0-5")
        return
    
    if not all(0 <= val <= 255 for val in [args.r, args.g, args.b]):
        print("RGB值错误，范围为0-255")
        return
    
    dog = XGO()
    dog.rider_led(args.index, [args.r, args.g, args.b])
    time.sleep(0.2)
    print(f"Rider LED{args.index}颜色设置为RGB({args.r},{args.g},{args.b})")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""XGO-Rider软件标定"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='XGO-Rider软件标定（请谨慎使用）')
    parser.add_argument('--state', type=str, required=True, choices=['start', 'end'], help='start=开始标定，end=结束标定')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_calibration(args.state)
    time.sleep(0.5)
    status = "开始" if args.state == 'start' else "结束"
    print(f"Rider标定已{status}")

if __name__ == '__main__':
    main()

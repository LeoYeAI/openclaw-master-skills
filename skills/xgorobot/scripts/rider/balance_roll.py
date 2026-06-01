#!/usr/bin/env python3
"""开启/关闭XGO-Rider Roll轴自平衡"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='开启/关闭XGO-Rider Roll轴自平衡')
    parser.add_argument('--mode', type=int, required=True, choices=[0, 1], help='0=关闭，1=开启')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_balance_roll(args.mode)
    time.sleep(0.3)
    status = "开启" if args.mode == 1 else "关闭"
    print(f"Rider Roll轴自平衡已{status}")

if __name__ == '__main__':
    main()

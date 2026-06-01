#!/usr/bin/env python3
"""调整XGO-Rider横滚角(Roll)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='调整XGO-Rider横滚角(Roll)')
    parser.add_argument('--angle', type=float, required=True, help='Roll角度[-17, 17]度')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_roll(args.angle)
    time.sleep(1.5)
    print(f"Rider Roll调整至: {args.angle}°")

if __name__ == '__main__':
    main()

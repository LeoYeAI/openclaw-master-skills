#!/usr/bin/env python3
"""读取XGO-Rider偏航角(Yaw)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO-Rider偏航角(Yaw)')
    args = parser.parse_args()
    
    dog = XGO()
    yaw = dog.rider_read_yaw()
    print(f"Rider Yaw角度: {yaw}°")

if __name__ == '__main__':
    main()

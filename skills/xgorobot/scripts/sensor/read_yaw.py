#!/usr/bin/env python3
"""读取XGO偏航角(Yaw)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO偏航角(Yaw)，通过IMU传感器获取机身旋转方向角度')
    args = parser.parse_args()
    
    dog = XGO()
    yaw = dog.read_yaw()
    print(f"Yaw角度: {yaw}°")

if __name__ == '__main__':
    main()

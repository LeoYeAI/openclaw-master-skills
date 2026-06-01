#!/usr/bin/env python3
"""读取XGO横滚角(Roll)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO横滚角(Roll)，通过IMU传感器获取机身左右倾斜角度')
    args = parser.parse_args()
    
    dog = XGO()
    roll = dog.read_roll()
    print(f"Roll角度: {roll}°")

if __name__ == '__main__':
    main()

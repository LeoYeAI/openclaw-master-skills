#!/usr/bin/env python3
"""读取XGO俯仰角(Pitch)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO俯仰角(Pitch)，通过IMU传感器获取机身前后倾斜角度')
    args = parser.parse_args()
    
    dog = XGO()
    pitch = dog.read_pitch()
    print(f"Pitch角度: {pitch}°")

if __name__ == '__main__':
    main()

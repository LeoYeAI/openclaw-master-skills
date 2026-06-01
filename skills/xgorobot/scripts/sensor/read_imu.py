#!/usr/bin/env python3
"""读取XGO IMU数据"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO IMU数据')
    parser.add_argument('--axis', type=str, default='all', choices=['roll', 'pitch', 'yaw', 'all'], help='要读取的轴向')
    args = parser.parse_args()
    
    dog = XGO()
    
    if args.axis == 'all':
        roll = dog.read_roll()
        pitch = dog.read_pitch()
        yaw = dog.read_yaw()
        print(f"XGO IMU数据:")
        print(f"  Roll(横滚): {roll}°")
        print(f"  Pitch(俯仰): {pitch}°")
        print(f"  Yaw(偏航): {yaw}°")
    elif args.axis == 'roll':
        roll = dog.read_roll()
        print(f"XGO Roll(横滚): {roll}°")
    elif args.axis == 'pitch':
        pitch = dog.read_pitch()
        print(f"XGO Pitch(俯仰): {pitch}°")
    elif args.axis == 'yaw':
        yaw = dog.read_yaw()
        print(f"XGO Yaw(偏航): {yaw}°")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""读取XGO-Rider横滚角(Roll)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO-Rider横滚角(Roll)')
    args = parser.parse_args()
    
    dog = XGO()
    roll = dog.rider_read_roll()
    print(f"Rider Roll角度: {roll}°")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""读取XGO-Rider俯仰角(Pitch)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO-Rider俯仰角(Pitch)')
    args = parser.parse_args()
    
    dog = XGO()
    pitch = dog.rider_read_pitch()
    print(f"Rider Pitch角度: {pitch}°")

if __name__ == '__main__':
    main()

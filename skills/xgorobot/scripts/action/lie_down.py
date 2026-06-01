#!/usr/bin/env python3
"""
趴下 - 机器狗趴下动作
用法: python lie_down.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行趴下动作...")
    dog.action(2, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

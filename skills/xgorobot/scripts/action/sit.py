#!/usr/bin/env python3
"""
坐下 - 机器狗坐下动作
用法: python sit.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行坐下动作...")
    dog.action(1, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

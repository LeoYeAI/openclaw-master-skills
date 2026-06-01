#!/usr/bin/env python3
"""
伸懒腰 - 机器狗伸懒腰动作
用法: python stretch.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行伸懒腰...")
    dog.action(13, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
坐下抬手 - 机器狗坐下并抬手动作
用法: python wave.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行坐下抬手...")
    dog.action(12, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
俯卧撑 - 机器狗俯卧撑动作
用法: python pushup.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行俯卧撑...")
    dog.action(21, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

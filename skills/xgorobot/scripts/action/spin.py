#!/usr/bin/env python3
"""
转圈 - 机器狗原地转圈动作
用法: python spin.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行转圈动作...")
    dog.action(4, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

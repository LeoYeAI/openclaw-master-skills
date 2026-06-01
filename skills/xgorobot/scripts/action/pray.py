#!/usr/bin/env python3
"""
祈祷 - 机器狗祈祷动作
用法: python pray.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行祈祷动作...")
    dog.action(19, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

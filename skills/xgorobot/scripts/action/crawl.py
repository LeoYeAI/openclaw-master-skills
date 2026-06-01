#!/usr/bin/env python3
"""
匍匐前进 - 机器狗匍匐前进动作
用法: python crawl.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行匍匐前进...")
    dog.action(3, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

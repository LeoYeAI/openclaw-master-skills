#!/usr/bin/env python3
"""
撒尿 - 机器狗撒尿动作(抬腿)
用法: python pee.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("执行撒尿动作...")
    dog.action(11, wait=True)
    print("动作完成")

if __name__ == '__main__':
    main()

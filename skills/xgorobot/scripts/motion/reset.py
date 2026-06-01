#!/usr/bin/env python3
"""重置XGO到初始标准状态"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import time
from xgolib import XGO

def main():
    dog = XGO()
    print("重置XGO到初始状态...")
    dog.reset()
    time.sleep(2)
    print("✓ XGO已重置")

if __name__ == '__main__':
    main()

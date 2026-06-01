#!/usr/bin/env python3
"""停止XGO当前运动"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO

def main():
    dog = XGO()
    print("停止XGO运动...")
    dog.stop()
    print("✓ XGO已停止")

if __name__ == '__main__':
    main()

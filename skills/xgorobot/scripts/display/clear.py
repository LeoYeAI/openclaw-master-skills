#!/usr/bin/env python3
"""清除XGO屏幕显示"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='清除XGO屏幕显示')
    args = parser.parse_args()
    
    edu = XGOEDU()
    edu.lcd_clear()
    print("屏幕已清除")

if __name__ == '__main__':
    main()

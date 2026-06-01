#!/usr/bin/env python3
"""XGO屏幕显示文字"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='XGO屏幕显示文字')
    parser.add_argument('--text', type=str, required=True, help='要显示的文字内容')
    parser.add_argument('--x', type=int, default=5, help='X坐标，默认5')
    parser.add_argument('--y', type=int, default=5, help='Y坐标，默认5')
    parser.add_argument('--color', type=str, default='WHITE', help='颜色，默认WHITE')
    parser.add_argument('--size', type=int, default=15, help='字体大小，默认15')
    args = parser.parse_args()
    
    edu = XGOEDU()
    edu.lcd_text(args.x, args.y, args.text, args.color, args.size)
    print(f"已显示文字: {args.text}")

if __name__ == '__main__':
    main()

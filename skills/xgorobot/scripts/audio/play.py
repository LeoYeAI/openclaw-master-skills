#!/usr/bin/env python3
"""XGO播放本地音频文件"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse

def main():
    parser = argparse.ArgumentParser(description='XGO播放本地音频文件')
    parser.add_argument('--filename', type=str, required=True, help='音频文件名(位于/home/pi/Music/)')
    args = parser.parse_args()
    
    os.system(f"mplayer /home/pi/Music/{args.filename}")
    print(f"已播放音频: {args.filename}")

if __name__ == '__main__':
    main()

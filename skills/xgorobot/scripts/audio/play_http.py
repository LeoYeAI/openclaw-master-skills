#!/usr/bin/env python3
"""XGO播放HTTP音频"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='XGO播放HTTP音频')
    parser.add_argument('--url', type=str, required=True, help='音频HTTP URL')
    args = parser.parse_args()
    
    cmd = f'mplayer "{args.url}"'
    subprocess.run(cmd, shell=True, check=True)
    print(f"已播放HTTP音频: {args.url}")

if __name__ == '__main__':
    main()

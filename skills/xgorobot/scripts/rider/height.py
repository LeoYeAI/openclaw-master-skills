#!/usr/bin/env python3
"""调整XGO-Rider身高"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='调整XGO-Rider身高')
    parser.add_argument('--height', type=float, required=True, help='身高[60, 120]mm')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_height(args.height)
    time.sleep(1)
    print(f"Rider身高调整至: {args.height}mm")

if __name__ == '__main__':
    main()

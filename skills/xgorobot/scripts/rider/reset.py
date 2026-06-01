#!/usr/bin/env python3
"""重置XGO-Rider到初始状态"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='重置XGO-Rider到初始状态')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_reset()
    time.sleep(1)
    print("Rider已重置")

if __name__ == '__main__':
    main()

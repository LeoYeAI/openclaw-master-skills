#!/usr/bin/env python3
"""重置XGO-Rider里程计"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='重置XGO-Rider里程计')
    args = parser.parse_args()
    
    dog = XGO()
    dog.rider_reset_odom()
    time.sleep(0.5)
    print("Rider里程计已重置")

if __name__ == '__main__':
    main()

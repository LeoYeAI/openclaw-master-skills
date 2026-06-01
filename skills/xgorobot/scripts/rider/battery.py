#!/usr/bin/env python3
"""读取XGO-Rider电池电量"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
from xgolib import XGO

def main():
    parser = argparse.ArgumentParser(description='读取XGO-Rider电池电量')
    args = parser.parse_args()
    
    dog = XGO()
    battery = dog.rider_read_battery()
    
    if battery >= 80:
        status = "电量充足"
    elif battery >= 50:
        status = "电量正常"
    elif battery >= 20:
        status = "电量偏低"
    else:
        status = "电量严重不足，请及时充电"
    
    print(f"Rider电池电量: {battery}% - {status}")

if __name__ == '__main__':
    main()

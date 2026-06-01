#!/usr/bin/env python3
"""
拍照 - 使用摄像头拍照并保存
用法: python take_photo.py [--filename FILENAME]
参数:
  --filename: 保存的文件名，默认photo.jpg
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='拍照')
    parser.add_argument('--filename', type=str, default='photo.jpg', help='保存的文件名')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    filename = args.filename
    if not filename.endswith('.jpg'):
        filename += '.jpg'
    
    print(f"正在拍照...")
    edu.xgoTakePhoto(filename)
    print(f"照片已保存: /home/pi/xgoPictures/{filename}")

if __name__ == '__main__':
    main()

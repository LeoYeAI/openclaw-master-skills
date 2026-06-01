#!/usr/bin/env python3
"""XGO屏幕显示HTTP图片"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import requests
from PIL import Image
from io import BytesIO
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='XGO屏幕显示HTTP图片')
    parser.add_argument('--url', type=str, required=True, help='图片HTTP URL')
    parser.add_argument('--x', type=int, default=0, help='显示位置X坐标，默认0')
    parser.add_argument('--y', type=int, default=0, help='显示位置Y坐标，默认0')
    args = parser.parse_args()
    
    edu = XGOEDU()
    
    response = requests.get(args.url, timeout=10)
    response.raise_for_status()
    
    image = Image.open(BytesIO(response.content))
    image = image.resize((320, 240))
    
    edu.splash.paste(image, (args.x, args.y))
    edu.display.ShowImage(edu.splash)
    print(f"已显示HTTP图片: {args.url}")

if __name__ == '__main__':
    main()

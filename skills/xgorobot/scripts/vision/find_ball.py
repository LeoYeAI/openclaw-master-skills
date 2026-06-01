#!/usr/bin/env python3
"""
寻找指定颜色的小球 - 与 catch_ball.py 使用相同的检测参数
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
import cv2
import numpy as np
from xgolib import XGO
from edulib import XGOEDU

# HSV颜色范围（与 catch_ball.py 和官方 demo 一致）
COLOR_RANGES = {
    'red': {
        'lower1': np.array([0, 100, 80]),
        'upper1': np.array([10, 255, 255]),
        'lower2': np.array([160, 100, 80]),
        'upper2': np.array([180, 255, 255])
    },
    'green': {
        'lower1': np.array([40, 60, 75]),
        'upper1': np.array([77, 255, 255])
    },
    'blue': {
        'lower1': np.array([90, 50, 50]),
        'upper1': np.array([130, 255, 255])
    }
}

def detect_ball(hsv, color):
    """检测特定颜色的小球"""
    ranges = COLOR_RANGES[color]
    
    if color == 'red':
        mask1 = cv2.inRange(hsv, ranges['lower1'], ranges['upper1'])
        mask2 = cv2.inRange(hsv, ranges['lower2'], ranges['upper2'])
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = cv2.inRange(hsv, ranges['lower1'], ranges['upper1'])
    
    return mask

def main():
    parser = argparse.ArgumentParser(description='寻找指定颜色的小球')
    parser.add_argument('--color', type=str, default='red', choices=['red', 'green', 'blue'], help='小球颜色')
    parser.add_argument('--timeout', type=float, default=30, help='最大搜索时间（秒）')
    args = parser.parse_args()
    
    color_names = {'red': '红色', 'green': '绿色', 'blue': '蓝色'}
    color_name = color_names[args.color]
    
    dog = XGO()
    edu = XGOEDU()
    
    print(f"开始搜索{color_name}小球，超时时间: {args.timeout}秒")
    edu.lcd_clear()
    edu.lcd_text(5, 5, f"搜索{color_name}小球", "YELLOW", 14)
    
    # 趴下准备姿势（与 catch_ball.py 一致，摄像头朝向地面才能看到球）
    dog.attitude('p', 15)
    dog.translation('z', 75)
    time.sleep(2)
    
    # 初始化摄像头
    edu.open_camera()
    time.sleep(1)
    
    start_time = time.time()
    found = False
    
    while time.time() - start_time < args.timeout:
        try:
            image = edu.picam2.capture_array()
            if image is None:
                continue
            
            image = cv2.GaussianBlur(image, (3, 3), 0)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mask = detect_ball(hsv, args.color)
            
            masked_image = cv2.bitwise_and(image, image, mask=mask)
            gray_img = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
            
            # 使用 HoughCircles（与 catch_ball.py 一致）
            circles = cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 1, 30,
                                       param1=36, param2=12, minRadius=5, maxRadius=80)
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                max_idx = np.argmax(circles[:, 2])
                x, y, r = circles[max_idx]
                
                if r > 5:
                    found = True
                    # 距离计算与 catch_ball.py 一致
                    distance_cm = 54.82 - r
                    
                    edu.lcd_clear()
                    edu.lcd_text(5, 5, f"找到{color_name}小球", "GREEN", 14)
                    edu.lcd_text(5, 25, f"位置:({int(x)}, {int(y)})", "WHITE", 12)
                    edu.lcd_text(5, 45, f"距离:约{int(distance_cm)}cm", "CYAN", 12)
                    
                    print(f"✓ 找到{color_name}小球！位置:({int(x)}, {int(y)}), 半径:{int(r)}, 距离:约{int(distance_cm)}cm")
                    break
                    
        except Exception as e:
            print(f"检测异常: {e}")
        
        time.sleep(0.1)
    
    if not found:
        edu.lcd_clear()
        edu.lcd_text(5, 5, f"未找到{color_name}小球", "RED", 14)
        print(f"✗ 搜索超时，未找到{color_name}小球")

if __name__ == '__main__':
    main()

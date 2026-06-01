#!/usr/bin/env python3
"""
人脸计数 - 统计画面中的人脸数量
用法: python face_count.py
输出: 
  - 共检测到 N 张人脸
  - 每张人脸的位置信息
示例输出:
  共检测到 3 张人脸
  人脸1: x=100, y=50, w=60, h=60
  人脸2: x=200, y=80, w=55, h=55
  人脸3: x=150, y=120, w=50, h=50
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import cv2
from edulib import XGOEDU, face_detection

def main():
    edu = XGOEDU()
    
    # 初始化人脸检测器
    face_detector = face_detection(0.7)
    
    # 打开摄像头并获取图像
    edu.open_camera()
    image = edu.picam2.capture_array()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.flip(image, 1)
    
    # 检测所有人脸
    faces = face_detector.run(image)
    
    # 输出结果
    count = len(faces)
    print(f"共检测到 {count} 张人脸")
    
    if count > 0:
        for i, face in enumerate(faces, 1):
            rect = face['rect']
            print(f"人脸{i}: x={rect[0]}, y={rect[1]}, w={rect[2]}, h={rect[3]}")
    else:
        print("画面中没有检测到人脸")

if __name__ == '__main__':
    main()

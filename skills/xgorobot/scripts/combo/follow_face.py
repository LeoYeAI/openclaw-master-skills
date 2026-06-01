#!/usr/bin/env python3
"""
人脸追踪 - 检测人脸并控制机器狗转向追踪
用法: python follow_face.py
按C键退出
"""
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO
from edulib import XGOEDU

def main():
    dog = XGO()
    edu = XGOEDU()
    
    print("人脸追踪模式... 按C键退出")
    edu.lcd_text(10, 100, "人脸追踪 按C退出", "YELLOW", 20)
    
    while not edu.xgoButton("c"):
        result = edu.face_detect()
        
        if result:
            x, y, w, h = result
            center_x = x + w // 2
            
            # 计算偏离中心的距离 (屏幕宽度320)
            error = center_x - 160
            
            if error > 40:
                dog.turnright(30)
                print(f"人脸在右侧, 右转 (偏移={error})")
            elif error < -40:
                dog.turnleft(30)
                print(f"人脸在左侧, 左转 (偏移={error})")
            else:
                dog.stop()
                print(f"人脸居中 (偏移={error})")
        else:
            dog.stop()
        
        time.sleep(0.1)
    
    dog.stop()
    dog.reset()
    print("追踪结束")

if __name__ == '__main__':
    main()

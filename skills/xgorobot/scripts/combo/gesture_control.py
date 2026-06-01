#!/usr/bin/env python3
"""
手势控制 - 通过手势控制机器狗
用法: python gesture_control.py
手势映射:
  '5' (张开五指) -> 前进
  '1' (食指)    -> 后退
  '2' (食指中指) -> 左转
  '3' (三指)    -> 右转
  'Good' (点赞) -> 坐下
  'Stone'(拳头) -> 停止
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
    
    print("手势控制模式... 按C键退出")
    print("手势: 5=前进, 1=后退, 2=左转, 3=右转, Good=坐下, Stone=停止")
    edu.lcd_text(5, 100, "手势控制 按C退出", "YELLOW", 18)
    
    last_gesture = None
    
    while not edu.xgoButton("c"):
        result = edu.gestureRecognition()
        
        if result:
            gesture, pos = result
            
            # 去抖动：手势变化才执行
            if gesture != last_gesture:
                last_gesture = gesture
                
                if gesture == '5':
                    print("手势5 -> 前进")
                    dog.forward(15)
                elif gesture == '1':
                    print("手势1 -> 后退")
                    dog.back(15)
                elif gesture == '2':
                    print("手势2 -> 左转")
                    dog.turnleft(40)
                elif gesture == '3':
                    print("手势3 -> 右转")
                    dog.turnright(40)
                elif gesture == 'Good':
                    print("点赞 -> 坐下")
                    dog.stop()
                    dog.action(1, wait=True)
                elif gesture == 'Stone':
                    print("拳头 -> 停止")
                    dog.stop()
                elif gesture == '4':
                    print("手势4 -> 摇摆")
                    dog.periodic_rot(['r'], [3])
        else:
            # 没检测到手势，停止运动
            if last_gesture not in [None, 'Stone', 'Good']:
                dog.stop()
                dog.periodic_rot(['r'], [0])
            last_gesture = None
        
        time.sleep(0.2)
    
    dog.stop()
    dog.reset()
    print("控制结束")

if __name__ == '__main__':
    main()

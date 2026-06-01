#!/usr/bin/env python3
"""
二维码巡逻 - 扫描二维码并执行对应动作
用法: python qr_patrol.py
二维码指令:
  "forward" -> 前进
  "back"    -> 后退
  "left"    -> 左转
  "right"   -> 右转
  "sit"     -> 坐下
  "wave"    -> 招手
  "stop"    -> 停止
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
    
    print("二维码巡逻模式... 按C键退出")
    edu.lcd_text(10, 100, "扫码控制 按C退出", "YELLOW", 18)
    
    while not edu.xgoButton("c"):
        result = edu.QRRecognition()
        
        if result:
            cmd = result[0].lower().strip()
            print(f"扫描到指令: {cmd}")
            
            if cmd == "forward":
                dog.forward(15)
                time.sleep(2)
                dog.stop()
            elif cmd == "back":
                dog.back(15)
                time.sleep(2)
                dog.stop()
            elif cmd == "left":
                dog.turnleft(50)
                time.sleep(1)
                dog.stop()
            elif cmd == "right":
                dog.turnright(50)
                time.sleep(1)
                dog.stop()
            elif cmd == "sit":
                dog.action(1, wait=True)
            elif cmd == "wave":
                dog.action(12, wait=True)
            elif cmd == "stop":
                dog.stop()
            
            time.sleep(1)  # 防止重复扫描
        
        time.sleep(0.2)
    
    dog.stop()
    dog.reset()
    print("巡逻结束")

if __name__ == '__main__':
    main()

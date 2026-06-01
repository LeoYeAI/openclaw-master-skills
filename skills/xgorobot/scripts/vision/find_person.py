#!/usr/bin/env python3
"""寻找人类目标"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
from xgolib import XGO
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='寻找人类目标')
    parser.add_argument('--timeout', type=float, default=45, help='最大搜索时间（秒）')
    args = parser.parse_args()
    
    dog = XGO()
    edu = XGOEDU()
    
    print(f"开始搜索人类目标，超时时间: {args.timeout}秒")
    
    # 初始化摄像头
    try:
        edu.open_camera()
        time.sleep(1)
    except Exception as e:
        print(f"✗ 摄像头初始化失败: {e}")
        return
    
    edu.lcd_clear()
    edu.lcd_text(5, 5, "搜索人类目标", "YELLOW", 14)
    
    start_time = time.time()
    found = False
    
    while time.time() - start_time < args.timeout:
        try:
            face_rect = edu.face_detect()
            
            if face_rect is not None:
                found = True
                x, y, w, h = face_rect
                
                edu.lcd_clear()
                edu.lcd_text(5, 5, "找到人类目标", "GREEN", 14)
                edu.lcd_text(5, 25, f"位置:({int(x)}, {int(y)})", "WHITE", 12)
                edu.lcd_text(5, 45, f"大小:{int(w)}x{int(h)}", "WHITE", 12)
                
                print(f"✓ 找到人类目标！位置:({int(x)}, {int(y)}), 大小:{int(w)}x{int(h)}")
                break
        except Exception as e:
            print(f"检测异常: {e}")
        
        time.sleep(0.1)
    
    if not found:
        edu.lcd_clear()
        edu.lcd_text(5, 5, "未找到人类目标", "RED", 14)
        print(f"✗ 搜索超时，未找到人类目标")

if __name__ == '__main__':
    main()

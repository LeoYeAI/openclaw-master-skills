#!/usr/bin/env python3
"""
颜色追踪 - 追踪指定颜色物体
用法: python follow_color.py [--color COLOR]
参数:
  --color: 颜色 R(红)/G(绿)/B(蓝)/Y(黄)，默认R
按C键退出
"""
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='颜色追踪')
    parser.add_argument('--color', type=str, default='R', choices=['R', 'G', 'B', 'Y'])
    args = parser.parse_args()
    
    dog = XGO()
    edu = XGOEDU()
    
    color_names = {'R': '红色', 'G': '绿色', 'B': '蓝色', 'Y': '黄色'}
    print(f"追踪{color_names[args.color]}物体... 按C键退出")
    edu.lcd_text(10, 100, f"追踪{color_names[args.color]} 按C退出", "YELLOW", 18)
    
    while not edu.xgoButton("c"):
        (x, y), radius = edu.ColorRecognition(mode=args.color)
        
        if radius > 15:
            # 计算偏离中心
            error = x - 160
            
            if error > 30:
                dog.turnright(25)
            elif error < -30:
                dog.turnleft(25)
            else:
                # 居中时前进
                if radius < 80:
                    dog.forward(12)
                else:
                    dog.stop()
        else:
            dog.stop()
        
        time.sleep(0.1)
    
    dog.stop()
    dog.reset()
    print("追踪结束")

if __name__ == '__main__':
    main()

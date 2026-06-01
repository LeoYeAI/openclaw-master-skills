#!/usr/bin/env python3
"""
巡线行走 - 沿着线条行走
用法: python line_follow.py [--color COLOR]
参数:
  --color: 线条颜色 K(黑)/W(白)，默认K
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
    parser = argparse.ArgumentParser(description='巡线行走')
    parser.add_argument('--color', type=str, default='K', choices=['K', 'W'])
    args = parser.parse_args()
    
    dog = XGO()
    edu = XGOEDU()
    
    color_name = '黑线' if args.color == 'K' else '白线'
    print(f"巡{color_name}模式... 按C键退出")
    edu.lcd_text(10, 100, f"巡{color_name} 按C退出", "YELLOW", 20)
    
    while not edu.xgoButton("c"):
        result = edu.LineRecognition(mode=args.color)
        x = result['x']
        angle = result['angle']
        
        if x > 0:
            # 计算偏移量
            offset = x - 160
            
            # 根据偏移量调整转向
            if offset > 25:
                dog.turnright(25)
            elif offset < -25:
                dog.turnleft(25)
            else:
                dog.turn(0)
            
            # 前进
            dog.forward(10)
        else:
            # 找不到线，停止
            dog.stop()
        
        time.sleep(0.05)
    
    dog.stop()
    dog.reset()
    print("巡线结束")

if __name__ == '__main__':
    main()

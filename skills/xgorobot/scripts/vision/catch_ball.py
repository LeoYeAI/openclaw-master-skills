#!/usr/bin/env python3
"""
XGO机器狗抓取小球 - 完全基于 mini.py xgo_catch_ball 逻辑
支持红、绿、蓝三种颜色小球
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

# HSV颜色范围 - 来自 mini.py xgo_catch_ball
COLOR_RANGES = {
    'red': {
        'lower1': np.array([0, 120, 60]),
        'upper1': np.array([15, 255, 255]),
        'lower2': np.array([160, 120, 60]),
        'upper2': np.array([180, 255, 255])
    },
    'blue': {
        'lower1': np.array([90, 100, 60]),
        'upper1': np.array([130, 255, 255]),
        'lower2': np.array([90, 100, 60]),
        'upper2': np.array([130, 255, 255])
    },
    'green': {
        'lower1': np.array([40, 80, 60]),
        'upper1': np.array([80, 255, 255]),
        'lower2': np.array([40, 80, 60]),
        'upper2': np.array([80, 255, 255])
    }
}

def detect_ball(frame, color):
    """检测特定颜色的小球 - 来自 mini.py"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ranges = COLOR_RANGES[color]
    
    # 创建掩码
    if color == 'red':
        mask1 = cv2.inRange(hsv, ranges['lower1'], ranges['upper1'])
        mask2 = cv2.inRange(hsv, ranges['lower2'], ranges['upper2'])
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = cv2.inRange(hsv, ranges['lower1'], ranges['upper1'])
    
    # 形态学处理 - 来自 mini.py
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 应用掩码
    masked = cv2.bitwise_and(frame, frame, mask=mask)
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 2)
    
    # 霍夫圆变换 - 参数来自 mini.py
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=25,
        param1=40,
        param2=18,
        minRadius=10,
        maxRadius=80
    )
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        if len(circles) > 0:
            max_circle = max(circles, key=lambda c: c[2])
            return int(max_circle[0]), int(max_circle[1]), int(max_circle[2])
    
    return 0, 0, 0

def calculate_distance(radius):
    """根据半径估算距离(cm) - 来自 mini.py"""
    if radius == 0:
        return float('inf')
    return 600 / radius

def make_lie_down(dog):
    """让机器狗趴下 - 来自 mini.py"""
    dog.translation('z', 75)
    dog.attitude('p', 25)
    time.sleep(1)

def check_grab_success(dog):
    """检查抓取是否成功 - 来自 mini.py"""
    try:
        motor_angles = dog.read_motor()
        if motor_angles and len(motor_angles) >= 15:
            claw_angle = motor_angles[12]
            return claw_angle > -60
        return False
    except:
        return False

def attempt_catch(dog):
    """执行一次抓取 - 来自 mini.py"""
    # 打开夹爪
    dog.claw(0)
    time.sleep(0.5)
    
    # 移动机械臂到抓取位置
    dog.arm_polar(226, 130)
    time.sleep(2)
    
    # 闭合夹爪
    dog.claw(245)
    time.sleep(1.5)
    
    # 检测成功
    success = check_grab_success(dog)
    
    if success:
        # 抬起展示
        dog.arm_polar(90, 100)
        time.sleep(1)
        dog.attitude('p', 10)
        time.sleep(1)
        return True
    else:
        # 重置
        dog.claw(0)
        time.sleep(0.5)
        dog.arm_polar(90, 100)
        time.sleep(1)
        return False

def main():
    parser = argparse.ArgumentParser(description='XGO机器狗抓取小球')
    parser.add_argument('--color', type=str, default='red', choices=['red', 'green', 'blue'], help='小球颜色')
    parser.add_argument('--timeout', type=float, default=30, help='最大搜索时间（秒）')
    parser.add_argument('--max-grab-attempts', type=int, default=3, help='最大抓取尝试次数')
    args = parser.parse_args()
    
    color_names = {'red': '红色', 'green': '绿色', 'blue': '蓝色'}
    color_name = color_names[args.color]
    
    dog = XGO()
    edu = XGOEDU()
    
    # 读取固件判断机型
    fm = dog.read_firmware()
    dog_type = fm[0] if fm else 'M'
    print(f"机型: XGO-{dog_type}")
    
    print(f"开始抓取{color_name}小球...")
    edu.lcd_clear()
    edu.lcd_text(5, 5, f"抓取{color_name}小球", "YELLOW", 14)
    
    # 趴下准备姿势 - 来自 mini.py
    make_lie_down(dog)
    
    # 初始化摄像头
    edu.open_camera()
    time.sleep(2)
    
    start_time = time.time()
    x_center = 160  # 画面中心x坐标
    
    # 搜索参数 - 来自 mini.py
    search_attempts = 0
    max_search_attempts = 50
    found_ball = False
    
    while search_attempts < max_search_attempts and not found_ball:
        if args.timeout > 0 and (time.time() - start_time) > args.timeout:
            dog.reset()
            print(f"⏰ 搜索超时，未找到{color_name}小球")
            edu.lcd_clear()
            edu.lcd_text(5, 5, "搜索超时", "RED", 16)
            return
        
        try:
            frame = edu.picam2.capture_array()
            if frame is None:
                continue
            
            ball_x, ball_y, ball_radius = detect_ball(frame, args.color)
            
            if ball_radius > 0:
                distance = calculate_distance(ball_radius)
                print(f"检测: x={ball_x}, r={ball_radius}, 距离={distance:.1f}cm")
                
                if distance > 16.9:
                    # 距离远，前进 - 来自 mini.py
                    print(f"距离远({distance:.1f}cm > 16.9)，前进")
                    dog.move('x', 3)
                    time.sleep(1.2)
                    dog.stop()
                elif distance < 13:
                    # 距离太近，后退 - 来自 mini.py
                    print(f"距离太近({distance:.1f}cm < 13)，后退")
                    dog.move('x', -3)
                    time.sleep(0.8)
                    dog.stop()
                elif 13 <= distance <= 16.9:
                    # 调整左右位置 - 来自 mini.py
                    if abs(ball_x - x_center) > 20:
                        if ball_x > x_center:
                            # 球在右边，向左平移 - 来自 mini.py
                            print(f"球在右侧(x={ball_x}>{x_center})，向左平移")
                            dog.move('y', 3)
                            time.sleep(0.6)
                            dog.stop()
                        else:
                            # 球在左边，向右平移 - 来自 mini.py
                            print(f"球在左侧(x={ball_x}<{x_center})，向右平移")
                            dog.move('y', -3)
                            time.sleep(0.6)
                            dog.stop()
                        continue
                    
                    # 位置合适，准备抓取
                    print(f"位置合适！距离={distance:.1f}cm, 偏移={abs(ball_x - x_center)}px")
                    found_ball = True
                    break
            else:
                # 没看到球，转向搜索 - 来自 mini.py
                if search_attempts % 4 == 3:
                    print("没看见球，转动搜索...")
                    dog.turn(60)
                    time.sleep(0.8)
                    dog.stop()
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"检测异常: {e}")
        
        search_attempts += 1
        time.sleep(0.6)
    
    # 尝试抓取 - 来自 mini.py
    grabbed_successfully = False
    grab_attempts = 0
    
    if found_ball:
        edu.lcd_clear()
        edu.lcd_text(5, 5, f"抓取{color_name}小球", "ORANGE", 14)
        
        while grab_attempts < args.max_grab_attempts and not grabbed_successfully:
            print(f"尝试抓取第{grab_attempts + 1}次...")
            grabbed_successfully = attempt_catch(dog)
            grab_attempts += 1
            
            if not grabbed_successfully and grab_attempts < args.max_grab_attempts:
                print("抓取失败，重新调整...")
                time.sleep(1)
    
    # 站起 - 来自 mini.py
    dog.action(2)
    time.sleep(3)
    dog.reset()
    
    # 返回结果
    total_time = int(time.time() - start_time)
    
    if grabbed_successfully:
        edu.lcd_clear()
        edu.lcd_text(5, 5, "抓取成功!", "GREEN", 16)
        edu.lcd_text(5, 35, f"{color_name}小球已抓取", "WHITE", 12)
        print(f"✅ 成功抓取{color_name}小球！抓取次数:{grab_attempts}, 耗时:{total_time}秒")
    else:
        edu.lcd_clear()
        edu.lcd_text(5, 5, "抓取失败", "RED", 16)
        if found_ball:
            print(f"❌ 找到{color_name}小球但抓取失败，尝试{grab_attempts}次，耗时{total_time}秒")
        else:
            print(f"❌ 未找到{color_name}小球，搜索{search_attempts}次，耗时{total_time}秒")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
XGO机器狗走向指定目标 - 使用AI图片理解识别目标位置并导航
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
import base64
import requests
import cv2
import re
from xgolib import XGO
from edulib import XGOEDU

def ai_locate_target(edu, api_key, target):
    """使用AI识别目标位置，返回 'left'/'center'/'right'/'none'"""
    path = "/home/pi/xgoPictures/"
    os.makedirs(path, exist_ok=True)
    photo_path = os.path.join(path, "goto_target_temp.jpg")
    
    # 拍照
    edu.camera_still = False
    time.sleep(0.3)
    
    if edu.picam2 is None:
        edu.open_camera()
        time.sleep(1)
    
    image = edu.picam2.capture_array()
    cv2.imwrite(photo_path, image)
    
    with open(photo_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    
    prompt = f"""请分析图片中"{target}"的位置。
要求：
1. 如果能看到"{target}"，判断它在画面中的水平位置
2. 将画面水平分成三等份：左侧(left)、中间(center)、右侧(right)
3. 只回复一个单词：left、center、right 或 none（如果看不到目标）

注意：只回复位置单词，不要有其他内容。"""
    
    data = {
        "model": "qwen-vl-max",
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "You are a vision assistant. Reply with only one word: left, center, right, or none."}]},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_data}},
                {"type": "text", "text": prompt}
            ]}
        ]
    }
    
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers, json=data, timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"].strip().lower()
                # 提取位置关键词
                for pos in ['left', 'center', 'right', 'none']:
                    if pos in answer:
                        return pos
                # 如果回答包含中文
                if '左' in answer:
                    return 'left'
                elif '中' in answer:
                    return 'center'
                elif '右' in answer:
                    return 'right'
                elif '没' in answer or '无' in answer or '不' in answer:
                    return 'none'
        return 'none'
    except Exception as e:
        print(f"AI识别异常: {e}")
        return 'none'

def ai_check_target_size(edu, api_key, target):
    """使用AI判断目标大小，用于估计距离"""
    path = "/home/pi/xgoPictures/"
    photo_path = os.path.join(path, "goto_target_temp.jpg")
    
    edu.camera_still = False
    time.sleep(0.3)
    
    image = edu.picam2.capture_array()
    cv2.imwrite(photo_path, image)
    
    with open(photo_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    
    prompt = f"""分析"{target}"在画面中占据的大小比例。
将画面高度分成：very_small(占<15%)、small(15-30%)、medium(30-50%)、large(50-70%)、very_large(>70%)
只回复一个单词：very_small、small、medium、large、very_large 或 none（看不到目标）"""
    
    data = {
        "model": "qwen-vl-max",
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "You are a vision assistant. Reply with only one word."}]},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_data}},
                {"type": "text", "text": prompt}
            ]}
        ]
    }
    
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers, json=data, timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"].strip().lower()
                for size in ['very_large', 'very_small', 'large', 'small', 'medium', 'none']:
                    if size.replace('_', '') in answer.replace('_', '').replace(' ', ''):
                        return size
        return 'small'
    except:
        return 'small'

def main():
    parser = argparse.ArgumentParser(description='XGO机器狗走向指定目标')
    parser.add_argument('--target', type=str, required=True, help='目标物体名称（如：黄色小鸡、紫色兔子、红色球）')
    parser.add_argument('--timeout', type=float, default=60, help='最大执行时间（秒）')
    parser.add_argument('--api-key', type=str, default=os.environ.get('DASHSCOPE_API_KEY'), help='阿里云API密钥')
    args = parser.parse_args()
    
    if not args.api_key:
        print('错误: 未提供API密钥，请设置环境变量DASHSCOPE_API_KEY或使用--api-key参数')
        return
    
    target = args.target
    print(f"目标: 走向「{target}」")
    
    dog = XGO()
    edu = XGOEDU()
    
    # 初始化显示
    edu.lcd_clear()
    edu.lcd_text(5, 5, f"走向:{target[:6]}", "YELLOW", 14)
    
    # 初始化摄像头
    edu.open_camera()
    time.sleep(1)
    
    # 站立姿态
    dog.reset()
    time.sleep(1)
    
    start_time = time.time()
    reached = False
    step_count = 0
    max_steps = 20
    
    while step_count < max_steps:
        if args.timeout > 0 and (time.time() - start_time) > args.timeout:
            print(f"⏰ 超时，已执行{step_count}步")
            break
        
        step_count += 1
        print(f"\n--- 第{step_count}步 ---")
        
        # AI识别目标位置
        edu.lcd_text(5, 25, "AI识别中...", "CYAN", 12)
        position = ai_locate_target(edu, args.api_key, target)
        print(f"目标位置: {position}")
        
        if position == 'none':
            # 看不到目标，转向搜索
            edu.lcd_text(5, 45, "搜索中...", "ORANGE", 12)
            print("看不到目标，转向搜索...")
            dog.turn(40)
            time.sleep(1)
            dog.stop()
            time.sleep(0.5)
            continue
        
        # 检查目标大小（估计距离）
        size = ai_check_target_size(edu, args.api_key, target)
        print(f"目标大小: {size}")
        
        # 判断是否已经到达
        if size in ['large', 'very_large']:
            reached = True
            print(f"✓ 已到达目标「{target}」附近！")
            edu.lcd_clear()
            edu.lcd_text(5, 5, "到达目标!", "GREEN", 16)
            edu.lcd_text(5, 35, target[:8], "WHITE", 12)
            break
        
        # 根据位置调整方向
        if position == 'left':
            edu.lcd_text(5, 45, "左转调整", "WHITE", 12)
            print("目标在左侧，左转...")
            dog.turn(25)
            time.sleep(0.6)
            dog.stop()
        elif position == 'right':
            edu.lcd_text(5, 45, "右转调整", "WHITE", 12)
            print("目标在右侧，右转...")
            dog.turn(-25)
            time.sleep(0.6)
            dog.stop()
        
        # 前进
        edu.lcd_text(5, 65, "前进中...", "GREEN", 12)
        print("向目标前进...")
        
        # 根据距离决定前进步长
        if size == 'very_small':
            step = 15
            duration = 2.0
        elif size == 'small':
            step = 12
            duration = 1.5
        else:  # medium
            step = 8
            duration = 1.0
        
        dog.move('x', step)
        time.sleep(duration)
        dog.stop()
        time.sleep(0.5)
    
    # 完成
    dog.stop()
    total_time = int(time.time() - start_time)
    
    if reached:
        print(f"\n✅ 成功走向「{target}」！步数:{step_count}, 耗时:{total_time}秒")
    else:
        edu.lcd_clear()
        edu.lcd_text(5, 5, "未能到达", "RED", 16)
        print(f"\n❌ 未能到达「{target}」，步数:{step_count}, 耗时:{total_time}秒")

if __name__ == '__main__':
    main()

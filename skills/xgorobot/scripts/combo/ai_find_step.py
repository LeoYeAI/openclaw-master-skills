#!/usr/bin/env python3
"""
AI智能踩物 - 用AI视觉识别目标物体，走向它并抬腿踩上去
用法: python ai_find_step.py --target "纸巾"
参数:
  --target: 目标物体名称（如"纸巾"、"胡萝卜"等）
  --leg: 用哪只腿踩，1=左前腿(默认), 2=右前腿
  --voice: TTS音色，默认Rocky（粤语阿强，笨拙机器感）
按C键可随时退出
"""
import argparse
import time
import sys
import os
import base64
import requests
import subprocess
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from xgolib import XGO
from edulib import XGOEDU


def ai_analyze_position(edu, api_key, target):
    """拍照并用AI分析目标物体位置"""
    path = "/home/pi/xgoPictures/"
    os.makedirs(path, exist_ok=True)
    photo_path = os.path.join(path, "ai_find_step_temp.jpg")
    
    # 拍照
    if edu.picam2 is None:
        edu.open_camera()
    edu.camera_still = False
    time.sleep(0.3)
    image = edu.picam2.capture_array()
    cv2.imwrite(photo_path, image)
    
    # 编码图片
    with open(photo_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # 调用AI分析
    prompt = f"""请仔细观察图片，找出"{target}"的位置。
只需回答以下格式之一（不要说其他内容）：
- 如果{target}在图片左侧1/3区域：回答"左边"
- 如果{target}在图片中间1/3区域：回答"中间"  
- 如果{target}在图片右侧1/3区域：回答"右边"
- 如果图片中没有{target}：回答"没有"
- 如果{target}在中间且占据图片很大面积(接近了)：回答"到了"
"""
    
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-vl-max",
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "你是一个精确的视觉位置判断助手，只需简短回答位置。"}]},
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
                answer = result["choices"][0]["message"]["content"].strip()
                return answer
    except Exception as e:
        print(f"AI分析出错: {e}")
    
    return "没有"


def text_to_speech(text, speed=120):
    """用eSpeak播放语音（机械感）"""
    try:
        # eSpeak中文语音，speed控制语速（默认120，越小越慢越笨拙）
        # -v zh 中文，-s 语速，-p 音调(50=低沉)
        cmd = f'espeak -v zh -s {speed} -p 50 "{text}"'
        subprocess.run(cmd, shell=True, check=True,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"TTS出错: {e}")
    return False


def step_on_target(dog, leg_id):
    """抬腿踩下动作"""
    leg_names = {1: "左前腿", 2: "右前腿"}
    print(f"抬起{leg_names[leg_id]}...")
    
    # 先站稳
    dog.stop()
    time.sleep(0.3)
    
    # 抬腿（z值变小=抬高）
    dog.leg(leg_id, [20, 0, 60])  # 向前伸出并抬高
    time.sleep(0.8)
    
    # 踩下（z值变大=放下，x向前）
    dog.leg(leg_id, [25, 0, 110])  # 向前踩下
    time.sleep(0.5)
    
    print(f"✓ {leg_names[leg_id]}已踩下")


def main():
    parser = argparse.ArgumentParser(description='AI智能踩物')
    parser.add_argument('--target', type=str, required=True, help='目标物体名称（如"纸巾"）')
    parser.add_argument('--leg', type=int, default=1, choices=[1, 2], help='用哪只腿踩: 1=左前腿, 2=右前腿')
    parser.add_argument('--speed', type=int, default=100, help='语音速度(越小越慢越机械,默认100)')
    parser.add_argument('--api-key', type=str, default=os.environ.get('DASHSCOPE_API_KEY'), help='API密钥')
    parser.add_argument('--max-attempts', type=int, default=10, help='最大尝试次数')
    args = parser.parse_args()
    
    if not args.api_key:
        print('错误: 未提供API密钥，请设置环境变量DASHSCOPE_API_KEY或使用--api-key参数')
        return
    
    dog = XGO()
    edu = XGOEDU()
    
    leg_names = {1: "左前腿", 2: "右前腿"}
    print(f"任务: 找到「{args.target}」并用{leg_names[args.leg]}踩上去")
    print("按C键可随时退出")
    
    edu.lcd_clear()
    edu.lcd_text(5, 5, f"寻找: {args.target}", "YELLOW", 16)
    edu.lcd_text(5, 100, "按C键退出", "WHITE", 12)
    
    attempts = 0
    found = False
    
    while not edu.xgoButton("c") and attempts < args.max_attempts:
        attempts += 1
        print(f"\n第{attempts}次观察...")
        edu.lcd_text(5, 30, f"观察中...({attempts})", "CYAN", 14)
        
        # AI分析位置
        position = ai_analyze_position(edu, args.api_key, args.target)
        print(f"AI判断: {args.target}在 {position}")
        edu.lcd_text(5, 55, f"位置: {position}", "GREEN", 14)
        
        if "没有" in position:
            print("未发现目标，原地转圈寻找...")
            dog.turnleft(40)
            time.sleep(1.5)
            dog.stop()
            time.sleep(0.5)
            
        elif "左" in position:
            print("目标在左边，左转...")
            dog.turnleft(35)
            time.sleep(0.8)
            dog.stop()
            time.sleep(0.3)
            
        elif "右" in position:
            print("目标在右边，右转...")
            dog.turnright(35)
            time.sleep(0.8)
            dog.stop()
            time.sleep(0.3)
            
        elif "中" in position:
            print("目标在中间，前进靠近...")
            dog.forward(15)
            time.sleep(1.2)
            dog.stop()
            time.sleep(0.5)
            
        elif "到了" in position:
            print("已到达目标位置！")
            found = True
            break
        
        time.sleep(0.3)
    
    if edu.xgoButton("c"):
        print("\n用户取消")
        dog.stop()
        dog.reset()
        return
    
    if found:
        # 执行踩踏动作
        edu.lcd_clear()
        edu.lcd_text(5, 5, "踩踏中...", "YELLOW", 18)
        
        step_on_target(dog, args.leg)
        
        # 语音播报
        edu.lcd_clear()
        edu.lcd_text(5, 5, f"这个是{args.target}", "GREEN", 18)
        
        speech_text = f"这个，是，{args.target}"
        print(f"语音播报: {speech_text}")
        text_to_speech(speech_text, args.speed)
        
        time.sleep(2)
        
        # 复位
        dog.reset()
        print(f"\n✓ 任务完成: 已找到并踩住「{args.target}」")
    else:
        print(f"\n✗ 尝试{args.max_attempts}次后仍未找到「{args.target}」")
        edu.lcd_clear()
        edu.lcd_text(5, 5, f"未找到{args.target}", "RED", 16)
        dog.reset()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""XGO AI拍照理解"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
import base64
import requests
import cv2
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='XGO AI拍照理解')
    parser.add_argument('--prompt', type=str, default='图中描绘的是什么景象?', help='提问内容')
    parser.add_argument('--filename', type=str, default='photo_understand', help='照片文件名(不含扩展名)')
    parser.add_argument('--api-key', type=str, default=os.environ.get('DASHSCOPE_API_KEY'), help='阿里云API密钥（默认从环境变量DASHSCOPE_API_KEY读取）')
    args = parser.parse_args()
    
    if not args.api_key:
        print('错误: 未提供API密钥，请设置环境变量DASHSCOPE_API_KEY或使用--api-key参数')
        return
    
    edu = XGOEDU()
    
    path = "/home/pi/xgoPictures/"
    photo_path = os.path.join(path, args.filename + ".jpg")
    
    edu.lcd_clear()
    edu.lcd_text(5, 5, "拍照中...", "YELLOW", 14)
    
    edu.camera_still = False
    time.sleep(0.6)
    
    if edu.picam2 is None:
        edu.open_camera()
    
    image = edu.picam2.capture_array()
    cv2.imwrite(photo_path, image)
    print(f"照片已保存: {photo_path}")
    
    with open(photo_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    edu.lcd_text(5, 30, "AI分析中...", "CYAN", 12)
    
    headers = {
        "Authorization": "Bearer " + args.api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-vl-max",
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_data}},
                {"type": "text", "text": args.prompt}
            ]}
        ]
    }
    
    response = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers=headers, json=data, timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            answer = result["choices"][0]["message"]["content"]
            print(f"问题: {args.prompt}")
            print(f"回答: {answer}")
        else:
            print("API返回数据格式异常")
    else:
        print(f"API请求失败: {response.status_code}")

if __name__ == '__main__':
    main()

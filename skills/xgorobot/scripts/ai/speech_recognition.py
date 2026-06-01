#!/usr/bin/env python3
"""XGO AI语音识别"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import uuid
import base64
import requests
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='XGO AI语音识别')
    parser.add_argument('--seconds', type=int, default=3, help='录音时长(秒)，默认3秒')
    parser.add_argument('--api-key', type=str, default=os.environ.get('DASHSCOPE_API_KEY'), help='阿里云API密钥（默认从环境变量DASHSCOPE_API_KEY读取）')
    args = parser.parse_args()
    
    if not args.api_key:
        print('错误: 未提供API密钥，请设置环境变量DASHSCOPE_API_KEY或使用--api-key参数')
        return
    
    edu = XGOEDU()
    
    temp_audio = f"/tmp/speech_{uuid.uuid4().hex}.wav"
    
    edu.lcd_clear()
    edu.lcd_text(5, 5, "录音中...", "YELLOW", 14)
    edu.lcd_text(5, 30, f"时长: {args.seconds}秒", "WHITE", 12)
    
    os.system(f"arecord -d {args.seconds} -f S16_LE -r 16000 -c 1 -t wav {temp_audio}")
    
    if not os.path.exists(temp_audio):
        print("录音文件不存在")
        return
    
    with open(temp_audio, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')
    
    edu.lcd_text(5, 55, "识别中...", "CYAN", 12)
    
    headers = {
        "Authorization": "Bearer " + args.api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen3-omni-30b-a3b-captioner",
        "messages": [
            {"role": "user", "content": [
                {"type": "input_audio", "input_audio": {"data": "data:audio/wav;base64," + audio_data}}
            ]}
        ]
    }
    
    response = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers=headers, json=data, timeout=30
    )
    
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
    
    if response.status_code == 200:
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            text = result["choices"][0]["message"]["content"]
            print(f"识别结果: {text}")
        else:
            print("API返回数据格式异常")
    else:
        print(f"API请求失败: {response.status_code}")

if __name__ == '__main__':
    main()

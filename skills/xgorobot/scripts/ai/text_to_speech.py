#!/usr/bin/env python3
"""XGO AI文本转语音"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import subprocess
import requests
from edulib import XGOEDU

VOICE_OPTIONS = {
    "Cherry": "芥悦-阳光积极、亲切自然小姐姐",
    "Ethan": "晨熅-标准普通话，带部分北方口音",
    "Nofish": "不吃鱼-不会翘舌音的设计师",
    "Jennifer": "詹妮弗-品牌级、电影质感般美语女声",
    "Ryan": "甜茶-节奏拉满，戏感炸裂",
    "Katerina": "卡捷琳娜-御姐音色，韵律回味十足",
    "Elias": "墨讲师-学科严谨性与叙事技巧",
    "Dylan": "北京-晓东-北京胡同里长大的少年",
    "Sunny": "四川-晴儿-甜到你心里的川妹子",
    "Rocky": "粤语-阿强-幽默风趣的阿强"
}

def main():
    parser = argparse.ArgumentParser(description='XGO AI文本转语音')
    parser.add_argument('--text', type=str, required=True, help='要合成的文本内容')
    parser.add_argument('--voice', type=str, default='Cherry', choices=list(VOICE_OPTIONS.keys()), help='音色选择，默认Cherry')
    parser.add_argument('--api-key', type=str, default=os.environ.get('DASHSCOPE_API_KEY'), help='阿里云API密钥（默认从环境变量DASHSCOPE_API_KEY读取）')
    args = parser.parse_args()
    
    if not args.api_key:
        print('错误: 未提供API密钥，请设置环境变量DASHSCOPE_API_KEY或使用--api-key参数')
        return
    
    edu = XGOEDU()
    
    edu.lcd_clear()
    edu.lcd_text(5, 5, "语音合成中...", "YELLOW", 14)
    
    headers = {
        "Authorization": "Bearer " + args.api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen3-tts-flash",
        "input": {
            "text": args.text,
            "voice": args.voice
        }
    }
    
    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        headers=headers, json=data, timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        if "output" in result and "audio" in result["output"] and "url" in result["output"]["audio"]:
            audio_url = result["output"]["audio"]["url"]
            
            edu.lcd_clear()
            edu.lcd_text(5, 5, "播放中...", "GREEN", 14)
            
            subprocess.run(f'mplayer -really-quiet "{audio_url}"', shell=True, check=True)
            print(f"语音合成完成: {args.text}")
            print(f"音色: {args.voice} ({VOICE_OPTIONS.get(args.voice, '')})")
        else:
            print("API返回数据格式异常")
    else:
        print(f"API请求失败: {response.status_code}")

if __name__ == '__main__':
    main()

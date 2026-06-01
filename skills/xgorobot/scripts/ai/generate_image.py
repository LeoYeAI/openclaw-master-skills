#!/usr/bin/env python3
"""XGO AI生成图片并显示"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import argparse
import time
import requests
from PIL import Image
from io import BytesIO
from edulib import XGOEDU

def main():
    parser = argparse.ArgumentParser(description='XGO AI生成图片并显示')
    parser.add_argument('--prompt', type=str, required=True, help='图片生成提示词')
    parser.add_argument('--size', type=str, default='960*720', help='图片尺寸，默认960*720')
    parser.add_argument('--api-key', type=str, default=os.environ.get('DASHSCOPE_API_KEY'), help='阿里云API密钥（默认从环境变量DASHSCOPE_API_KEY读取）')
    args = parser.parse_args()
    
    if not args.api_key:
        print('错误: 未提供API密钥，请设置环境变量DASHSCOPE_API_KEY或使用--api-key参数')
        return
    
    edu = XGOEDU()
    
    edu.lcd_clear()
    edu.lcd_text(5, 5, "生成图片中...", "YELLOW", 14)
    
    headers = {
        "X-DashScope-Async": "enable",
        "Authorization": "Bearer " + args.api_key,
        "Content-Type": "application/json"
    }
    
    create_data = {
        "model": "wan2.2-t2i-flash",
        "input": {"prompt": args.prompt},
        "parameters": {
            "size": args.size,
            "n": 1,
            "prompt_extend": True,
            "watermark": True
        }
    }
    
    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
        headers=headers, json=create_data, timeout=30
    )
    
    if response.status_code != 200:
        print(f"创建任务失败: {response.status_code}")
        return
    
    result = response.json()
    if "output" not in result or "task_id" not in result["output"]:
        print("创建任务返回数据格式异常")
        return
    
    task_id = result["output"]["task_id"]
    print(f"任务已创建: {task_id}")
    
    query_headers = {"Authorization": "Bearer " + args.api_key}
    
    for attempt in range(30):
        time.sleep(3)
        
        query_response = requests.get(
            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers=query_headers, timeout=15
        )
        
        if query_response.status_code != 200:
            continue
        
        query_result = query_response.json()
        if "output" not in query_result:
            continue
        
        status = query_result["output"].get("task_status", "UNKNOWN")
        print(f"任务状态: {status}")
        
        if status == "SUCCEEDED":
            if "results" in query_result["output"] and len(query_result["output"]["results"]) > 0:
                image_url = query_result["output"]["results"][0].get("url", "")
                if image_url:
                    img_response = requests.get(image_url, timeout=10)
                    image = Image.open(BytesIO(img_response.content))
                    image = image.resize((320, 240))
                    
                    edu.splash.paste(image, (0, 0))
                    edu.display.ShowImage(edu.splash)
                    
                    print(f"图片生成完成: {image_url}")
                    return
        elif status == "FAILED":
            print("图片生成失败")
            return
    
    print("图片生成超时")

if __name__ == '__main__':
    main()

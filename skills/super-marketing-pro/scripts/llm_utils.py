import os
import json
from openai import OpenAI

def get_llm_client():
    """初始化 OpenAI 客户端"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 警告: 未找到 OPENAI_API_KEY 环境变量，将使用本地模拟数据。")
        return None
    
    return OpenAI()

import time

def call_llm(system_prompt, user_prompt, model="gemini-3.0-flash", json_mode=False, max_retries=3):
    """统一的 LLM 调用接口，带指数退避重试机制"""
    client = get_llm_client()
    if not client:
        return None
        
    for attempt in range(max_retries):
        try:
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            if json_mode:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    print("⚠️ 警告: LLM 返回的不是有效的 JSON 格式")
                    return None
                    
            return content
            
        except Exception as e:
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                print(f"⚠️ LLM 调用失败 ({str(e)}), {sleep_time}秒后重试 ({attempt+1}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                print(f"❌ LLM 调用失败，已达到最大重试次数: {str(e)}")
                return None

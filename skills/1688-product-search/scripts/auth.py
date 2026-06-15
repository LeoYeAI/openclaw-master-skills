#!/usr/bin/env python3
"""
1688 API 鉴权模块
- 支持 access_token 直接使用
- 支持 refresh_token 自动刷新
- Token 缓存全局共享
"""

import os
import json
import time
import requests
import hmac
import hashlib
from pathlib import Path

# 全局 Token 缓存路径（所有 1688 Skill 共用）
TOKEN_CACHE_PATH = Path.home() / ".openclaw" / "workspace" / "skills" / ".1688_token_cache.json"

def ensure_cache_dir():
    """确保缓存目录存在"""
    cache_dir = TOKEN_CACHE_PATH.parent
    cache_dir.mkdir(parents=True, exist_ok=True)

def load_cached_token():
    """从缓存加载 token"""
    if not TOKEN_CACHE_PATH.exists():
        return None
    
    try:
        with open(TOKEN_CACHE_PATH, 'r') as f:
            cache = json.load(f)
            # 检查是否过期（提前5分钟刷新）
            if time.time() < cache.get('expires_at', 0) - 300:
                return cache
    except (json.JSONDecodeError, KeyError):
        pass
    
    return None

def save_token_to_cache(token_data, app_key):
    """保存 token 到缓存"""
    ensure_cache_dir()
    
    # 计算过期时间（转换为数字）
    expires_in = int(token_data.get('expires_in', 3600))
    expires_at = time.time() + expires_in
    
    cache_data = {
        'access_token': token_data['access_token'],
        'refresh_token': token_data.get('refresh_token'),
        'expires_at': expires_at,
        'app_key': app_key
    }
    
    with open(TOKEN_CACHE_PATH, 'w') as f:
        json.dump(cache_data, f)

def get_access_token(app_key, app_secret, refresh_token=None, access_token=None):
    """
    获取有效的 access_token
    优先级：缓存 > 环境变量 access_token > refresh_token 刷新
    """
    # 1. 尝试从缓存获取
    cached = load_cached_token()
    if cached and cached.get('app_key') == app_key:
        return cached['access_token']
    
    # 2. 如果提供了 access_token，直接使用（但不缓存，因为不知道过期时间）
    if access_token:
        return access_token
    
    # 3. 使用 refresh_token 刷新
    if refresh_token:
        token_url = f"https://gw.open.1688.com/openapi/param2/1/system.oauth2/getToken/{app_key}"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': app_key,
            'client_secret': app_secret
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            
            if 'access_token' in token_data:
                save_token_to_cache(token_data, app_key)
                return token_data['access_token']
            else:
                raise Exception(f"Token response missing access_token: {token_data}")
                
        except requests.RequestException as e:
            raise Exception(f"Failed to refresh token: {e}")
    
    raise Exception("No valid token source available")

def sign_request_hmac_sha1(url_path, params, app_secret):
    """
    生成 1688 API 签名（HMAC-SHA1算法）
    url_path: 从 param2 开始的URL路径部分
    params: 请求参数字典
    app_secret: 应用密钥
    """
    # 按 key 排序
    sorted_params = sorted(params.items())
    # 拼接成字符串 key+value
    param_str = ''.join([f"{k}{v}" for k, v in sorted_params])
    # 拼接 url_path 和 param_str
    sign_str = url_path + param_str
    # HMAC-SHA1 签名
    signature = hmac.new(
        app_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha1
    ).hexdigest().upper()
    return signature

if __name__ == "__main__":
    # 测试用例
    app_key = os.getenv('ALI1688_APP_KEY')
    app_secret = os.getenv('ALI1688_APP_SECRET')
    refresh_token = os.getenv('ALI1688_REFRESH_TOKEN')
    access_token = os.getenv('ALI1688_ACCESS_TOKEN')
    
    if not app_key or not app_secret:
        print("Error: ALI1688_APP_KEY and ALI1688_APP_SECRET are required")
        exit(1)
    
    try:
        token = get_access_token(app_key, app_secret, refresh_token, access_token)
        print(f"Access token: {token}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
#!/usr/bin/env python3
"""
1688 图片搜索处理脚本
专门处理"图搜同款"、"找同款"等命令
"""

import os
import sys
import json
import argparse
import requests
import base64
import tempfile
import shutil
from urllib.parse import urlparse

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.auth import get_access_token, sign_request_hmac_sha1
from scripts.image_utils import compress_image_if_needed

# API 基础URL
BASE_URL = "https://gw.open.1688.com/openapi"

def get_app_credentials():
    """获取应用凭证"""
    app_key = os.getenv('ALI1688_APP_KEY')
    app_secret = os.getenv('ALI1688_APP_SECRET')
    refresh_token = os.getenv('ALI1688_REFRESH_TOKEN')
    access_token = os.getenv('ALI1688_ACCESS_TOKEN')
    
    if not app_key or not app_secret:
        raise Exception("Missing ALI1688_APP_KEY or ALI1688_APP_SECRET")
    
    return app_key, app_secret, refresh_token, access_token

def download_image_from_url(image_url, temp_dir):
    """从URL下载图片到临时目录"""
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 从URL获取文件扩展名
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            filename = 'downloaded_image.jpg'
        
        temp_path = os.path.join(temp_dir, filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        return temp_path
    except Exception as e:
        raise Exception(f"Failed to download image from URL: {str(e)}")

def upload_image(image_path):
    """上传图片获取imageId（自动压缩大于300KB的图片）"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    # 检查并压缩图片（如果需要）
    compressed_path, was_compressed = compress_image_if_needed(image_path, max_size_kb=300)
    
    try:
        # 读取（可能已压缩的）图片并转换为base64
        with open(compressed_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        upload_params = {
            'imageBase64': base64_image
        }
        
        params = {
            'uploadImageParam': json.dumps(upload_params, separators=(',', ':')),
            'access_token': token
        }
        
        url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.image.upload/{app_key}"
        sign = sign_request_hmac_sha1(url_path, params, app_secret)
        params['_aop_signature'] = sign
        
        url = f"{BASE_URL}/{url_path}"
        response = requests.post(url, data=params, timeout=30)
        response.raise_for_status()
        return response.json()
        
    finally:
        # 如果图片被压缩了，清理临时文件
        if was_compressed and os.path.exists(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass

def image_search(image_id, country='zh', begin_page=1, page_size=20):
    """多语言图片搜索"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    search_params = {
        'imageId': image_id,
        'country': country,
        'beginPage': begin_page,
        'pageSize': page_size
    }
    
    params = {
        'offerQueryParam': json.dumps(search_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.imageQuery/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def process_image_search(image_source, is_url=False, country='zh', begin_page=1, page_size=20):
    """处理图片搜索请求"""
    temp_dir = None
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        if is_url:
            # 从URL下载图片
            image_path = download_image_from_url(image_source, temp_dir)
        else:
            # 使用本地图片路径
            image_path = image_source
        
        # 上传图片获取imageId
        upload_result = upload_image(image_path)
        
        if 'result' not in upload_result or upload_result['result'] == '0':
            raise Exception("Failed to upload image, got imageId=0")
        
        image_id = upload_result['result']
        
        # 使用imageId进行图片搜索
        search_result = image_search(image_id, country, begin_page, page_size)
        
        return search_result
        
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                pass

def main():
    parser = argparse.ArgumentParser(description='1688 Image Search Handler for "图搜同款" and "找同款" commands')
    parser.add_argument('image_source', help='Image URL or local file path')
    parser.add_argument('--is-url', action='store_true', help='Whether the image_source is a URL')
    parser.add_argument('--country', default='zh', help='Country/language code (default: zh)')
    parser.add_argument('--beginPage', type=int, default=1, help='Starting page number (default: 1)')
    parser.add_argument('--pageSize', type=int, default=20, help='Number of results per page (default: 20)')
    
    args = parser.parse_args()
    
    try:
        result = process_image_search(
            args.image_source, 
            args.is_url, 
            args.country, 
            args.beginPage, 
            args.pageSize
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
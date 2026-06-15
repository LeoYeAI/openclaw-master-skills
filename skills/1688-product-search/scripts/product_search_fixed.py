#!/usr/bin/env python3
"""
1688 商品搜索脚本 - 修复版本
支持9个核心接口：类目查询、关键词搜索、图片搜索、商品详情等
修复了图片上传接口的签名问题
"""

import os
import sys
import json
import argparse
import requests
import base64

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.auth_fixed import get_access_token, sign_request_hmac_sha1, sign_image_upload_request
from scripts.image_utils import compress_image_if_needed, cleanup_temp_file

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

def upload_image(image_path):
    """上传图片获取imageId（自动压缩大于300KB的图片）- 修复签名版本"""
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
        
        # 构造 uploadImageParam JSON 字符串（不进行额外编码）
        upload_image_param_json = json.dumps(upload_params, separators=(',', ':'))
        
        # 使用专用签名函数
        url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.image.upload/{app_key}"
        sign = sign_image_upload_request(url_path, upload_image_param_json, token, app_secret)
        
        # 构造请求参数
        params = {
            'uploadImageParam': upload_image_param_json,
            'access_token': token,
            '_aop_signature': sign
        }
        
        url = f"{BASE_URL}/{url_path}"
        response = requests.post(url, data=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # 提取 imageId
        if 'result' in result and isinstance(result['result'], str):
            return result['result']
        else:
            raise Exception(f"Failed to get imageId from upload response: {result}")
        
    finally:
        # 如果图片被压缩了，清理临时文件
        if was_compressed and os.path.exists(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass

def main():
    parser = argparse.ArgumentParser(description='1688 Product Search Skill - Fixed Version')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # 图片上传（修复版本）
    upload_parser = subparsers.add_parser('upload-image', help='Upload image to get imageId (fixed signature)')
    upload_parser.add_argument('image_path', help='Local image file path')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'upload-image':
            result = upload_image(args.image_path)
            print(json.dumps({"imageId": result}, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
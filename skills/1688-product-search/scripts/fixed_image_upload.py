#!/usr/bin/env python3
"""
修复后的1688图片上传接口
- 修正签名算法
- 处理Base64编码的特殊要求
"""

import os
import sys
import json
import base64
import requests
import hmac
import hashlib

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.auth import get_access_token, sign_request_hmac_sha1
from scripts.image_utils import compress_image_if_needed, cleanup_temp_file

def fixed_sign_request_hmac_sha1_for_upload(url_path, upload_param_json, access_token, app_secret):
    """
    修复后的图片上传签名算法
    根据1688官方文档，图片上传接口的签名需要特殊处理
    """
    # 图片上传接口的签名格式：url_path + uploadImageParam + access_token
    sign_str = url_path + upload_param_json + access_token
    signature = hmac.new(
        app_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha1
    ).hexdigest().upper()
    return signature

def fixed_upload_image(image_path, app_key, app_secret, token):
    """修复后的图片上传函数"""
    # 检查并压缩图片（如果需要）
    compressed_path, was_compressed = compress_image_if_needed(image_path, max_size_kb=300)
    
    try:
        # 读取（可能已压缩的）图片并转换为base64
        with open(compressed_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # 构造uploadImageParam JSON（不包含access_token）
        upload_params = {
            'imageBase64': base64_image
        }
        upload_param_json = json.dumps(upload_params, separators=(',', ':'))
        
        # 构造请求参数
        params = {
            'uploadImageParam': upload_param_json,
            'access_token': token
        }
        
        # 使用修复后的签名算法
        url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.image.upload/{app_key}"
        sign = fixed_sign_request_hmac_sha1_for_upload(url_path, upload_param_json, token, app_secret)
        params['_aop_signature'] = sign
        
        # 发送请求
        url = f"https://gw.open.1688.com/openapi/{url_path}"
        response = requests.post(url, data=params, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Upload failed with status {response.status_code}: {response.text}")
            
        result = response.json()
        
        # 检查响应中是否有imageId
        if 'result' in result and isinstance(result['result'], str):
            return result['result']
        else:
            raise Exception(f"Failed to get imageId from upload response: {result}")
            
    finally:
        # 清理临时文件
        if was_compressed and os.path.exists(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 fixed_image_upload.py <image_path> <app_key> <app_secret> <access_token>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    app_key = sys.argv[2]
    app_secret = sys.argv[3]
    token = sys.argv[4]
    
    try:
        image_id = fixed_upload_image(image_path, app_key, app_secret, token)
        print(json.dumps({"imageId": image_id}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)
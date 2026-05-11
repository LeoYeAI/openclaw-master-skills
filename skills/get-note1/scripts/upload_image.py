#!/usr/bin/env python3
"""
Get笔记图片上传脚本

用法:
    python upload_image.py <图片路径> [--api-key KEY]
    
示例:
    python upload_image.py /path/to/image.jpg
    python upload_image.py /path/to/image.jpg --api-key gk_live_xxx
    
环境变量:
    GETNOTE_API_KEY - API Key（如未提供 --api-key 则使用此变量）
"""

import os
import sys
import argparse
import mimetypes
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库")
    print("运行: pip install requests")
    sys.exit(1)


BASE_URL = "https://openapi.biji.com/open/api/v1/resource"


def get_mime_type(file_path: str) -> str:
    """获取文件 MIME 类型"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "image/jpeg"


def upload_image(image_path: str, api_key: str) -> str:
    """
    上传图片到 Get笔记 OSS
    
    Args:
        image_path: 本地图片路径
        api_key: Get笔记 API Key
        
    Returns:
        上传后的访问 URL
    """
    # 检查文件
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"文件不存在: {image_path}")
    
    mime_type = get_mime_type(image_path)
    headers = {"Authorization": api_key}
    
    # 步骤 1: 获取上传凭证
    print("[1/3] 获取上传凭证...")
    
    resp = requests.get(
        f"{BASE_URL}/image/upload_token",
        params={"count": 1, "mime_type": mime_type},
        headers=headers
    )
    resp.raise_for_status()
    data = resp.json()
    
    if not data.get("success"):
        error = data.get("error", {})
        raise Exception(f"获取凭证失败: {error.get('message', 'Unknown error')}")
    
    tokens = data["data"]["tokens"]
    if not tokens:
        raise Exception("获取凭证失败: tokens 为空")
    
    token = tokens[0]
    host = token["host"]
    object_key = token["object_key"]
    policy = token.get("policy", "")
    signature = token.get("signature", "")
    callback = token.get("callback", "")
    access_url = token["access_url"]
    
    print("✓ 凭证获取成功")
    
    # 步骤 2: 上传到 OSS（multipart form）
    print("[2/3] 上传图片到 OSS...")
    
    file_name = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        form_data = {
            "key": object_key,
            "policy": policy,
            "signature": signature,
            "callback": callback,
            "Content-Type": mime_type,
        }
        files = {"file": (file_name, f, mime_type)}
        resp = requests.post(host, data=form_data, files=files)
    
    if resp.status_code not in (200, 204):
        raise Exception(f"上传失败: HTTP {resp.status_code}")
    
    print("✓ 上传成功")
    
    # 步骤 3: 返回访问 URL
    print("[3/3] 完成")
    
    return access_url


def main():
    parser = argparse.ArgumentParser(
        description="Get笔记图片上传脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    %(prog)s /path/to/image.jpg
    %(prog)s /path/to/image.jpg --api-key gk_live_xxx
    
环境变量:
    GETNOTE_API_KEY - API Key
        """
    )
    parser.add_argument("image_path", help="本地图片路径")
    parser.add_argument("--api-key", "-k", help="API Key（或设置 GETNOTE_API_KEY 环境变量）")
    
    args = parser.parse_args()
    
    # 获取 API Key
    api_key = args.api_key or os.environ.get("GETNOTE_API_KEY")
    if not api_key:
        print("错误: 请提供 API Key（--api-key 参数或 GETNOTE_API_KEY 环境变量）")
        sys.exit(1)
    
    try:
        image_url = upload_image(args.image_path, api_key)
        
        print()
        print("=" * 40)
        print("图片上传成功！")
        print("=" * 40)
        print()
        print(f"访问 URL: {image_url}")
        print()
        print("💡 创建图片笔记:")
        print(f'   curl -X POST "https://openapi.biji.com/open/api/v1/resource/note/save?task_id=..."')
        print(f'     -H "Authorization: $GETNOTE_API_KEY"')
        print(f'     -H "Content-Type: application/json"')
        print(f'     -d \'{{"type":"img_text","image_urls":["{image_url}"]}}\'')
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

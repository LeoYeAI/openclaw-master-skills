#!/usr/bin/env python3
"""上传图片/视频/音频文件到 VoooAI：POST /api/upload（multipart/form-data）"""

import argparse
import json
import mimetypes
import os
import sys
import uuid
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from _common import BASE_URL, validate_api_path, json_output, error_exit, _ensure_access_key

# 允许的 MIME 类型前缀
ALLOWED_PREFIXES = ("image/", "video/", "audio/")


def upload_file(file_path: str) -> dict:
    """
    上传本地文件到 VoooAI 平台。
    
    Args:
        file_path: 本地文件路径
    
    Returns:
        上传结果字典，包含 url 和 file_type
    """
    if not os.path.isfile(file_path):
        error_exit(f"文件不存在: {file_path}")
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    max_size_mb = 200  # 视频最大 200MB
    if file_size > max_size_mb * 1024 * 1024:
        error_exit(f"文件过大: {file_size / 1024 / 1024:.1f}MB（最大 {max_size_mb}MB）")
    
    # 检查 MIME 类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and not any(mime_type.startswith(p) for p in ALLOWED_PREFIXES):
        error_exit(f"不支持的文件类型: {mime_type}，仅支持图片、视频和音频")
    
    # 构建 multipart/form-data 请求体
    boundary = f"----VoooAIUpload{uuid.uuid4().hex}"
    filename = os.path.basename(file_path)
    content_type = mime_type or "application/octet-stream"
    
    body_parts = []
    
    # file 字段
    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    )
    body_parts.append(f"Content-Type: {content_type}\r\n\r\n".encode())
    with open(file_path, "rb") as f:
        body_parts.append(f.read())
    body_parts.append(b"\r\n")
    
    # 结束边界
    body_parts.append(f"--{boundary}--\r\n".encode())
    
    data = b"".join(body_parts)
    
    # 校验路径（/api/upload）
    api_path = "/api/upload"
    validate_api_path(api_path)
    
    # 获取 AccessKey
    access_key = _ensure_access_key()
    
    url = f"{BASE_URL.rstrip('/')}{api_path}"
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {access_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        # 上传大文件可能需要更长时间
        timeout = 180 if file_size > 50 * 1024 * 1024 else 120
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            
            # 处理响应
            if result.get("success") is False:
                error_exit(result.get("message", "上传失败"))
            
            # 提取 URL（兼容不同响应格式）
            file_url = result.get("url") or result.get("data", {}).get("url", "")
            
            return {
                "url": file_url,
                "file_type": mime_type or "unknown",
                "file_name": filename,
                "file_size_bytes": file_size,
            }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        print(f"API 错误 {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"网络错误: {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="上传图片、视频或音频文件到 VoooAI 平台",
        epilog="""
环境变量:
  VOOOAI_ACCESS_KEY  必填，Bearer 鉴权
  VOOOAI_BASE_URL    可选，默认 https://voooai.com

支持的文件类型:
  - 图片: jpg, jpeg, png, webp, gif
  - 视频: mp4, mov, avi, mkv, webm
  - 音频: mp3, wav, flac, m4a, ogg

文件大小限制:
  - 图片: 最大 10MB
  - 视频: 最大 200MB
  - 音频: 最大 15MB

示例:
  # 上传参考图片
  python3 upload_file.py /path/to/image.png

  # 上传参考视频
  python3 upload_file.py /path/to/video.mp4

  # 上传参考音频
  python3 upload_file.py /path/to/audio.mp3
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="要上传的图片、视频或音频文件路径",
    )
    args = parser.parse_args()

    result = upload_file(args.file)
    
    if not result.get("url"):
        error_exit("上传成功但未返回文件 URL")
    
    out = {
        "file_url": result["url"],
        "file_type": result["file_type"],
        "file_name": result["file_name"],
        "file_size_bytes": result["file_size_bytes"],
    }
    json_output(out)


if __name__ == "__main__":
    main()

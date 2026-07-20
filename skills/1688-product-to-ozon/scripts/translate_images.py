#!/usr/bin/env python3
"""
图片翻译脚本 — 调用 AlphaShop 图片翻译PRO接口，将图片中的文字翻译为俄语。

用法:
  python translate_images.py --image-url <URL1> [<URL2> ...]

环境变量:
  ALPHASHOP_ACCESS_KEY  AlphaShop Access Key
  ALPHASHOP_SECRET_KEY  AlphaShop Secret Key
"""
import sys
import os
import json
import time
import argparse
import requests
import jwt

API_URL = "https://api.alphashop.cn/ai.image.translateImagePro/1.0"


def get_token():
    """生成 AlphaShop JWT 认证 token"""
    ak = os.environ.get("ALPHASHOP_ACCESS_KEY", "").strip()
    sk = os.environ.get("ALPHASHOP_SECRET_KEY", "").strip()
    if not ak or not sk:
        print("Error: Set ALPHASHOP_ACCESS_KEY and ALPHASHOP_SECRET_KEY env vars.", file=sys.stderr)
        sys.exit(1)
    now = int(time.time())
    token = jwt.encode(
        {"iss": ak, "exp": now + 1800, "nbf": now - 5},
        sk,
        algorithm="HS256",
        headers={"alg": "HS256"},
    )
    return token if isinstance(token, str) else token.decode("utf-8")


def translate_image(image_url: str) -> dict:
    """调用图片翻译PRO接口，源语种auto，目标语种ru"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
    }
    body = {
        "imageUrl": image_url,
        "sourceLanguage": "auto",
        "targetLanguage": "ru",
    }
    try:
        r = requests.post(API_URL, json=body, headers=headers, timeout=120)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "originalUrl": image_url}
    except Exception as e:
        return {"error": str(e), "originalUrl": image_url}


def main():
    parser = argparse.ArgumentParser(description="AlphaShop 图片翻译PRO（→俄语）")
    parser.add_argument("--image-url", nargs="+", required=True, help="图片URL（支持多个）")
    args = parser.parse_args()

    results = []
    for url in args.image_url:
        result = translate_image(url)
        results.append({"originalUrl": url, "response": result})

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

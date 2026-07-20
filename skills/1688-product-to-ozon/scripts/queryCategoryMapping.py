#!/usr/bin/env python3
"""
查询1688的类目映射到Ozon的类目的情况
通过 AlphaShop API 接口查询

环境变量:
  ALPHASHOP_ACCESS_KEY  AlphaShop Access Key
  ALPHASHOP_SECRET_KEY  AlphaShop Secret Key
"""

import json
import os
import sys
import time

import jwt
import requests

# === 常量 ===
API_URL = "https://api.alphashop.cn/alphashop.openclaw.offer.cate.ozon.query/1.0"


def log(msg: str, level: str = "INFO"):
    print(f"[{level}] {msg}")


def error_exit(msg: str):
    log(msg, "ERROR")
    sys.exit(1)


def get_token():
    """生成 AlphaShop JWT 认证 token"""
    ak = os.environ.get("ALPHASHOP_ACCESS_KEY", "").strip()
    sk = os.environ.get("ALPHASHOP_SECRET_KEY", "").strip()
    if not ak or not sk:
        error_exit("请设置环境变量 ALPHASHOP_ACCESS_KEY 和 ALPHASHOP_SECRET_KEY")
    now = int(time.time())
    token = jwt.encode(
        {"iss": ak, "exp": now + 1800, "nbf": now - 5},
        sk,
        algorithm="HS256",
        headers={"alg": "HS256"},
    )
    return token if isinstance(token, str) else token.decode("utf-8")


def query_category_mapping(category_id: str) -> dict:
    """调用 AlphaShop 接口查询 Ozon 类目映射"""
    log(f"查询类目映射: 1688 categoryId={category_id}")
    try:
        resp = requests.post(
            API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {get_token()}",
            },
            json={"categoryId": str(category_id)},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        log(f"类目映射响应: {json.dumps(data, ensure_ascii=False)[:500]}")
        return data
    except Exception as e:
        error_exit(f"查询类目映射失败: {e}")


def main(category_id: str = None, **kwargs) -> str:
    """
    主入口函数 - OpenClaw SKILL 调用此函数

    Args:
        category_id: 1688商品的叶子类目ID（thirdCategoryId），数字格式

    Returns:
        str: JSON格式的处理结果字符串
    """
    if category_id is None:
        error_exit("类目数据为空")
    result = query_category_mapping(category_id)
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = main(sys.argv[1])
    else:
        error_exit("该1688商品数据无有效类目数据，执行失败")

    log(f"执行结果:{result}")

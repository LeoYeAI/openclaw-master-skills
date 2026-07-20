#!/usr/bin/env python3
"""
查询 Ozon 属性的字典可选值

支持两种模式：
  - 搜索模式：根据关键词搜索匹配的字典值
  - 列表模式：列出所有可选值

用法:
  # 搜索模式 - 根据关键词搜索
  python queryDictionaryValues.py \
    --attribute_id 85 \
    --description_category_id 17028922 \
    --type_id 91565 \
    --search "Нет бренда"

  # 列表模式 - 列出所有可选值
  python queryDictionaryValues.py \
    --attribute_id 85 \
    --description_category_id 17028922 \
    --type_id 91565 \
    --limit 50
"""

import os
import sys
import json
import argparse

import requests

OZON_BASE_URL = "https://api-seller.ozon.ru"
SEARCH_URL = f"{OZON_BASE_URL}/v1/description-category/attribute/values/search"
LIST_URL = f"{OZON_BASE_URL}/v1/description-category/attribute/values"


def log(msg: str, level: str = "INFO"):
    print(f"[{level}] {msg}", file=sys.stderr)


def error_exit(msg: str):
    log(msg, "ERROR")
    sys.exit(1)


def get_ozon_api_key():
    key = os.environ.get("OZON_API_KEY", "").strip()
    if not key:
        error_exit("OZON_API_KEY not set")
    return key


def get_ozon_client_id():
    key = os.environ.get("OZON_CLIENT_ID", "").strip()
    if not key:
        error_exit("OZON_CLIENT_ID not set")
    return key


def get_headers(client_id: str, api_key: str) -> dict:
    return {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json",
    }


def search_values(client_id, api_key, attribute_id, desc_cat_id, type_id, search, limit):
    """搜索模式：根据关键词搜索字典值"""
    log(f"搜索字典值: attribute_id={attribute_id}, search='{search}'")
    resp = requests.post(
        SEARCH_URL,
        headers=get_headers(client_id, api_key),
        json={
            "attribute_id": attribute_id,
            "description_category_id": desc_cat_id,
            "type_id": type_id,
            "language": "DEFAULT",
            "limit": limit,
            "value": search,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("result", [])


def list_values(client_id, api_key, attribute_id, desc_cat_id, type_id, limit):
    """列表模式：列出所有可选值"""
    log(f"列出字典值: attribute_id={attribute_id}")
    resp = requests.post(
        LIST_URL,
        headers=get_headers(client_id, api_key),
        json={
            "attribute_id": attribute_id,
            "description_category_id": desc_cat_id,
            "type_id": type_id,
            "language": "DEFAULT",
            "last_value_id": 0,
            "limit": limit,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("result", [])


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 属性的字典可选值")
    parser.add_argument("--attribute_id", type=int, required=True, help="属性ID")
    parser.add_argument("--description_category_id", type=int, required=True, help="描述类目ID")
    parser.add_argument("--type_id", type=int, required=True, help="类型ID")
    parser.add_argument("--search", type=str, default=None, help="搜索关键词（不传则使用列表模式）")
    parser.add_argument("--limit", type=int, default=50, help="返回数量限制（默认50）")
    args = parser.parse_args()

    api_key = get_ozon_api_key()
    client_id = get_ozon_client_id()

    try:
        if args.search:
            result = search_values(
                client_id, api_key,
                args.attribute_id, args.description_category_id, args.type_id,
                args.search, args.limit,
            )
        else:
            result = list_values(
                client_id, api_key,
                args.attribute_id, args.description_category_id, args.type_id,
                args.limit,
            )
    except requests.exceptions.HTTPError as e:
        error_body = getattr(e.response, "text", "")
        error_exit(f"查询字典值失败: {e}\n响应: {error_body}")
    except Exception as e:
        error_exit(f"查询字典值失败: {e}")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

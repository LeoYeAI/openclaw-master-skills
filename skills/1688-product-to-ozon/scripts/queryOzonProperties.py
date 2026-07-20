import os

import requests
import json

# !/usr/bin/env python3
"""
查询指定的Ozon类目属性的要求

用法:
  python queryOzonProperties.py \
    --external_category_id 你需要查询的Ozon的类目ID \

流程:
  1. 解析Ozon的类目
  2. 调用Ozon的接口获取Ozon类目的属性要求
  3. 返回查询结果
"""

import sys

# === 常量 ===

OZON_BASE_URL = "https://api-seller.ozon.ru"
OZON_CATEGORY_ATTRIBUTES_URL = f"{OZON_BASE_URL}/v1/description-category/attribute"

def log(msg: str, level: str = "INFO"):
    print(f"[{level}] {msg}", file=sys.stderr)


def error_exit(msg: str):
    log(msg, "ERROR")
    sys.exit(1)


def get_ozon_api_key():
    """Read API key from environment variable OZON_API_KEY."""
    key = os.environ.get("OZON_API_KEY", "").strip()
    if not key:
        print("Error: OZON_API_KEY not set. Configure it in OpenClaw:\n"
              '  skills.entries.1688-to-Ozon-Product-category-Converter.apiKey or\n'
              '  skills.entries.1688-to-Ozon-Product-category-Converter.env.OZON_API_KEY',
              file=sys.stderr)
        sys.exit(1)
    return key


def get_ozon_client_id():
    """Read API key from environment variable OZON_CLIENT_ID."""
    key = os.environ.get("OZON_CLIENT_ID", "").strip()
    if not key:
        print("Error: OZON_CLIENT_ID not set. Configure it in OpenClaw:\n"
              '  skills.entries.1688-to-Ozon-Product-category-Converter.clientId or\n'
              '  skills.entries.1688-to-Ozon-Product-category-Converter.env.OZON_CLIENT_ID',
              file=sys.stderr)
        sys.exit(1)
    return key


# === Step 2: 获取Ozon类目属性 ===
def get_ozon_category_attributes(client_id: str, api_key: str, desc_cat_id: int, type_id: int) -> list:
    """获取Ozon类目下的属性要求"""
    log(f"获取Ozon类目属性: description_category_id={desc_cat_id}, type_id={type_id}")
    try:
        resp = requests.post(
            OZON_CATEGORY_ATTRIBUTES_URL,
            headers={
                "Client-Id": client_id,
                "Api-Key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "description_category_id": desc_cat_id,
                "language": "ZH_HANS",
                "type_id": type_id,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("result", [])
    except requests.exceptions.HTTPError as e:
        error_body = getattr(e.response, 'text', '')
        error_exit(f"获取Ozon类目属性失败: {e}\n响应: {error_body}")
    except Exception as e:
        error_exit(f"获取Ozon类目属性失败: {e}")


def main(external_category_id: str = None) -> str:
    """
    主入口函数 - OpenClaw SKILL 调用此函数

    OpenClaw 框架会将大模型提取的作为参数传入。

    Args:
        external_category_id: 类目数据，通过1688的商品类目映射出来的Ozon类目列表，例如："100,329023"

    Returns:
        str: JSON格式的处理结果字符串（OpenClaw要求返回字符串）
    """
    if external_category_id is None:
        error_exit("类目数据为空")

    category_id_1, category_id_2 = external_category_id.split(",")

    ozon_api_key = get_ozon_api_key()
    ozon_client_id = get_ozon_client_id()
    result = get_ozon_category_attributes(ozon_client_id, ozon_api_key, category_id_1, category_id_2)
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 命令行传参
        result = main(sys.argv[1])
    else:
        # 使用测试数据
        error_exit("该商品无有效的Ozon类目")

    log(f"执行结果:{result}")

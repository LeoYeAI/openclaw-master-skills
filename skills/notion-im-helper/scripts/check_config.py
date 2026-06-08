# -*- coding: utf-8 -*-
"""
配置检查脚本
验证环境变量是否已配置，并测试 API 连通性。
"""

import sys
import os

# 将脚本所在目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    get_client,
    get_parent_page_id,
    output_ok,
    output_error,
    log_debug,
    NOTION_API_KEY,
    NOTION_PARENT_PAGE_ID,
    NOTION_QUOTES_PAGE_ID,
)
from notion_helper import APIResponseError


def main():
    # 1. 检查环境变量
    if not check_required_config():
        return

    # 2. 测试 API 连通性
    try:
        client = get_client()
        page_id = get_parent_page_id()

        # 尝试读取页面信息（最轻量的 API 调用）
        log_debug(f"测试连接页面: {page_id}")
        result = client.blocks.children.list(block_id=page_id, page_size=1)

        # 输出配置状态
        status_parts = [
            f"API 连接正常",
            f"目标页面已授权",
        ]
        if NOTION_QUOTES_PAGE_ID:
            # 同时检查摘抄本页面
            try:
                from notion_helper import get_quotes_page_id
                quotes_id = get_quotes_page_id()
                client.blocks.children.list(block_id=quotes_id, page_size=1)
                status_parts.append("摘抄本页面已授权")
            except Exception:
                status_parts.append("摘抄本页面未授权或 ID 无效")
        else:
            status_parts.append("摘抄本未配置（可选）")

        output_ok("，".join(status_parts))

    except APIResponseError as e:
        log_debug(f"API 错误: {e.status} {e.code}")
        if e.status == 401:
            output_error("AUTH", "API 密钥无效，请检查 NOTION_API_KEY")
        elif e.status == 403 or e.status == 404:
            output_error("AUTH", "页面未授权，请在 Notion 中 Connect to Integration")
        else:
            output_error("API", f"HTTP {e.status}")
    except Exception as e:
        log_debug(f"连接错误: {type(e).__name__}: {e}")
        if "connect" in str(e).lower() or "timeout" in str(e).lower():
            output_error("NETWORK", "无法连接 Notion API")
        else:
            output_error("UNKNOWN", str(e))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
搜索笔记
从 Notion 搜索包含关键词的页面，返回格式化的 JSON 结果。

用法：
    python search_notes.py "关键词"
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    search_pages,
    output_ok,
    output_error,
    log_debug,
)


def extract_page_info(page: dict) -> dict:
    """从 Notion 页面对象中提取关键信息"""
    # 提取标题
    title = ""
    properties = page.get("properties", {})
    for prop_name, prop_value in properties.items():
        if prop_value.get("type") == "title":
            title_items = prop_value.get("title", [])
            title = "".join(item.get("plain_text", "") for item in title_items)
            break

    # 如果 properties 中没有 title，尝试从其他字段获取
    if not title:
        # 对于 child_page 类型的结果
        if page.get("type") == "child_page":
            title = page.get("child_page", {}).get("title", "无标题")

    # 构建 URL
    page_id = page.get("id", "").replace("-", "")
    url = f"https://www.notion.so/{page_id}" if page_id else ""

    # 提取最后编辑时间
    last_edited = page.get("last_edited_time", "")

    return {
        "title": title or "无标题",
        "url": url,
        "last_edited": last_edited,
    }


def main():
    if not check_required_config():
        return

    args = sys.argv[1:]
    if not args:
        output_error("ARGS", "缺少搜索关键词")
        return

    query = " ".join(args)
    log_debug(f"搜索: {query}")

    results = search_pages(query, page_size=10)

    if not results:
        output_ok(f"未找到与「{query}」相关的内容")
        return

    # 格式化结果
    formatted = []
    for page in results:
        info = extract_page_info(page)
        formatted.append(info)

    # 输出 JSON 数组
    print(f"OK|{json.dumps(formatted, ensure_ascii=False)}", flush=True)


if __name__ == "__main__":
    main()

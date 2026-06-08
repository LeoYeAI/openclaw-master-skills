# -*- coding: utf-8 -*-
"""
随机摘抄
从摘抄本页面中随机获取内容（Toggle 块）。

用法：
    python daily_quote.py                   # 随机 1 条
    python daily_quote.py --count 3          # 随机 3 条
    python daily_quote.py --book "原子习惯"   # 按书名搜索
"""

import sys
import os
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    check_quotes_config,
    list_all_blocks,
    get_quotes_page_id,
    output_ok,
    output_error,
    log_debug,
)


def extract_toggle_text(block: dict) -> str:
    """提取 Toggle 块的标题文本"""
    toggle_data = block.get("toggle", {})
    rich_text = toggle_data.get("rich_text", [])
    return "".join(item.get("plain_text", "") for item in rich_text)


def extract_block_text(block: dict) -> str:
    """从任意块中提取文本"""
    block_type = block.get("type", "")
    type_data = block.get(block_type, {})
    rich_text = type_data.get("rich_text", [])
    return "".join(item.get("plain_text", "") for item in rich_text)


def main():
    if not check_required_config():
        return
    if not check_quotes_config():
        return

    # 解析参数
    args = sys.argv[1:]
    count = 1
    book_filter = None

    i = 0
    while i < len(args):
        if args[i] == "--count" and i + 1 < len(args):
            try:
                count = int(args[i + 1])
                count = max(1, min(count, 10))  # 限制 1-10 条
            except ValueError:
                count = 1
            i += 2
        elif args[i] == "--book" and i + 1 < len(args):
            book_filter = args[i + 1]
            i += 2
        else:
            # 兼容直接传数字或书名的情况
            if args[i].isdigit():
                count = int(args[i])
                count = max(1, min(count, 10))
            else:
                book_filter = args[i]
            i += 1

    quotes_page_id = get_quotes_page_id()
    log_debug(f"从摘抄本获取内容: page_id={quotes_page_id}, count={count}, book={book_filter}")

    all_blocks = list_all_blocks(page_id=quotes_page_id)

    # 收集所有 Toggle 块（摘抄条目）
    quotes = []
    for block in all_blocks:
        if block.get("type") == "toggle":
            text = extract_toggle_text(block)
            if text:
                quotes.append({
                    "text": text,
                    "id": block.get("id", ""),
                })
        # 也支持段落和引用格式的摘抄
        elif block.get("type") in ("paragraph", "quote"):
            text = extract_block_text(block)
            if text and len(text) > 5:  # 过滤太短的内容
                quotes.append({
                    "text": text,
                    "id": block.get("id", ""),
                })

    if not quotes:
        output_ok("摘抄本还是空的，快去添加一些摘抄吧 📖")
        return

    # 按书名过滤
    if book_filter:
        filtered = [q for q in quotes if book_filter in q["text"]]
        if not filtered:
            output_ok(f"没有找到与「{book_filter}」相关的摘抄")
            return
        quotes = filtered

    # 随机选取
    count = min(count, len(quotes))
    selected = random.sample(quotes, count)

    # 输出
    result = {
        "count": len(selected),
        "total": len(quotes),
        "quotes": [q["text"] for q in selected],
    }
    print(f"OK|{json.dumps(result, ensure_ascii=False)}", flush=True)


if __name__ == "__main__":
    main()

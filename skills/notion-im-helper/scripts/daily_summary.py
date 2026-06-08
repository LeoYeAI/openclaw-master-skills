# -*- coding: utf-8 -*-
"""
每日汇总
读取目标页面今天的所有内容块，整理成格式化的日报。

用法：
    python daily_summary.py
"""

import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    list_all_blocks,
    get_today_str,
    output_ok,
    output_error,
    log_debug,
)


def extract_block_text(block: dict) -> str:
    """从内容块中提取纯文本"""
    block_type = block.get("type", "")
    type_data = block.get(block_type, {})

    # 大部分块类型都有 rich_text
    rich_text = type_data.get("rich_text", [])
    if rich_text:
        return "".join(item.get("plain_text", "") for item in rich_text)

    return ""


def format_block_for_summary(block: dict) -> dict:
    """将内容块格式化为日报条目"""
    block_type = block.get("type", "")
    text = extract_block_text(block)
    created_time = block.get("created_time", "")

    # 解析创建时间
    time_str = ""
    if created_time:
        try:
            dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
            local_dt = dt.astimezone()
            time_str = local_dt.strftime("%H:%M")
        except (ValueError, TypeError):
            pass

    type_labels = {
        "paragraph": "📝",
        "to_do": "✅" if block.get("to_do", {}).get("checked") else "☐",
        "heading_1": "📌 H1",
        "heading_2": "📌 H2",
        "heading_3": "📌 H3",
        "quote": "💬",
        "bulleted_list_item": "•",
        "numbered_list_item": "#",
        "toggle": "📂",
        "divider": "---",
    }

    label = type_labels.get(block_type, "📝")

    return {
        "type": block_type,
        "label": label,
        "text": text,
        "time": time_str,
    }


def main():
    if not check_required_config():
        return

    today = get_today_str()
    log_debug(f"获取今日（{today}）记录")

    all_blocks = list_all_blocks()

    # 过滤今天的内容块
    today_blocks = []
    for block in all_blocks:
        created_time = block.get("created_time", "")
        if not created_time:
            continue
        try:
            dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
            local_dt = dt.astimezone()
            if local_dt.strftime("%Y-%m-%d") == today:
                # 跳过分割线
                if block.get("type") == "divider":
                    continue
                formatted = format_block_for_summary(block)
                if formatted["text"]:  # 只保留有内容的块
                    today_blocks.append(formatted)
        except (ValueError, TypeError):
            continue

    if not today_blocks:
        output_ok(f"今天（{today}）暂无记录")
        return

    # 输出 JSON
    result = {
        "date": today,
        "count": len(today_blocks),
        "items": today_blocks,
    }
    print(f"OK|{json.dumps(result, ensure_ascii=False)}", flush=True)


if __name__ == "__main__":
    main()

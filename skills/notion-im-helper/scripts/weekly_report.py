# -*- coding: utf-8 -*-
"""
周报生成
收集本周（周一到当前）目标页面的所有内容块，按日期分组整理。

用法：
    python weekly_report.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    list_all_blocks,
    output_ok,
    output_error,
    log_debug,
)


def get_week_range() -> tuple:
    """获取本周的起止日期（周一 ~ 今天）"""
    from datetime import timezone
    today = datetime.now(timezone.utc)
    # 计算本周一
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return monday, today


def extract_block_text(block: dict) -> str:
    """从内容块中提取纯文本"""
    block_type = block.get("type", "")
    type_data = block.get(block_type, {})
    rich_text = type_data.get("rich_text", [])
    if rich_text:
        return "".join(item.get("plain_text", "") for item in rich_text)
    return ""


def format_block_entry(block: dict) -> dict:
    """格式化单个内容块"""
    block_type = block.get("type", "")
    text = extract_block_text(block)
    created_time = block.get("created_time", "")

    type_labels = {
        "paragraph": "[P]",
        "to_do": "[x]" if block.get("to_do", {}).get("checked") else "[ ]",
        "heading_1": "[H1]",
        "heading_2": "[H2]",
        "heading_3": "[H3]",
        "quote": "[>]",
        "bulleted_list_item": "[-]",
        "numbered_list_item": "[#]",
        "toggle": "[T]",
    }

    return {
        "type": block_type,
        "label": type_labels.get(block_type, "📝"),
        "text": text,
        "created_time": created_time,
    }


def main():
    if not check_required_config():
        return

    monday, today = get_week_range()
    log_debug(f"生成周报: {monday.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}")

    all_blocks = list_all_blocks()

    # 按日期分组
    daily_groups = {}
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    for block in all_blocks:
        created_time = block.get("created_time", "")
        if not created_time:
            continue

        try:
            dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
            local_dt = dt.astimezone()
        except (ValueError, TypeError):
            continue

        # 检查是否在本周范围内
        if local_dt < monday or local_dt > today:
            continue

        # 跳过分割线
        if block.get("type") == "divider":
            continue

        text = extract_block_text(block)
        if not text:
            continue

        date_key = local_dt.strftime("%Y-%m-%d")
        weekday = weekday_names[local_dt.weekday()]
        display_date = f"{date_key} {weekday}"

        if display_date not in daily_groups:
            daily_groups[display_date] = []

        daily_groups[display_date].append(format_block_entry(block))

    if not daily_groups:
        output_ok(f"本周（{monday.strftime('%m/%d')}~{today.strftime('%m/%d')}）暂无记录")
        return

    # 统计
    total_items = sum(len(items) for items in daily_groups.values())
    todo_count = 0
    done_count = 0
    for items in daily_groups.values():
        for item in items:
            if item["type"] == "to_do":
                if item["label"] == "[x]":
                    done_count += 1
                else:
                    todo_count += 1

    result = {
        "week_range": f"{monday.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}",
        "total_items": total_items,
        "todo_pending": todo_count,
        "todo_done": done_count,
        "days": daily_groups,
    }

    # 输出 JSON，避免 Windows 编码问题
    json_str = json.dumps(result, ensure_ascii=True)
    print(f"OK|{json_str}", flush=True)


if __name__ == "__main__":
    main()

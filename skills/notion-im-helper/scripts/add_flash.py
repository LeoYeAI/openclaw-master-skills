# -*- coding: utf-8 -*-
"""
添加闪念笔记
输出格式：
  第一行（段落块）：⚡ 时间戳  📌Claw名 #标签 【项目】
  第二行（段落块）：内容正文
  第三行：分割线块

用法：
    python add_flash.py "内容" [--tag TAG] [--project PROJECT] [--claw CLAW]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    make_paragraph_block,
    make_divider_block,
    make_rich_text,
    append_blocks,
    get_timestamp,
    output_ok,
    output_error,
    parse_metadata_args,
    build_metadata_suffix,
)


def main():
    if not check_required_config():
        return

    args = sys.argv[1:]
    remaining, tag, project, claw = parse_metadata_args(args)

    if not remaining:
        output_error("ARGS", "缺少闪念内容")
        return

    content = " ".join(remaining)
    timestamp = get_timestamp()

    # 构建元数据后缀（Claw来源 + 标签 + 项目）
    meta_suffix = build_metadata_suffix(tag, project, claw)

    # ── 第一行：时间戳 + 元数据 ──
    time_line_rich_text = [
        {
            "type": "text",
            "text": {"content": f"⚡ {timestamp}"},
            "annotations": {"color": "gray"},
        },
    ]
    if meta_suffix:
        time_line_rich_text.append({
            "type": "text",
            "text": {"content": f"  {meta_suffix}"},
            "annotations": {"color": "blue", "italic": True},
        })

    time_block = {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": time_line_rich_text,
        },
    }

    # ── 第二行：内容正文 ──
    content_block = {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": content},
                },
            ],
        },
    }

    # ── 第三行：分割线 ──
    blocks = [time_block, content_block, make_divider_block()]

    append_blocks(blocks)
    output_ok(f"已添加闪念：{content}")


if __name__ == "__main__":
    main()

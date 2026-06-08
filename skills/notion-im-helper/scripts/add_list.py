# -*- coding: utf-8 -*-
"""
添加无序/有序列表

用法：
    python add_list.py bullet "item1" "item2" "item3"
    python add_list.py number "item1" "item2" "item3"
    python add_list.py bullet "item1" --tag TAG --project PROJECT
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    make_bulleted_list_block,
    make_numbered_list_block,
    append_blocks,
    output_ok,
    output_error,
    parse_metadata_args,
    build_metadata_suffix,
)


def main():
    if not check_required_config():
        return

    args = sys.argv[1:]

    if len(args) < 2:
        output_error("ARGS", "用法: add_list.py <bullet|number> <item1> [item2] ...")
        return

    list_type = args[0].lower()
    remaining_args = args[1:]
    remaining, tag, project, _claw = parse_metadata_args(remaining_args)

    if list_type not in ("bullet", "number"):
        output_error("ARGS", f"列表类型必须是 bullet 或 number，收到: {list_type}")
        return

    if not remaining:
        output_error("ARGS", "缺少列表项")
        return

    meta_suffix = build_metadata_suffix(tag, project)

    blocks = []
    for item in remaining:
        text = item.strip()
        if not text:
            continue
        if meta_suffix:
            text += f"  {meta_suffix}"
        if list_type == "bullet":
            blocks.append(make_bulleted_list_block(text))
        else:
            blocks.append(make_numbered_list_block(text))

    if not blocks:
        output_error("ARGS", "缺少列表项")
        return

    append_blocks(blocks)
    type_name = "无序列表" if list_type == "bullet" else "有序列表"
    output_ok(f"已添加 {len(blocks)} 条{type_name}项")


if __name__ == "__main__":
    main()

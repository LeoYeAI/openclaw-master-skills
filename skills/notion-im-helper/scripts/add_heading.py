# -*- coding: utf-8 -*-
"""
添加标题
支持 H1/H2/H3 三级标题。

用法：
    python add_heading.py 1 "一级标题"
    python add_heading.py 2 "二级标题"
    python add_heading.py 3 "三级标题"
    python add_heading.py 1 "标题" --tag TAG --project PROJECT
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    make_heading_block,
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
        output_error("ARGS", "用法: add_heading.py <level:1|2|3> <text>")
        return

    # 第一个参数是标题级别
    level_str = args[0]
    remaining_args = args[1:]
    remaining, tag, project, _claw = parse_metadata_args(remaining_args)

    try:
        level = int(level_str)
        if level not in (1, 2, 3):
            raise ValueError()
    except ValueError:
        output_error("ARGS", f"标题级别必须是 1、2 或 3，收到: {level_str}")
        return

    if not remaining:
        output_error("ARGS", "缺少标题文字")
        return

    text = " ".join(remaining)
    meta_suffix = build_metadata_suffix(tag, project)
    if meta_suffix:
        text += f"  {meta_suffix}"

    blocks = [make_heading_block(level, text)]
    append_blocks(blocks)
    output_ok(f"已添加 H{level} 标题：{remaining[0]}")


if __name__ == "__main__":
    main()

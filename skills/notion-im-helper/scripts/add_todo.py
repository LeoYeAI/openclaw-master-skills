# -*- coding: utf-8 -*-
"""
添加待办事项
支持多条待办和已完成标记。

用法：
    python add_todo.py "任务1" "任务2" "任务3"
    python add_todo.py --done "已完成的任务"
    python add_todo.py "任务1" --tag TAG --project PROJECT
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    make_todo_block,
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

    # 检查 --done 标志
    checked = False
    if "--done" in args:
        checked = True
        args.remove("--done")

    remaining, tag, project, _claw = parse_metadata_args(args)

    if not remaining:
        output_error("ARGS", "缺少待办内容")
        return

    meta_suffix = build_metadata_suffix(tag, project)

    # 每个参数创建一个待办块
    blocks = []
    for item in remaining:
        text = item.strip()
        if not text:
            continue
        if meta_suffix:
            text += f"  {meta_suffix}"
        blocks.append(make_todo_block(text, checked=checked))

    if not blocks:
        output_error("ARGS", "缺少待办内容")
        return

    append_blocks(blocks)

    status = "已完成" if checked else "待办"
    output_ok(f"已添加 {len(blocks)} 条{status}")


if __name__ == "__main__":
    main()

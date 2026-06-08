# -*- coding: utf-8 -*-
"""
添加多级下拉列表（Toggle）
从 stdin 读取 JSON 结构，创建多级嵌套的 Toggle 块。

JSON 格式：
{
  "title": "标题",
  "children": [
    {"text": "第一级"},
    {"text": "第一级带子项", "children": [
      {"text": "第二级"},
      {"text": "第二级带子项", "children": [
        {"text": "第三级"}
      ]}
    ]}
  ]
}

用法：
    echo '{"title":"计划","children":[{"text":"第一步"}]}' | python add_toggle.py
    echo '...' | python add_toggle.py --tag TAG --project PROJECT
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    make_toggle_block,
    make_bulleted_list_block,
    append_blocks,
    output_ok,
    output_error,
    log_debug,
    parse_metadata_args,
    build_metadata_suffix,
)


def build_children_blocks(children_data: list) -> list:
    """
    递归构建嵌套的列表项。
    Notion API 限制：最多 3 级嵌套。
    """
    blocks = []
    for item in children_data:
        text = item.get("text", "").strip()
        if not text:
            continue
        sub_children = item.get("children", [])
        if sub_children:
            child_blocks = build_children_blocks(sub_children)
            blocks.append(make_bulleted_list_block(text, children=child_blocks))
        else:
            blocks.append(make_bulleted_list_block(text))
    return blocks


def main():
    if not check_required_config():
        return

    # 解析命令行参数中的 metadata
    args = sys.argv[1:]
    _, tag, project, _claw = parse_metadata_args(args)

    # 从 stdin 读取 JSON
    try:
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            output_error("ARGS", "缺少 JSON 输入（通过 stdin 传入）")
            return
        data = json.loads(raw_input)
    except json.JSONDecodeError as e:
        log_debug(f"JSON 解析错误: {e}")
        output_error("ARGS", "JSON 格式无效")
        return

    title = data.get("title", "").strip()
    if not title:
        output_error("ARGS", "缺少 title 字段")
        return

    meta_suffix = build_metadata_suffix(tag, project)
    if meta_suffix:
        title += f"  {meta_suffix}"

    children_data = data.get("children", [])

    # 构建子块
    children_blocks = build_children_blocks(children_data) if children_data else None

    # 创建 Toggle 块
    toggle = make_toggle_block(title, children=children_blocks)
    append_blocks([toggle])

    child_count = len(children_data) if children_data else 0
    output_ok(f"已添加下拉列表：{data.get('title', '')}（{child_count} 个子项）")


if __name__ == "__main__":
    main()

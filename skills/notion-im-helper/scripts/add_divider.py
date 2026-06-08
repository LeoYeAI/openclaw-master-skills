# -*- coding: utf-8 -*-
"""
添加分割线

用法：
    python add_divider.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notion_helper import (
    check_required_config,
    make_divider_block,
    append_blocks,
    output_ok,
)


def main():
    if not check_required_config():
        return

    blocks = [make_divider_block()]
    append_blocks(blocks)
    output_ok("已添加分割线")


if __name__ == "__main__":
    main()

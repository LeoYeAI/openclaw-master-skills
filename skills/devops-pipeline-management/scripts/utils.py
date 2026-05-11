#!/usr/bin/env python3
"""
工具函数模块
提供交互式输入、选择、确认等功能
"""

import sys
from typing import Optional, Dict, List


def prompt_choice(prompt_text: str, options: List[Dict], option_key: str = 'value') -> Optional[Dict]:
    """
    交互式选择接口 - 在实际交互中由上层框架调用

    Args:
        prompt_text: 提示文本
        options: 选项列表 [{"label": "选项1", "value": "opt1"}, ...]
        option_key: 使用哪个字段作为返回值

    Returns:
        选中的选项对象，如果没有选项返回None
    """
    if not options:
        return None

    print(f"\n{prompt_text}")
    for i, option in enumerate(options, 1):
        label = option.get('label', option.get(option_key, str(option)))
        print(f"  {i}. {label}")

    while True:
        try:
            choice = input("\n请选择 (输入数字，直接回车使用默认值): ").strip()
            if not choice:
                # 返回默认选项（第一个）
                return options[0]
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print(f"请输入 1-{len(options)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")
        except EOFError:
            # 当管道输入耗尽时，返回默认选项
            print(f"(输入耗尽，使用默认选项)")
            return options[0] if options else None


def prompt_input(prompt_text: str, default: str = None) -> str:
    """
    带默认值的输入提示

    Args:
        prompt_text: 提示文本
        default: 默认值

    Returns:
        用户输入或默认值
    """
    try:
        value = input(prompt_text).strip()
        return value if value else default
    except EOFError:
        print(f"(输入耗尽，使用默认值: {default})")
        return default


def confirm(prompt_text: str, default: bool = False) -> bool:
    """
    确认提示

    Args:
        prompt_text: 提示文本
        default: 默认选项

    Returns:
        用户确认返回True，否则返回False
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        try:
            choice = input(prompt_text + suffix).strip().lower()
            if not choice:
                return default
            if choice in ('y', 'yes'):
                return True
            if choice in ('n', 'no'):
                return False
            print("请输入 y 或 n")
        except EOFError:
            # 当管道输入耗尽时，返回默认值以避免无限循环
            print(f"(输入耗尽，使用默认值: {default})")
            return default

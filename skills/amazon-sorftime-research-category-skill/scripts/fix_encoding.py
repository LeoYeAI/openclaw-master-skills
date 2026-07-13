#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编码修复工具 - 修复 UTF-8/Latin-1 双重编码问题 (Mojibake)

用法:
    python fix_encoding.py <json_file>

示例:
    python fix_encoding.py category-reports/Kitchen_US_20260304/data.json
"""

import json
import sys
import os


def fix_mojibake(obj):
    """
    修复 UTF-8/Latin-1 双重编码问题

    当 UTF-8 字节被错误地解释为 Latin-1 时会产生乱码:
    - 'æ ' 应该是 '标' (E6 A0 87)
    - 'é¢' 应该是 '题' (E9 A2 98)

    解决方法: encode('latin-1') → decode('utf-8')
    """
    if isinstance(obj, dict):
        return {fix_mojibake(k): fix_mojibake(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_mojibake(item) for item in obj]
    elif isinstance(obj, str):
        # 检查是否包含典型 Mojibake 模式
        mojibake_patterns = ['æ ', 'é¢', 'å ', 'ä»£', 'åç', 'å³', '§']
        if any(p in obj for p in mojibake_patterns):
            try:
                return obj.encode('latin-1').decode('utf-8')
            except:
                return obj
        return obj
    else:
        return obj


def main():
    if len(sys.argv) < 2:
        print("用法: python fix_encoding.py <json_file>")
        print("\n示例:")
        print("  python fix_encoding.py category-reports/Kitchen_US_20260304/data.json")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        sys.exit(1)

    print(f"读取文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"错误: 无法读取 JSON 文件 - {e}")
        sys.exit(1)

    print("检测并修复编码问题...")

    # 检查是否有 Mojibake
    json_str = json.dumps(data, ensure_ascii=False)
    has_mojibake = any(p in json_str for p in ['æ ', 'é¢', 'å ', 'ä»£'])

    if not has_mojibake:
        print("未检测到编码问题，文件正常。")
        return

    # 修复编码
    fixed_data = fix_mojibake(data)

    # 检查修复效果
    fixed_str = json.dumps(fixed_data, ensure_ascii=False)
    remaining_mojibake = any(p in fixed_str for p in ['æ ', 'é¢', 'å ', 'ä»£'])

    if remaining_mojibake:
        print("警告: 修复后仍有部分编码问题")

    # 保存修复后的数据
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"原始文件已备份到: {backup_path}")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    print(f"编码修复完成: {file_path}")

    # 显示修复前后对比
    print("\n修复对比:")
    if isinstance(data, dict) and 'Top100产品' in data:
        original_key = list(data.keys())[0] if data else ''
        fixed_key = list(fixed_data.keys())[0] if fixed_data else ''
        if original_key != fixed_key:
            print(f"  键名: {original_key} → {fixed_key}")


if __name__ == "__main__":
    main()

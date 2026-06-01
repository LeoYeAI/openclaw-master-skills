#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例文件名生成器
每次生成文件名都添加时间戳后缀，便于版本管理和历史追溯

使用方法：
    python3 generate_filename.py <base_name> <output_dir>

参数：
    base_name: 基础文件名（不含扩展名）
    output_dir: 输出目录

输出：
    JSON格式的文件路径，包含md和xmind文件名
    格式：{"md_file": "path/to/file.md", "xmind_file": "path/to/file.xmind", "base_name": "file-v0318_143052"}
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path


def generate_filename(base_name: str, output_dir: str) -> dict:
    """
    生成测试用例文件名（带时间戳）
    
    Args:
        base_name: 基础文件名（不含扩展名）
        output_dir: 输出目录
    
    Returns:
        dict: 包含md_file、xmind_file和base_name的字典
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成时间戳（格式：MMdd_HHmmss）
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    
    # 生成带时间戳的文件名
    final_base_name = f"{base_name}-v{timestamp}"
    
    # 构造完整路径
    md_file = os.path.join(output_dir, f"{final_base_name}.md")
    xmind_file = os.path.join(output_dir, f"{final_base_name}.xmind")
    
    return {
        "md_file": md_file,
        "xmind_file": xmind_file,
        "base_name": final_base_name
    }


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法：python3 generate_filename.py <base_name> <output_dir>", file=sys.stderr)
        print("示例：python3 generate_filename.py '专属管家产品V1.0测试用例' '/Users/xxx/downloads'", file=sys.stderr)
        sys.exit(1)
    
    base_name = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 生成文件名
    result = generate_filename(base_name, output_dir)
    
    # 输出JSON格式结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

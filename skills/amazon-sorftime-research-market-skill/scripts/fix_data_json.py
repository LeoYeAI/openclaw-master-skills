#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证和修复脚本 - 确保 data.json 结构正确

用法:
    python fix_data_json.py path/to/data.json
    python fix_data_json.py path/to/data.json --fix
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path


def validate_data(data: dict) -> tuple[bool, list[str]]:
    """验证数据结构"""
    errors = []
    warnings = []

    # 必需字段检查
    required_fields = ['metadata', 'market_overview']
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")

    # metadata 检查
    if 'metadata' in data:
        metadata = data['metadata']
        required_metadata = ['category', 'site', 'date']
        for field in required_metadata:
            if field not in metadata:
                warnings.append(f"metadata 缺少字段: {field}")

    # market_overview 检查
    if 'market_overview' in data:
        mo = data['market_overview']
        required_mo = ['top100_monthly_sales', 'top100_monthly_revenue', 'avg_price']
        for field in required_mo:
            if field not in mo:
                warnings.append(f"market_overview 缺少字段: {field}")

    # go_nogo 检查
    if 'go_nogo' not in data:
        errors.append("缺少 go_nogo 字段")
    else:
        gogono = data['go_nogo']
        if 'overall_score' not in gogono and 'total_score' not in gogono:
            warnings.append("go_nogo 缺少评分字段")
        if 'decision' not in gogono and 'verdict' not in gogono:
            warnings.append("go_nogo 缺少决策字段")

    # dimensions 检查
    if 'dimensions' in data and data['dimensions']:
        # 检查每个维度是否有正确的结构
        for i, dim in enumerate(data['dimensions']):
            if 'dimension' not in dim and 'name' not in dim:
                warnings.append(f"dimensions[{i}] 缺少 'dimension' 或 'name' 字段")

    # voc_analysis 检查
    if 'voc_analysis' in data and data['voc_analysis']:
        voc = data['voc_analysis']
        if 'dimensions' not in voc:
            warnings.append("voc_analysis 缺少 'dimensions' 字段")

    is_valid = len(errors) == 0
    return is_valid, errors + warnings


def fix_data(data: dict) -> dict:
    """修复常见的数据结构问题"""
    # 修复 go_nogo 字段名称
    if 'go_nogo' in data:
        gogono = data['go_nogo']
        if 'verdict' in gogono and 'decision' not in gogono:
            gogono['decision'] = gogono['verdict']
        if 'total_score' in gogono and 'overall_score' not in gogono:
            gogono['overall_score'] = gogono['total_score']

    # 确保必需字段存在
    if 'market_overview' not in data:
        data['market_overview'] = {}

    mo = data['market_overview']
    if 'top3_product_concentration' not in mo and 'top3_concentration' in mo:
        mo['top3_product_concentration'] = mo['top3_concentration']

    return data


def main():
    parser = argparse.ArgumentParser(description="数据验证和修复脚本")
    parser.add_argument("data_file", help="data.json 文件路径")
    parser.add_argument("--fix", action="store_true", help="自动修复问题")
    parser.add_argument("--output", "-o", help="输出文件路径（默认覆盖原文件）")

    args = parser.parse_args()

    data_path = Path(args.data_file)
    if not data_path.exists():
        print(f"✗ 文件不存在: {data_path}")
        return 1

    # 读取数据
    print(f"读取数据: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 验证数据
    is_valid, messages = validate_data(data)

    print("\n验证结果:")
    for msg in messages:
        prefix = "✗" if "错误" in msg or "缺少" in msg else "⚠"
        print(f"  {prefix} {msg}")

    if is_valid:
        print("\n✓ 数据结构验证通过")
    else:
        print("\n✗ 数据结构存在问题")
        if not args.fix:
            print("  提示: 使用 --fix 参数尝试自动修复")
            return 1

    # 修复数据
    if args.fix:
        print("\n修复数据...")
        data = fix_data(data)

        # 重新验证
        is_valid_after, messages_after = validate_data(data)
        if is_valid_after:
            print("✓ 数据修复成功")
        else:
            print("⚠ 部分问题无法自动修复")

        # 保存
        output_path = Path(args.output) if args.output else data_path
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 已保存: {output_path}")

    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime 类目趋势数据解析器
解析 category_trend API 返回的 SSE 格式数据
"""

import re
import json
import codecs
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional


def decode_sse_trend(file_path: str) -> dict:
    """
    解码 Sorftime category_trend SSE 响应

    Args:
        file_path: SSE 响应文件路径

    Returns:
        dict: 解码后的趋势数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 方法1: 提取 SSE data 行中的 JSON
    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 前缀
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # 解码 Unicode 转义
                    decoded = codecs.decode(result_text, 'unicode-escape')
                    # 提取 JSON 对象
                    start = decoded.find('{')
                    if start != -1:
                        # 找到匹配的结束括号
                        depth = 0
                        end = -1
                        for i in range(start, len(decoded)):
                            if decoded[i] == '{':
                                depth += 1
                            elif decoded[i] == '}':
                                depth -= 1
                                if depth == 0:
                                    end = i + 1
                                    break
                        if end != -1:
                            json_str = decoded[start:end]
                            return json.loads(json_str)
            except:
                continue

    # 方法2: 直接搜索 JSON 模式
    # 趋势数据通常包含 "趋势日期" 或 "trendDate" 字段
    patterns = [
        r'"趋势日期":\[([^\]]+)\]',
        r'"trendDate":\[([^\]]+)\]',
        r'"趋势值":\[([^\]]+)\]',
        r'"trendValue":\[([^\]]+)\]'
    ]

    result = {}
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            key = 'dates' if '日期' in pattern or 'Date' in pattern else 'values'
            # 提取数组内容
            array_content = match.group(1)
            # 简单解析（假设是字符串数组）
            if array_content:
                result[key] = [item.strip('"') for item in array_content.split(',')]

    return result


def extract_trend_data(data: dict, trend_type: str) -> dict:
    """
    从解码数据中提取趋势信息

    Args:
        data: 解码后的 JSON 数据
        trend_type: 趋势类型

    Returns:
        dict: 包含日期和值的趋势数据
    """
    # 趋势数据可能的字段名
    date_field_candidates = ['趋势日期', 'trendDate', 'dates', 'date']
    value_field_candidates = ['趋势值', 'trendValue', 'values', 'data', 'value']

    dates = []
    values = []

    for field in date_field_candidates:
        if field in data:
            dates = data[field]
            break

    for field in value_field_candidates:
        if field in data:
            values = data[field]
            break

    # 如果数据是嵌套结构，尝试提取
    if not dates or not values:
        # 检查是否有类目趋势字段
        if '类目趋势' in data:
            trend_info = data['类目趋势']
            dates = trend_info.get('趋势日期', trend_info.get('trendDate', []))
            values = trend_info.get('趋势值', trend_info.get('trendValue', []))

    return {
        'type': trend_type,
        'dates': dates,
        'values': values
    }


def save_trend_json(trend_data: dict, output_dir: str, filename: str = 'trend_data.json'):
    """保存合并后的趋势数据到 JSON 文件"""
    output_file = os.path.join(output_dir, filename)

    # 如果文件已存在，读取并合并
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        existing_data.update(trend_data)
        trend_data = existing_data

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)

    return output_file


def parse_all_trends(input_dir: str) -> dict:
    """
    解析目录中的所有趋势文件

    Args:
        input_dir: 包含趋势原始文件的目录

    Returns:
        dict: 所有趋势数据的字典
    """
    trend_files = {
        '类目月销量趋势': 'trend_类目月销量趋势_raw.txt',
        '平均售价趋势': 'trend_平均售价趋势_raw.txt',
        '平均星级趋势': 'trend_平均星级趋势_raw.txt',
        '品牌数量趋势': 'trend_品牌数量趋势_raw.txt'
    }

    all_trends = {}

    for trend_type, filename in trend_files.items():
        file_path = os.path.join(input_dir, filename)
        if not os.path.exists(file_path):
            print(f"  跳过: {filename} (文件不存在)")
            continue

        try:
            decoded = decode_sse_trend(file_path)
            trend = extract_trend_data(decoded, trend_type)

            # 转换数据格式为图表所需格式
            if trend['dates'] and trend['values']:
                # 清理数据
                dates = [str(d).strip('"').strip("'") for d in trend['dates']]
                values = [float(v) if isinstance(v, (int, float, str)) else 0 for v in trend['values']]

                # 根据趋势类型存储到不同的键
                if trend_type == '类目月销量趋势':
                    all_trends['sales_trend'] = {'dates': dates, 'sales': values}
                elif trend_type == '平均售价趋势':
                    all_trends['price_trend'] = {'dates': dates, 'prices': values}
                elif trend_type == '平均星级趋势':
                    all_trends['rating_trend'] = {'dates': dates, 'ratings': values}
                elif trend_type == '品牌数量趋势':
                    all_trends['brand_count_trend'] = {'dates': dates, 'count': values}

                print(f"  ✓ {trend_type}: {len(dates)} 个数据点")

        except Exception as e:
            print(f"  ✗ {trend_type} 解析失败: {e}")

    return all_trends


def main():
    if len(sys.argv) < 2:
        print("用法: python trend_parser.py <数据目录>")
        print("\n示例:")
        print("  python trend_parser.py category-reports/Sofas_US_20260304")
        sys.exit(1)

    input_dir = sys.argv[1]

    print("\n" + "="*60)
    print("类目趋势数据解析")
    print("="*60)

    # 解析所有趋势文件
    all_trends = parse_all_trends(input_dir)

    if all_trends:
        # 保存合并数据
        output_file = save_trend_json(all_trends, input_dir)
        print(f"\n趋势数据已保存到: {output_file}")

        # 打印摘要
        print("\n数据摘要:")
        for key, data in all_trends.items():
            print(f"  - {key}: {len(data.get('dates', []))} 个月")
    else:
        print("\n警告: 未找到有效的趋势数据")


if __name__ == "__main__":
    main()

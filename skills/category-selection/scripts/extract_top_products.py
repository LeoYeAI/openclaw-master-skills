#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Sorftime category_report 响应中提取 Top N 产品
处理大数据文件 (>25000 tokens) 的标准工具
"""

import re
import sys
import json
from typing import List, Dict, Optional


def extract_top_products(file_path: str, limit: int = 100) -> List[Dict]:
    """
    从 Sorftime 响应文件中提取 Top N 产品

    Args:
        file_path: Sorftime API 响应文件路径
        limit: 提取产品数量

    Returns:
        产品列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 文件不存在 {file_path}")
        return []
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        return []

    # 使用正则表达式提取产品信息
    # 模式：ASIN + 标题 + 价格 + 销量 + 评分 + 品牌
    # 这种模式可以处理 Unicode 转义的中文
    products = []

    # 方法1: 匹配完整的产品块
    product_pattern = r'\{"ASIN":"([A-Z0-9]{10})"[^\}]*?"月销量":"?(\d+)"?[^\}]*?"月销额":"?([\d.]+)"?[^\}]*?"标题":"([^"]{30,150})"[^\}]*?"价格":"?([\d.]+)"?[^\}]*?"星级":"?([\d.]+)"?[^\}]*?"品牌":"([^"]+?)"[^\}]*?\}'

    for match in re.finditer(product_pattern, content):
        asin, sales, revenue, title, price, rating, brand = match.groups()

        products.append({
            'ASIN': asin,
            '标题': title,
            '价格': float(price),
            '月销量': int(sales),
            '月销额': float(revenue),
            '评分': float(rating),
            '品牌': brand
        })

        if len(products) >= limit:
            break

    # 如果方法1没有找到足够产品，尝试方法2（更宽松的模式）
    if len(products) < limit:
        # 方法2: 逐个字段提取
        asin_pattern = r'"ASIN":"([A-Z0-9]{10})"'
        asins = list(set(re.findall(asin_pattern, content)))

        for asin in asins:
            if len(products) >= limit:
                break

            # 找到这个 ASIN 附近的数据块
            asin_pos = content.find(f'"ASIN":"{asin}"')
            if asin_pos == -1:
                continue

            # 提取 ASIN 周围 2000 字符的数据
            chunk = content[max(0, asin_pos - 100):asin_pos + 2000]

            # 从 chunk 中提取其他字段
            title_match = re.search(r'"标题":"([^"]{30,100})"', chunk)
            price_match = re.search(r'"价格":([\d.]+)', chunk)
            sales_match = re.search(r'"月销量":"?(\d+)"?', chunk)
            rating_match = re.search(r'"星级":"?([\d.]+)"?', chunk)
            brand_match = re.search(r'"品牌":"([^"]+?)"', chunk)

            if title_match and price_match:
                products.append({
                    'ASIN': asin,
                    '标题': title_match.group(1),
                    '价格': float(price_match.group(1)),
                    '月销量': int(sales_match.group(1)) if sales_match else 0,
                    '评分': float(rating_match.group(1)) if rating_match else 0,
                    '品牌': brand_match.group(1) if brand_match else 'Unknown'
                })

    return products


def print_products_table(products: List[Dict]):
    """打印产品表格"""
    if not products:
        print("未找到产品数据")
        return

    print(f"\n=== Top {len(products)} 产品 ===")
    print("-" * 100)
    print(f"{'排名':<4} {'ASIN':<12} {'品牌':<15} {'价格':<8} {'月销量':<10} {'评分':<6} {'标题'}")
    print("-" * 100)

    for i, p in enumerate(products, 1):
        title = p.get('标题', 'N/A')[:50]
        print(f"{i:<4} {p.get('ASIN', ''):<12} {p.get('品牌', ''):<15} "
              f"${p.get('价格', 0):<7.2f} {p.get('月销量', 0):<10,} "
              f"{p.get('评分', 0):<5.1f} {title}...")

    print("-" * 100)


def analyze_products(products: List[Dict]) -> Dict:
    """分析产品数据"""
    if not products:
        return {}

    total_sales = sum(p.get('月销量', 0) for p in products)
    total_revenue = sum(p.get('月销额', 0) for p in products)
    avg_price = sum(p.get('价格', 0) for p in products) / len(products)
    avg_rating = sum(p.get('评分', 0) for p in products) / len(products)

    # 品牌统计
    brands = {}
    for p in products:
        brand = p.get('品牌', 'Unknown')
        brands[brand] = brands.get(brand, 0) + 1

    # 排序品牌
    top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        '总销量': total_sales,
        '总销额': total_revenue,
        '平均价格': avg_price,
        '平均评分': avg_rating,
        '品牌数量': len(brands),
        'Top品牌': top_brands
    }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python extract_top_products.py <响应文件路径> [数量]")
        print("\n示例:")
        print("  python extract_top_products.py temp_response.txt 100")
        print("\n选项:")
        print("  --json    输出 JSON 格式")
        print("  --analyze 分析产品数据")
        sys.exit(1)

    file_path = sys.argv[1]
    limit = 100

    # 解析参数
    for arg in sys.argv[2:]:
        if arg.isdigit():
            limit = int(arg)

    # 提取产品
    products = extract_top_products(file_path, limit)

    if not products:
        print("未找到产品数据")
        sys.exit(1)

    # 打印表格
    print_products_table(products)

    # 分析数据
    if '--analyze' in sys.argv:
        analysis = analyze_products(products)

        print("\n=== 产品分析 ===")
        for key, value in analysis.items():
            if key == 'Top品牌':
                print(f"\n{key}:")
                for brand, count in value:
                    print(f"  - {brand}: {count} 个产品")
            else:
                print(f"  {key}: {value}")

    # 输出 JSON
    if '--json' in sys.argv:
        print("\n=== JSON 输出 ===")
        print(json.dumps(products, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

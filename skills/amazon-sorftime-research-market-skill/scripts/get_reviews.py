#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取竞品差评数据（通用版本）

使用方法:
    python get_reviews.py --output-dir "product-research/xxx_YYYYMMDD"

注意：此脚本从 top100.json 中自动选择代表性竞品
"""
import json
import os
import sys
from datetime import datetime

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from api_client import SorftimeClient

def get_project_root():
    """获取项目根目录"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 从 scripts/ 向上四级到达项目根目录
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="获取竞品差评数据（通用版本）")
    parser.add_argument("--output-dir", "-o", required=True, help="输出目录（包含 top100.json 的目录）")
    parser.add_argument("--site", default="US", help="站点代码")
    parser.add_argument("--max-reviews", type=int, default=6, help="最大竞品数量")
    args = parser.parse_args()

    # 检查 top100.json 是否存在
    top100_path = os.path.join(args.output_dir, 'raw', 'top100.json')
    if not os.path.exists(top100_path):
        print(f"✗ 错误：找不到 {top100_path}")
        print("  请确保输出目录中存在 raw/top100.json 文件")
        return 1

    client = SorftimeClient()

    # 读取 Top100 数据
    with open(top100_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('Top100产品', []) or data.get('Top100 产品', [])

    if not products:
        print("✗ 错误：top100.json 中没有产品数据")
        return 1

    print(f"📊 从 {len(products)} 个产品中选择代表性竞品...")

    # 按销量排序
    sorted_products = sorted(products, key=lambda x: float(x.get('月销量', 0)), reverse=True)

    # 选择策略：Top3 + 不同价格带代表
    competitors = []

    # 量级标杆（Top3）
    for i, p in enumerate(sorted_products[:3]):
        competitors.append((p['ASIN'], f"Top{i+1} - {p.get('品牌', 'Unknown')}"))

    # 按价格分组选择
    price_groups = {
        'low': [p for p in sorted_products if float(p.get('价格', 0)) < 30],
        'mid': [p for p in sorted_products if 30 <= float(p.get('价格', 0)) < 60],
        'high': [p for p in sorted_products if float(p.get('价格', 0)) >= 60]
    }

    # 各价位代表
    for price_name, price_list in [('低价', price_groups['low']), ('中价', price_groups['mid']), ('高价', price_groups['high'])]:
        for p in price_list:
            if p['ASIN'] not in [c[0] for c in competitors]:
                competitors.append((p['ASIN'], f"{price_name}代表 - {p.get('品牌', 'Unknown')}"))
                break

    # 去重
    seen = set()
    competitors = [x for x in competitors if not (x[0] in seen or seen.add(x[0]))]

    # 限制数量
    competitors = competitors[:args.max_reviews]

    print(f"  选择了 {len(competitors)} 个竞品进行差评分析")

    all_reviews = {}
    for asin, desc in competitors:
        print(f"  - {asin} ({desc})...", end=' ', flush=True)
        try:
            reviews, raw = client.get_product_reviews(args.site, asin, 'Negative')
            if reviews:
                if isinstance(reviews, list):
                    review_count = len(reviews)
                    sample = reviews[:20] if len(reviews) > 20 else reviews
                else:
                    review_count = 'data'
                    sample = reviews

                all_reviews[asin] = {
                    'description': desc,
                    'review_count': review_count,
                    'reviews': sample
                }
                print(f"✓ {review_count}条")
            else:
                print("✗ 无数据")
        except Exception as e:
            print(f"✗ {str(e)[:40]}")

    # 保存结果
    if all_reviews:
        reviews_path = os.path.join(args.output_dir, 'raw', 'competitor_reviews.json')
        os.makedirs(os.path.dirname(reviews_path), exist_ok=True)

        with open(reviews_path, 'w', encoding='utf-8') as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 差评数据已保存: {reviews_path}")
        return 0
    else:
        print("\n✗ 未获取到任何差评数据")
        return 1

if __name__ == "__main__":
    sys.exit(main())

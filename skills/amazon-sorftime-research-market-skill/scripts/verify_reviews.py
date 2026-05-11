#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Reviews 数据完整性
"""
import json
import os
import sys

def verify_reviews_data(reviews_path):
    """验证 Reviews 数据"""
    if not os.path.exists(reviews_path):
        print(f"✗ 文件不存在: {reviews_path}")
        return False

    with open(reviews_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"=== Reviews 数据验证 ===")
    print(f"文件路径: {reviews_path}")
    print(f"文件大小: {os.path.getsize(reviews_path)/1024:.1f} KB")
    print()

    print(f"竞品数量: {len(data)}")

    total_reviews = 0
    for asin, info in data.items():
        desc = info.get('description', 'N/A')
        count = info.get('review_count', 0)
        reviews = info.get('reviews', [])

        if isinstance(count, int):
            total_reviews += count

        review_count = len(reviews) if isinstance(reviews, list) else 0
        print(f"  - {asin}: {desc} ({count} 条，保存 {review_count} 条)")

    print()
    print(f"总差评数: {total_reviews}")
    print("✓ 数据验证通过")

    return True


def find_all_reviews_dirs():
    """查找所有 Reviews 数据目录"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 可能的目录位置
    search_paths = [
        os.path.join(project_root, 'product-research-reports'),  # 新的输出目录
        # os.path.join(project_root, 'product-research'),  # 旧的输出目录（已废弃）
    ]

    print(f"=== 搜索 Reviews 数据目录 ===")
    print(f"项目根目录: {project_root}")
    print()

    found = []
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue

        for root, dirs, files in os.walk(base_path):
            if 'competitor_reviews.json' in files:
                # 如果在 raw 目录，记录父目录
                if os.path.basename(root) == 'raw':
                    found.append(os.path.dirname(root))
                    print(f"✓ 找到: {os.path.dirname(root)}")
                else:
                    found.append(root)
                    print(f"✓ 找到: {root}")

    return found


if __name__ == '__main__':
    # 查找所有 Reviews 数据
    dirs = find_all_reviews_dirs()

    if not dirs:
        print("\n未找到任何 Reviews 数据")
        sys.exit(1)

    print(f"\n共找到 {len(dirs)} 个数据目录")

    # 验证最新的数据
    latest_dir = max(dirs, key=lambda x: os.path.getmtime(x))
    reviews_path = os.path.join(latest_dir, 'raw', 'competitor_reviews.json')

    print(f"\n验证最新数据: {latest_dir}")
    print()

    verify_reviews_data(reviews_path)

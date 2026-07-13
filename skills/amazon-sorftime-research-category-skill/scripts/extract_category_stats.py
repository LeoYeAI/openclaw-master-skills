#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Sorftime category_report 响应中提取统计数据
处理大数据文件 (>25000 tokens) 的标准工具
"""

import re
import sys
import json
from typing import Dict, Optional


def extract_statistics(file_path: str) -> Dict[str, str]:
    """
    从 Sorftime 响应文件中提取类目统计数据

    Args:
        file_path: Sorftime API 响应文件路径

    Returns:
        包含统计数据的字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 文件不存在 {file_path}")
        return {}
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        return {}

    # 定义需要提取的字段模式
    patterns = {
        '总销量': r'"top100产品月销量":"?(\d+)"?',
        '总销额': r'"top100产品月销额":"?([\d.]+)"?',
        '平均价格': r'"average_price":"?([\d.]+)"?',
        '中位数价格': r'"median_price":"?([\d.]+)"?',
        'Top3品牌占比': r'"top3_brands_sales_volume_share":"?([\d.]+%?)"?',
        'Amazon自营占比': r'"amazonOwned_sales_volume_share":"?([\d.]+%?)"?',
        '高评分占比': r'"high_rated_sales_volume_share":"?([\d.]+%?)"?',
        '低评论占比': r'"low_reviews_sales_volume_share":"?([\d.]+%?)"?',
    }

    results = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            results[name] = match.group(1)
        else:
            results[name] = "未找到"

    return results


def calculate_scores_from_stats(stats: Dict[str, str]) -> Dict[str, float]:
    """
    基于统计数据计算五维评分

    Args:
        stats: 从 extract_statistics 返回的统计数据

    Returns:
        五维评分字典
    """
    # 辅助函数：安全提取数值
    def safe_float(value, default=0):
        try:
            return float(str(value).replace('%', '').replace(',', ''))
        except:
            return default

    # 提取数值
    revenue = safe_float(stats.get('总销额', 0))
    top3_share = safe_float(stats.get('Top3品牌占比', 0))
    amazon_share = safe_float(stats.get('Amazon自营占比', 0))
    low_review_share = safe_float(stats.get('低评论占比', 0))
    avg_price = safe_float(stats.get('平均价格', 0))

    scores = {}

    # 1. 市场规模 (20分)
    if revenue > 10000000:
        scores['市场规模'] = 20
    elif revenue > 5000000:
        scores['市场规模'] = 17
    elif revenue > 1000000:
        scores['市场规模'] = 14
    else:
        scores['市场规模'] = 10

    # 2. 增长潜力 (25分) - 基于低评论产品占比 (新品机会)
    if low_review_share > 40:
        scores['增长潜力'] = 22
    elif low_review_share > 20:
        scores['增长潜力'] = 18
    else:
        scores['增长潜力'] = 14

    # 3. 竞争烈度 (20分) - 基于 Top3 品牌占比
    if top3_share < 30:
        scores['竞争烈度'] = 18  # 低度集中
    elif top3_share < 50:
        scores['竞争烈度'] = 14  # 中度集中
    else:
        scores['竞争烈度'] = 8   # 高度集中

    # 4. 进入壁垒 (20分)
    barrier_score = 0

    # Amazon 占比越低，壁垒越小
    if amazon_share < 20:
        barrier_score += 10
    elif amazon_share < 40:
        barrier_score += 6
    else:
        barrier_score += 3

    # 新品机会越大，壁垒越小
    if low_review_share > 40:
        barrier_score += 10
    elif low_review_share > 20:
        barrier_score += 6
    else:
        barrier_score += 3

    scores['进入壁垒'] = barrier_score

    # 5. 利润空间 (15分)
    if avg_price > 300:
        scores['利润空间'] = 12
    elif avg_price > 150:
        scores['利润空间'] = 10
    elif avg_price > 50:
        scores['利润空间'] = 7
    else:
        scores['利润空间'] = 4

    # 计算总分
    scores['总分'] = sum(scores.values())

    # 评级
    if scores['总分'] >= 80:
        scores['评级'] = '优秀'
    elif scores['总分'] >= 70:
        scores['评级'] = '良好'
    elif scores['总分'] >= 50:
        scores['评级'] = '一般'
    else:
        scores['评级'] = '较差'

    return scores


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python extract_category_stats.py <响应文件路径>")
        print("\n示例:")
        print("  python extract_category_stats.py temp_response.txt")
        print("\n或者从标准输入读取:")
        print("  cat temp_response.txt | python extract_category_stats.py -")
        sys.exit(1)

    file_path = sys.argv[1]

    # 提取统计数据
    stats = extract_statistics(file_path)

    if not stats:
        print("未能提取到统计数据")
        sys.exit(1)

    print("=" * 60)
    print("类目统计数据")
    print("=" * 60)

    # 打印统计数据
    for name, value in stats.items():
        if value != "未找到":
            print(f"  {name}: {value}")

    # 计算评分
    scores = calculate_scores_from_stats(stats)

    print("\n" + "=" * 60)
    print("五维评分")
    print("=" * 60)

    for dimension, score in scores.items():
        if dimension not in ['总分', '评级']:
            print(f"  {dimension}: {score}")

    print(f"\n  总分: {scores['总分']}/100")
    print(f"  评级: {scores['评级']}")

    # 输出 JSON 格式 (便于脚本使用)
    if '--json' in sys.argv:
        output = {
            'statistics': stats,
            'scores': scores
        }
        print("\n" + "=" * 60)
        print("JSON 格式输出")
        print("=" * 60)
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime SSE 响应快速解码器 v3.0
专门处理 category_report 的 SSE 响应格式
"""

import re
import json
import codecs
import sys
import os
from datetime import datetime


def decode_sse_response(file_path: str) -> dict:
    """
    解码 Sorftime SSE 响应文件

    Args:
        file_path: SSE 响应文件路径

    Returns:
        dict: 解码后的完整 JSON 数据
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

    # 方法2: 直接搜索 JSON 数组模式
    array_match = re.search(r'\[{"[^"]*"[^}]{50,}', content)
    if array_match:
        # 找到完整的数据范围
        raw_content = content
        # 查找第一个 { 和最后一个 }
        start = raw_content.find('{"Top100产品"')
        if start == -1:
            start = raw_content.find('{"类目统计报告"')
        if start == -1:
            start = raw_content.find('{\\"关键词\\"')

        if start != -1:
            # 手动解析
            bracket_count = 0
            in_string = False
            escape_next = False
            end = -1

            for i in range(start, len(raw_content)):
                c = raw_content[i]

                if escape_next:
                    escape_next = False
                    continue

                if c == '\\':
                    escape_next = True
                    continue

                if c == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if c == '{':
                        bracket_count += 1
                    elif c == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = i + 1
                            break

            if end != -1:
                # 提取并解码
                raw_json = raw_content[start:end]
                # 解码 unicode escapes like \u0022
                decoded = codecs.decode(raw_json, 'unicode-escape')
                return json.loads(decoded)

    raise ValueError("无法解析 SSE 响应文件")


def fix_mojibake(obj):
    """
    修复 UTF-8/Latin-1 双重编码问题 (Mojibake)

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
        mojibake_patterns = ['æ ', 'é¢', 'å ', 'ä»£', 'åç']
        if any(p in obj for p in mojibake_patterns):
            try:
                return obj.encode('latin-1').decode('utf-8')
            except:
                return obj
        return obj
    else:
        return obj


def save_decoded_data(data: dict, output_dir: str):
    """保存解码后的数据，自动修复编码问题"""
    os.makedirs(output_dir, exist_ok=True)

    # 修复可能的 Mojibake 编码问题
    fixed_data = fix_mojibake(data)

    # 保存完整 JSON
    output_file = os.path.join(output_dir, 'data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    return output_file


def extract_category_stats(data: dict) -> dict:
    """提取类目统计数据"""
    stats = data.get('类目统计报告', {})

    return {
        'nodeid': stats.get('nodeid', ''),
        '类目名称': stats.get('类目名称', ''),
        'top100产品月销量': stats.get('top100产品月销量', '0'),
        'top100产品月销额': stats.get('top100产品月销额', '0'),
        'average_price': stats.get('average_price', '0'),
        'median_price': stats.get('median_price', '0'),
        'top3_brands_sales_volume_share': stats.get('top3_brands_sales_volume_share', '0'),
        'amazonOwned_sales_volume_share': stats.get('amazonOwned_sales_volume_share', '0'),
        'high_rated_sales_volume_share': stats.get('high_rated_sales_volume_share', '0'),
        'low_reviews_sales_volume_share': stats.get('low_reviews_sales_volume_share', '0'),
    }


def extract_top_products(data: dict, limit: int = 20) -> list:
    """提取 Top N 产品"""
    products_list = data.get('Top100产品', [])

    result = []
    for p in products_list[:limit]:
        # 提取月销量（处理字符串格式的数字）
        monthly_sales = p.get('月销量', '0')
        if isinstance(monthly_sales, str):
            # 移除非数字字符
            monthly_sales = re.sub(r'[^\d.]', '', monthly_sales)

        # 提取价格
        price = float(p.get('价格', 0))

        # 计算月销额 = 价格 * 月销量
        monthly_sales_num = int(float(monthly_sales)) if monthly_sales else 0
        monthly_revenue = price * monthly_sales_num

        result.append({
            'ASIN': p.get('ASIN', ''),
            '标题': p.get('标题', '')[:80],
            '价格': price,
            '月销量': monthly_sales_num,
            '月销额': monthly_revenue,  # 新增：计算得出
            '评分': float(p.get('星级', 0)),
            '品牌': p.get('品牌', 'Unknown'),
            '评论数': int(p.get('评论数', 0)),
            '卖家来源': p.get('卖家来源', ''),
            '卖家': p.get('卖家', ''),  # 新增：卖家名称
            '上架天数': p.get('上架天数', 0),  # 新增：如果有此字段
            '类目排名': p.get('类目排名', ''),  # 新增：类目排名
            '图片': p.get('图片', ''),  # 新增：产品图片URL
        })

    return result


def calculate_five_dimension_score(stats: dict) -> dict:
    """
    计算五维评分 (标准版本)

    评分标准:
    - 市场规模 (20分): >10M=20, >5M=17, >1M=14, 其他=10
    - 增长潜力 (25分): 低评论占比>40%=22, >20%=18, 其他=14
    - 竞争烈度 (20分): Top3<30%=18, <50%=14, 其他=8
    - 进入壁垒 (20分): Amazon占比+新品机会组合评分
    - 利润空间 (15分): 均价>$300=12, >$150=10, >$50=7, 其他=4
    """
    def safe_float(value, default=0):
        try:
            return float(str(value).replace('%', '').replace(',', '').replace('$', ''))
        except:
            return default

    scores = {}

    # 1. 市场规模 (20分)
    revenue = safe_float(stats.get('top100产品月销额', 0))
    if revenue > 10_000_000:
        scores['市场规模'] = 20
    elif revenue > 5_000_000:
        scores['市场规模'] = 17
    elif revenue > 1_000_000:
        scores['市场规模'] = 14
    else:
        scores['市场规模'] = 10

    # 2. 增长潜力 (25分)
    low_review_share = safe_float(stats.get('low_reviews_sales_volume_share', 0))
    if low_review_share > 40:
        scores['增长潜力'] = 22
    elif low_review_share > 20:
        scores['增长潜力'] = 18
    else:
        scores['增长潜力'] = 14

    # 3. 竞争烈度 (20分)
    top3_share = safe_float(stats.get('top3_brands_sales_volume_share', 0))
    if top3_share < 30:
        scores['竞争烈度'] = 18
    elif top3_share < 50:
        scores['竞争烈度'] = 14
    else:
        scores['竞争烈度'] = 8

    # 4. 进入壁垒 (20分)
    amazon_share = safe_float(stats.get('amazonOwned_sales_volume_share', 0))

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
    avg_price = safe_float(stats.get('average_price', 0))
    if avg_price > 300:
        scores['利润空间'] = 12
    elif avg_price > 150:
        scores['利润空间'] = 10
    elif avg_price > 50:
        scores['利润空间'] = 7
    else:
        scores['利润空间'] = 4

    # 总分
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


def print_summary(stats: dict, products: list):
    """打印摘要信息"""
    print("\n" + "=" * 70)
    print("类目数据解码成功")
    print("=" * 70)

    print(f"\n类目: {stats.get('类目名称', 'Unknown')}")
    print(f"NodeID: {stats.get('nodeid', 'N/A')}")

    total_sales = stats.get('top100产品月销量', '0')
    total_revenue = stats.get('top100产品月销额', '0')
    avg_price = stats.get('average_price', '0')

    print(f"\nTop100 月销量: {total_sales}")
    print(f"Top100 月销额: ${total_revenue}")
    print(f"平均价格: ${avg_price}")

    print(f"\nTop3 品牌占比: {stats.get('top3_brands_sales_volume_share', 'N/A')}")
    print(f"Amazon 自营: {stats.get('amazonOwned_sales_volume_share', 'N/A')}")
    print(f"新品机会(<300评论): {stats.get('low_reviews_sales_volume_share', 'N/A')}")

    # 计算并显示五维评分
    scores = calculate_five_dimension_score(stats)
    print(f"\n【五维评分】")
    for key, value in scores.items():
        if key not in ['总分', '评级']:
            print(f"  {key}: {value}")
    print(f"  总分: {scores['总分']}/100")
    print(f"  评级: {scores['评级']}")

    print(f"\n【Top {len(products)} 产品】")
    print("-" * 100)
    for i, p in enumerate(products, 1):
        print(f"{i:2}. {p['ASIN']} | {p['品牌']:<15} | ${p['价格']:7.2f} | "
              f"销量:{p['月销量']:5} | 评分:{p['评分']:3.1f}★")
    print("-" * 100)


def main():
    if len(sys.argv) < 2:
        print("用法: python sse_decoder.py <SSE响应文件> [输出目录] [产品数量]")
        print("\n示例:")
        print("  python sse_decoder.py response.txt")
        print("  python sse_decoder.py response.txt ./output 50")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 20

    try:
        # 解码 SSE 响应
        data = decode_sse_response(file_path)

        # 保存完整数据
        saved_file = save_decoded_data(data, output_dir)
        print(f"\n完整数据已保存到: {saved_file}")

        # 提取统计数据
        stats = extract_category_stats(data)

        # 提取产品列表
        products = extract_top_products(data, limit)

        # 打印摘要
        print_summary(stats, products)

        # 计算并保存评分
        scores = calculate_five_dimension_score(stats)
        scores_file = os.path.join(output_dir, 'scores.json')
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        print(f"\n五维评分已保存到: {scores_file}")

        # 保存产品列表到单独文件
        products_file = os.path.join(output_dir, 'top_products.json')
        with open(products_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"Top {len(products)} 产品已保存到: {products_file}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

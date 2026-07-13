#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime SSE 响应快速解码器 v6.0 - Mojibake 修复版
专门处理 category_report 的 SSE 响应格式

主要改进:
1. 修复 Unicode-escape + Mojibake 双重编码问题
2. 在 Unicode 解码后立即应用 Mojibake 修复
3. 更健壮的控制字符处理
4. 改进的括号匹配算法
5. 更详细的调试信息
6. 支持 Python dict 格式转 JSON
"""

import re
import json
import codecs
import sys
import os
from datetime import datetime


def safe_float(value, default=0.0):
    """安全地转换为浮点数"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # 移除常见的非数字字符
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def safe_int(value, default=0):
    """安全地转换为整数"""
    return int(safe_float(value, default))


def clean_json_string(json_str: str) -> str:
    """
    清理 JSON 字符串中的控制字符和转义序列
    """
    # 替换常见的转义换行符（在 JSON 字符串中）
    json_str = json_str.replace('\\r\\n', ' ')
    json_str = json_str.replace('\\r', ' ')
    json_str = json_str.replace('\\n', ' ')

    # 移除实际的控制字符（解码后产生的）
    json_str = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', json_str)

    return json_str


def fix_mojibake_text(text: str) -> str:
    """
    修复 Mojibake (UTF-8/Latin-1 双重编码)

    当 UTF-8 字节被错误地解释为 Latin-1 时会产生乱码
    修复方法: encode as Latin-1, then decode as UTF-8
    """
    if not isinstance(text, str):
        return text

    # 检测 Mojibake: 如果包含 Latin-1 扩展字符范围，可能是 Mojibake
    # Latin-1 扩展字符: \xc0-\xff (À-ÿ)
    has_latin1_extended = any(0xC0 <= ord(c) <= 0xFF for c in text if c != '\r' and c != '\n' and c != '\t')

    if has_latin1_extended:
        try:
            # 尝试修复: Latin-1 -> UTF-8
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    return text


def decode_sse_response(file_path: str, verbose: bool = False) -> dict:
    """
    解码 Sorftime SSE 响应文件

    支持多种格式:
    1. 标准 SSE 格式 (event: message, data: {...})
    2. 直接 JSON 格式
    3. 嵌套转义的 JSON 格式

    Args:
        file_path: SSE 响应文件路径
        verbose: 是否显示详细调试信息

    Returns:
        dict: 解码后的完整 JSON 数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if verbose:
        print(f"[DEBUG] 文件大小: {len(content)} 字节")
        print(f"[DEBUG] 文件前200字符: {content[:200]}")

    # 策略 1: 标准 SSE 格式解析
    if verbose:
        print("\n[策略1] 尝试标准 SSE 格式解析...")

    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 前缀
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # 关键修复: 先清理，再 Unicode 解码，再 Mojibake 修复
                    cleaned_text = clean_json_string(result_text)

                    # 解码 Unicode 转义
                    decoded = codecs.decode(cleaned_text, 'unicode-escape')

                    # 立即修复 Mojibake
                    decoded = fix_mojibake_text(decoded)

                    # 再次清理（解码后可能产生新的控制字符）
                    decoded = clean_json_string(decoded)

                    # 提取 JSON 对象（使用括号匹配）
                    json_obj = extract_json_object(decoded)
                    if json_obj:
                        if verbose:
                            print("[策略1] ✓ 成功")
                        return json_obj
            except Exception as e:
                if verbose:
                    print(f"[策略1] 失败: {e}")
                continue

    # 策略 2: 直接 JSON 解析（用于已经提取好的 JSON）
    if verbose:
        print("\n[策略2] 尝试直接 JSON 解析...")

    try:
        # 先尝试 Mojibake 修复整个内容
        fixed_content = fix_mojibake_text(content)
        data = json.loads(fixed_content)
        if verbose:
            print("[策略2] ✓ 直接解析成功")
        return data
    except Exception as e:
        if verbose:
            print(f"[策略2] 失败: {e}")

    # 策略 3: 正则表达式直接提取 JSON
    if verbose:
        print("\n[策略3] 尝试正则表达式提取...")

    # 查找 JSON 开始标记
    patterns = [
        r'(\{"Top100产品":)',
        r'(\{"Top100\\u[0-9a-f]{4}[0-9a-f]{4}:)',
        r'("Top100产品":)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            start = match.start()
            if content[start] != '{':
                start = content.rfind('{', 0, start)

            # 使用括号匹配找到完整的 JSON
            json_obj = extract_json_from_text(content, start)
            if json_obj:
                if verbose:
                    print("[策略3] ✓ 成功")
                return json_obj

    raise ValueError("无法解析 SSE 响应文件 - 所有策略均失败")


def extract_json_object(text: str) -> dict:
    """
    从文本中提取完整的 JSON 对象
    使用括号匹配来处理嵌套结构
    """
    start = text.find('{')
    if start == -1:
        return None

    json_str = extract_json_from_text(text, start)
    if not json_str:
        return None

    # 转换 Python dict 格式为 JSON 格式
    json_str = python_dict_to_json(json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}")


def extract_json_from_text(text: str, start: int = 0) -> str:
    """
    从文本中提取完整的 JSON/Python dict 字符串
    使用括号匹配算法
    """
    if start >= len(text):
        return None

    if text[start] != '{':
        # 找到下一个 '{'
        start = text.find('{', start)
        if start == -1:
            return None

    depth = 0
    in_string = False
    escape_next = False
    end = -1

    for i in range(start, len(text)):
        c = text[i]

        if escape_next:
            escape_next = False
            continue

        if c == '\\':
            escape_next = True
            continue

        if c == '"':
            in_string = not in_string
            continue

        if not in_string:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

    if end == -1:
        return None

    return text[start:end]


def python_dict_to_json(text: str) -> str:
    """
    将 Python dict 格式（单引号）转换为 JSON 格式（双引号）
    同时处理 True/False/None
    """
    # 先替换 Python 字面量
    text = text.replace('True', 'true')
    text = text.replace('False', 'false')
    text = text.replace('None', 'null')

    # 转换单引号为双引号（注意不要处理字符串内的单引号）
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(text):
        c = text[i]

        if escape_next:
            result.append(c)
            escape_next = False
            i += 1
            continue

        if c == '\\':
            result.append(c)
            escape_next = True
            i += 1
            continue

        if c == '"':
            in_string = not in_string
            result.append(c)
            i += 1
            continue

        # 只在非字符串内的单引号转换为双引号
        if c == "'" and not in_string:
            result.append('"')
            i += 1
            continue

        result.append(c)
        i += 1

    return ''.join(result)


def save_decoded_data(data: dict, output_dir: str):
    """保存解码后的数据"""
    os.makedirs(output_dir, exist_ok=True)

    # 保存完整 JSON
    output_file = os.path.join(output_dir, 'data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_file


def extract_category_stats(data: dict) -> dict:
    """提取类目统计数据"""
    # 尝试不同的键名
    stats = data.get('类目统计报告', {})

    if not stats:
        # 如果没有统计数据，从产品列表计算
        products = data.get('Top100产品', data.get('产品列表', []))
        if products:
            total_revenue = sum(safe_float(p.get('月销额', 0)) for p in products)
            total_sales = sum(safe_int(p.get('月销量', 0)) for p in products)
            avg_price = total_revenue / total_sales if total_sales > 0 else 0

            stats = {
                'top100产品月销额': str(total_revenue),
                'top100产品月销量': str(total_sales),
                'average_price': str(avg_price),
            }

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
    # 尝试不同的键名
    products_list = data.get('Top100产品', data.get('产品列表', data.get('products', [])))

    result = []
    for p in products_list[:limit]:
        # 安全提取和转换数据
        monthly_sales = safe_int(p.get('月销量', '0'))
        price = safe_float(p.get('价格', 0))
        monthly_revenue = safe_float(p.get('月销额', price * monthly_sales))

        result.append({
            'ASIN': p.get('ASIN', ''),
            '标题': p.get('标题', '')[:80],
            '价格': price,
            '月销量': monthly_sales,
            '月销额': monthly_revenue,
            '评分': safe_float(p.get('星级', p.get('评分', 0))),
            '品牌': p.get('品牌', 'Unknown'),
            '评论数': safe_int(p.get('评论数', 0)),
            '卖家来源': p.get('卖家来源', ''),
            '卖家': p.get('卖家', ''),
            '上架天数': safe_int(p.get('上架天数', p.get('上线天数', 0))),
            '类目排名': p.get('类目排名', p.get('所处类目排名', '')),
            '图片': p.get('图片', ''),
        })

    return result


def calculate_five_dimension_score(stats: dict, products: list = None) -> dict:
    """
    计算五维评分 (标准版本)

    评分标准:
    - 市场规模 (20分): >10M=20, >5M=17, >1M=14, 其他=10
    - 增长潜力 (25分): 低评论占比>40%=22, >20%=18, 其他=14
    - 竞争烈度 (20分): Top3<30%=18, <50%=14, 其他=8
    - 进入壁垒 (20分): Amazon占比+新品机会组合评分
    - 利润空间 (15分): 均价>$300=12, >$150=10, >$50=7, 其他=4
    """
    scores = {}

    # 从产品列表计算统计数据（如果 stats 中没有）
    if products and not stats.get('top3_brands_sales_volume_share'):
        total_revenue = sum(p.get('月销额', 0) for p in products)
        if total_revenue > 0:
            # 计算品牌份额
            brand_revenue = {}
            for p in products:
                brand = p.get('品牌', 'Unknown')
                brand_revenue[brand] = brand_revenue.get(brand, 0) + p.get('月销额', 0)

            # Top3 份额
            sorted_brands = sorted(brand_revenue.values(), reverse=True)
            top3_share = sum(sorted_brands[:3]) / total_revenue * 100 if sorted_brands else 0
            stats['top3_brands_sales_volume_share'] = str(top3_share)

            # Amazon 份额
            amazon_revenue = sum(p.get('月销额', 0) for p in products if p.get('卖家') == 'Amazon')
            amazon_share = amazon_revenue / total_revenue * 100
            stats['amazonOwned_sales_volume_share'] = str(amazon_share)

            # 低评论产品份额
            low_review_revenue = sum(p.get('月销额', 0) for p in products if p.get('评论数', 0) < 300)
            low_review_share = low_review_revenue / total_revenue * 100
            stats['low_reviews_sales_volume_share'] = str(low_review_share)

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
    scores = calculate_five_dimension_score(stats, products)
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
        print("用法: python sse_decoder.py <SSE响应文件> [输出目录] [产品数量] [--verbose]")
        print("\n示例:")
        print("  python sse_decoder.py response.txt")
        print("  python sse_decoder.py response.txt ./output 50")
        print("  python sse_decoder.py response.txt ./output 20 --verbose")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 20
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    try:
        # 解码 SSE 响应
        print(f"\n正在解析文件: {file_path}")
        data = decode_sse_response(file_path, verbose=verbose)

        # 保存完整数据
        saved_file = save_decoded_data(data, output_dir)
        print(f"\n✓ 完整数据已保存到: {saved_file}")

        # 提取统计数据
        stats = extract_category_stats(data)

        # 提取产品列表
        products = extract_top_products(data, limit)

        # 打印摘要
        print_summary(stats, products)

        # 计算并保存评分
        scores = calculate_five_dimension_score(stats, products)
        scores_file = os.path.join(output_dir, 'scores.json')
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 五维评分已保存到: {scores_file}")

        # 保存产品列表到单独文件
        products_file = os.path.join(output_dir, 'top_products.json')
        with open(products_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"✓ Top {len(products)} 产品已保存到: {products_file}")

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

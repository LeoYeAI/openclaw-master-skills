#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime category_report 健壮解析器 v2.0
处理 SSE 响应 + Unicode 转义的复杂格式
"""

import re
import sys
import json
import codecs


def fix_chinese_keys(obj):
    """
    修复中文键名的编码问题

    当 UTF-8 编码的中文被错误地当作 Latin-1 解码时，会产生乱码。
    例如: "产品" -> "äº§å"
    修复方法: encode('latin-1') -> decode('utf-8')
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            # 修复键名
            if isinstance(key, str):
                # 检测是否包含 UTF-8 被当作 Latin-1 解码的乱码
                if any(0x80 <= ord(c) <= 0xFF for c in key):
                    try:
                        fixed_key = key.encode('latin-1').decode('utf-8')
                    except:
                        fixed_key = key
                else:
                    fixed_key = key
            else:
                fixed_key = key

            # 递归修复值
            new_dict[fixed_key] = fix_chinese_keys(value)
        return new_dict
    elif isinstance(obj, list):
        return [fix_chinese_keys(item) for item in obj]
    else:
        return obj


def parse_sorftime_sse(file_path: str, limit: int = 100):
    """
    完整解析 Sorftime SSE 响应文件

    Args:
        file_path: 响应文件路径
        limit: 提取产品数量

    Returns:
        dict: {statistics, products, scores}
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: 提取 SSE data 行
    result_text = None
    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 前缀
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    break
            except:
                continue

    if not result_text:
        return {'error': '无法提取 SSE data'}

    # Step 2: 解码 Unicode 转义
    # result_text 包含类似 {\u0022Top100\u4ea7\u54c1\u0022:[...]}
    # 需要先解码 Unicode 转义，再解析 JSON
    try:
        decoded = codecs.decode(result_text, 'unicode-escape')
    except:
        # 如果解码失败，尝试直接使用
        decoded = result_text

    # Step 3: 提取 JSON 对象
    # 查找第一个 { 和匹配的 }
    start = decoded.find('{')
    if start == -1:
        return {'error': '未找到 JSON 开始'}

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

    if end == -1:
        return {'error': '未找到 JSON 结束'}

    json_str = decoded[start:end]

    # Step 4: 解析 JSON (修复编码问题)
    try:
        # 尝试直接解析
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        # 清理控制字符后重试
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        try:
            parsed = json.loads(json_str)
        except:
            return {'error': f'JSON 解析失败: {e}'}

    # Step 4.5: 修复中文键名编码问题
    parsed = fix_chinese_keys(parsed)

    # Step 5: 提取统计数据
    stats = extract_stats_from_parsed(parsed)

    # Step 6: 提取产品列表
    products = extract_products_from_parsed(parsed, limit)

    # Step 7: 计算评分
    scores = calculate_scores(stats)

    return {
        'statistics': stats,
        'products': products,
        'scores': scores
    }


def extract_stats_from_parsed(parsed: dict) -> dict:
    """从已解析的数据中提取统计数据"""
    stats = {}

    # 查找类目统计报告
    category_stats = parsed.get('类目统计报告', {})

    if not category_stats:
        # 尝试其他可能的键名
        for key in parsed.keys():
            if '统计' in key or 'stats' in key.lower():
                category_stats = parsed[key]
                break

    # 提取字段
    field_mappings = {
        '总销量': ['top100产品月销量', '总销量', 'total_sales'],
        '总销额': ['top100产品月销额', '总销额', 'total_revenue'],
        '平均价格': ['average_price', '平均价格', 'avg_price'],
        '中位数价格': ['median_price', '中位数价格'],
        'Top3品牌占比': ['top3_brands_sales_volume_share', 'Top3品牌占比'],
        'Amazon自营占比': ['amazonOwned_sales_volume_share', 'Amazon自营占比'],
        '低评论占比': ['low_reviews_sales_volume_share', '低评论占比'],
    }

    for stat_name, possible_keys in field_mappings.items():
        for key in possible_keys:
            if key in category_stats:
                raw_value = category_stats[key]
                # 清理数值：从描述中提取数字
                stats[stat_name] = extract_numeric_value(raw_value)
                break
        if stat_name not in stats:
            stats[stat_name] = '未找到'

    return stats


def extract_numeric_value(raw_value):
    """
    从可能包含中文描述的值中提取数值
    例如: "销量前的80%产品平均价格：17.239" -> "17.239"
    """
    if isinstance(raw_value, (int, float)):
        return raw_value

    if isinstance(raw_value, str):
        # 尝试提取数字（包括小数和百分比）
        # 查找所有数字模式
        patterns = [
            r'(\d+\.?\d*)%?',  # 数字 + 可选小数 + 可选百分号
            r':\s*(\d+\.?\d*)',  # 冒号后的数字
        ]

        for pattern in patterns:
            matches = re.findall(pattern, raw_value)
            if matches:
                # 取最后一个数字（通常是实际值）
                value = matches[-1]
                # 如果是百分比且小于100，可能需要处理
                try:
                    return float(value)
                except:
                    continue

        # 如果没有找到，返回原始值
        return raw_value

    return raw_value


def extract_products_from_parsed(parsed: dict, limit: int) -> list:
    """从已解析的数据中提取产品列表"""
    products = []

    # 查找产品列表
    products_key = None
    for key in parsed.keys():
        if 'Top100' in key or 'top100' in key or 'product' in key.lower():
            products_key = key
            break

    if not products_key:
        return []

    raw_products = parsed[products_key]
    if not isinstance(raw_products, list):
        return []

    for p in raw_products[:limit]:
        products.append({
            'ASIN': p.get('ASIN', ''),
            '标题': p.get('标题', p.get('title', '')),
            '价格': float(p.get('价格', p.get('price', 0))),
            '月销量': int(p.get('月销量', p.get('monthly_sales', 0))),
            '评分': float(p.get('星级', p.get('rating', 0))),
            '品牌': p.get('品牌', p.get('brand', 'Unknown'))
        })

    return products


def calculate_scores(stats: dict) -> dict:
    """计算五维评分"""
    def safe_float(value, default=0):
        try:
            return float(str(value).replace('%', '').replace(',', ''))
        except:
            return default

    revenue = safe_float(stats.get('总销额', 0))
    top3_share = safe_float(stats.get('Top3品牌占比', 0))
    amazon_share = safe_float(stats.get('Amazon自营占比', 0))
    low_review_share = safe_float(stats.get('低评论占比', 0))
    avg_price = safe_float(stats.get('平均价格', 0))

    scores = {}

    # 市场规模
    if revenue > 10000000:
        scores['市场规模'] = 20
    elif revenue > 5000000:
        scores['市场规模'] = 17
    elif revenue > 1000000:
        scores['市场规模'] = 14
    else:
        scores['市场规模'] = 10

    # 增长潜力
    if low_review_share > 40:
        scores['增长潜力'] = 22
    elif low_review_share > 20:
        scores['增长潜力'] = 18
    else:
        scores['增长潜力'] = 14

    # 竞争烈度
    if top3_share < 30:
        scores['竞争烈度'] = 18
    elif top3_share < 50:
        scores['竞争烈度'] = 14
    else:
        scores['竞争烈度'] = 8

    # 进入壁垒
    barrier_score = 0
    if amazon_share < 20:
        barrier_score += 10
    elif amazon_share < 40:
        barrier_score += 6
    else:
        barrier_score += 3

    if low_review_share > 40:
        barrier_score += 10
    elif low_review_share > 20:
        barrier_score += 6
    else:
        barrier_score += 3

    scores['进入壁垒'] = barrier_score

    # 利润空间
    if avg_price > 300:
        scores['利润空间'] = 12
    elif avg_price > 150:
        scores['利润空间'] = 10
    elif avg_price > 50:
        scores['利润空间'] = 7
    else:
        scores['利润空间'] = 4

    scores['总分'] = sum(scores.values())

    if scores['总分'] >= 80:
        scores['评级'] = '优秀'
    elif scores['总分'] >= 70:
        scores['评级'] = '良好'
    elif scores['总分'] >= 50:
        scores['评级'] = '一般'
    else:
        scores['评级'] = '较差'

    return scores


def print_report(result: dict):
    """打印报告"""
    if 'error' in result:
        print(f"错误: {result['error']}")
        return

    print("=" * 70)
    print("类目选品分析报告")
    print("=" * 70)

    # 统计数据
    if result.get('statistics'):
        print("\n【统计数据】")
        for name, value in result['statistics'].items():
            print(f"  {name}: {value}")

    # 评分
    if result.get('scores'):
        print("\n【五维评分】")
        scores = result['scores']
        for key, value in scores.items():
            if key not in ['总分', '评级']:
                print(f"  {key}: {value}")
        print(f"\n  总分: {scores.get('总分', 0)}/100")
        print(f"  评级: {scores.get('评级', '未知')}")

    # 产品列表
    if result.get('products'):
        print(f"\n【Top {len(result['products'])} 产品】")
        print("-" * 100)
        for i, p in enumerate(result['products'], 1):
            print(f"{i}. {p.get('ASIN')} | {p.get('品牌')} | "
                  f"${p.get('价格', 0):.2f} | {p.get('月销量', 0):,}销量 | "
                  f"{p.get('评分', 0):.1f}★")
            title = p.get('标题', '')[:60]
            print(f"   {title}...")
        print("-" * 100)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python parse_sorftime_sse.py <响应文件路径> [产品数量] [--生成报告]")
        print("\n示例:")
        print("  python parse_sorftime_sse.py temp_response.txt 100")
        print("  python parse_sorftime_sse.py temp_response.txt 100 --生成报告")
        sys.exit(1)

    file_path = sys.argv[1]
    limit = 100
    generate_reports_flag = False

    for arg in sys.argv[2:]:
        if arg.isdigit():
            limit = int(arg)
        elif arg == '--生成报告' or arg == '--generate':
            generate_reports_flag = True

    result = parse_sorftime_sse(file_path, limit)
    print_report(result)

    if '--json' in sys.argv:
        print("\n" + "=" * 70)
        print("JSON 格式输出")
        print("=" * 70)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # 生成报告
    if generate_reports_flag:
        print("\n" + "=" * 70)
        print("正在生成报告...")
        print("=" * 70)

        try:
            from generate_reports import CategoryReportGenerator
            generator = CategoryReportGenerator(result)
            report_files = generator.generate_all()

            print("\n报告已保存到:", generator.output_dir)
        except ImportError:
            print("报告生成模块未找到，跳过")


if __name__ == "__main__":
    main()

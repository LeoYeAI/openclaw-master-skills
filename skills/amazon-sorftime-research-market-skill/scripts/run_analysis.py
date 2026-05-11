#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选品分析主脚本 - 整合数据采集、分析和报告生成

优化版本 v3.1 - 完全通用化（移除硬编码类别词）

使用方法:
    python run_analysis.py "keyword" US
    python run_analysis.py "keyword" US --no-reviews
"""
import sys
import os
import json
import argparse
from datetime import datetime
from collections import defaultdict

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from collect_data import collect_data, create_output_dir, save_json
from api_client import SorftimeClient


def get_project_root():
    """获取项目根目录"""
    # 从 scripts/ 向上四级到达项目根目录
    # 脚本路径：.claude/skills/product-research/scripts/
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))


def analyze_market_data(raw_dir, output_dir):
    """分析市场数据（价格区间、品牌、形态等）"""
    print("\n[分析] 市场数据分析...")

    # 读取 Top100 数据
    top100_path = os.path.join(raw_dir, 'top100.json')
    if not os.path.exists(top100_path):
        print("  ✗ top100.json 不存在")
        return None

    with open(top100_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('Top100产品', [])
    stats = data.get('类目统计报告', {})

    if not products:
        print("  ✗ 产品数据为空")
        return None

    print(f"  ✓ 产品数量: {len(products)}")

    # 价格区间分析
    price_ranges = defaultdict(lambda: {'count': 0, 'sales': 0})
    for p in products:
        price = float(p.get('价格', 0))
        sales = float(p.get('月销量', 0))

        if price < 30:
            price_ranges['0-30']['count'] += 1
            price_ranges['0-30']['sales'] += sales
        elif price < 60:
            price_ranges['30-60']['count'] += 1
            price_ranges['30-60']['sales'] += sales
        elif price < 100:
            price_ranges['60-100']['count'] += 1
            price_ranges['60-100']['sales'] += sales
        elif price < 150:
            price_ranges['100-150']['count'] += 1
            price_ranges['100-150']['sales'] += sales
        elif price < 200:
            price_ranges['150-200']['count'] += 1
            price_ranges['150-200']['sales'] += sales
        else:
            price_ranges['200+']['count'] += 1
            price_ranges['200+']['sales'] += sales

    # 品牌分析
    brand_sales = defaultdict(float)
    brand_count = defaultdict(int)
    for p in products:
        brand = p.get('品牌', 'Unknown')
        sales = float(p.get('月销量', 0))
        brand_sales[brand] += sales
        brand_count[brand] += 1

    # 卖家来源分析
    seller_source_sales = defaultdict(float)
    seller_source_count = defaultdict(int)
    for p in products:
        source = p.get('卖家来源', 'Unknown')
        sales = float(p.get('月销量', 0))
        seller_source_sales[source] += sales
        seller_source_count[source] += 1

    # 汇总分析结果
    # 注意：产品形态分析由 LLM 在报告生成阶段完成，不在此处硬编码
    analysis = {
        'price_ranges': dict(price_ranges),
        'top_brands': dict(sorted(brand_sales.items(), key=lambda x: x[1], reverse=True)[:10]),
        'brand_counts': dict(brand_count),
        'seller_sources': dict(seller_source_sales),
        'seller_counts': dict(seller_source_count),
        'top20_products': products[:20]
    }

    # 保存分析结果
    analysis_path = os.path.join(output_dir, 'market_analysis.json')
    save_json(analysis, analysis_path)
    print(f"  ✓ 分析结果已保存: {analysis_path}")

    return analysis


def collect_competitor_reviews(node_id, site, raw_dir, max_reviews=6):
    """收集竞品差评数据"""
    print("\n[数据采集] 竞品差评分析...")

    client = SorftimeClient()

    # 读取 Top100 数据，选择代表性竞品
    top100_path = os.path.join(raw_dir, 'top100.json')
    if not os.path.exists(top100_path):
        print("  ✗ top100.json 不存在，跳过差评分析")
        return False

    with open(top100_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('Top100产品', [])

    # 按销量排序，选择不同价格带的代表性产品
    sorted_products = sorted(products, key=lambda x: float(x.get('月销量', 0)), reverse=True)

    # 辅助函数：兼容中英文键名
    def get_field(product, field_name, cn_field_name):
        """获取产品字段，兼容中英文键名"""
        return product.get(field_name) or product.get(cn_field_name, '')

    def get_asin(p):
        return get_field(p, 'ASIN', '产品ASIN码')

    def get_brand(p):
        return get_field(p, '品牌', 'Brand')

    # 选择策略：Top3 + 不同价格带代表
    competitors = []

    # 量级标杆（Top3）
    for p in sorted_products[:3]:
        asin = get_asin(p)
        brand = get_brand(p)
        if asin:
            competitors.append((asin, f"{brand} - 量级标杆"))

    # 中价位代表 ($30-60)
    mid_price = [p for p in sorted_products if 30 <= float(p.get('价格', 0)) < 60]
    if mid_price:
        asin = get_asin(mid_price[0])
        brand = get_brand(mid_price[0])
        if asin:
            competitors.append((asin, f"{brand} - 中价位"))

    # 低价位代表 ($0-30)
    low_price = [p for p in sorted_products if float(p.get('价格', 0)) < 30]
    if low_price:
        asin = get_asin(low_price[0])
        brand = get_brand(low_price[0])
        if asin:
            competitors.append((asin, f"{brand} - 低价位"))

    # 高价位代表 ($100+)
    high_price = [p for p in sorted_products if float(p.get('价格', 0)) >= 100]
    if high_price:
        asin = get_asin(high_price[0])
        brand = get_brand(high_price[0])
        if asin:
            competitors.append((asin, f"{brand} - 高价位"))

    # 去重
    seen = set()
    competitors = [x for x in competitors if not (x[0] in seen or seen.add(x[0]))]

    # 限制数量
    competitors = competitors[:max_reviews]

    print(f"  选择竞品数量: {len(competitors)}")

    all_reviews = {}
    for asin, desc in competitors:
        print(f"  - {asin} ({desc})...", end=' ', flush=True)
        try:
            reviews, raw = client.get_product_reviews(site, asin, 'Negative')
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

    # 保存
    if all_reviews:
        reviews_path = os.path.join(raw_dir, 'competitor_reviews.json')
        save_json(all_reviews, reviews_path)
        print(f"  ✓ 差评数据已保存: {reviews_path}")
        return True

    return False


def update_data_json(raw_dir, output_dir):
    """
    更新 data.json - 将分析数据合并到 Dashboard 需要的格式

    这个函数解决了数据结构不匹配的问题：
    - collect_data.py 生成的基础 data.json 只有元数据
    - render_dashboard.py 期望完整的数据结构
    - 本函数将 market_analysis.json 等分析结果合并到 data.json
    """
    print("\n[更新] 合并分析数据到 data.json...")

    data_json_path = os.path.join(output_dir, 'data.json')
    market_analysis_path = os.path.join(output_dir, 'market_analysis.json')
    top100_path = os.path.join(raw_dir, 'top100.json')
    trend_path = os.path.join(raw_dir, 'trend.json')
    keywords_path = os.path.join(raw_dir, 'keywords.json')

    # 读取现有的 data.json
    if not os.path.exists(data_json_path):
        print("  ✗ data.json 不存在")
        return False

    with open(data_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 读取并处理 market_analysis.json
    if os.path.exists(market_analysis_path):
        with open(market_analysis_path, 'r', encoding='utf-8') as f:
            market_analysis = json.load(f)

        # 转换价格区间数据为 Dashboard 期望的列表格式
        if 'price_ranges' in market_analysis:
            price_ranges_dict = market_analysis['price_ranges']
            price_ranges_list = []
            total_sales = sum(p['sales'] for p in price_ranges_dict.values())

            for range_name, range_data in price_ranges_dict.items():
                count = range_data['count']
                sales = range_data['sales']
                share = sales / total_sales if total_sales > 0 else 0
                price_ranges_list.append({
                    'range': f'${range_name}',
                    'count': count,
                    'share': share,
                    'sales': sales
                })

            data['price_ranges'] = price_ranges_list

        # 转换品牌数据
        if 'top_brands' in market_analysis:
            top_brands = []
            for brand, sales in market_analysis['top_brands'].items():
                brand_count = market_analysis.get('brand_counts', {}).get(brand, 0)
                top_brands.append({
                    'brand': brand,
                    'sales': int(sales),
                    'revenue': int(sales * 50),  # 估算收入
                    'count': brand_count
                })
            data['top_brands'] = top_brands[:10]

        # 转换竞品数据
        if 'top20_products' in market_analysis:
            competitors = []
            for p in market_analysis['top20_products'][:10]:
                competitors.append({
                    'asin': p.get('ASIN', ''),
                    'brand': p.get('品牌', ''),
                    'title': p.get('标题', ''),
                    'price': float(p.get('价格', 0)),
                    'monthly_sales': int(float(p.get('月销量', 0))),
                    'reviews': int(float(p.get('评论数', 0))),
                    'rating': float(p.get('星级', 0)),
                    'type': '竞品',
                    'launch_date': p.get('上线日期', '')
                })
            data['competitors'] = competitors

    # 读取并处理 trend.json
    if os.path.exists(trend_path):
        with open(trend_path, 'r', encoding='utf-8') as f:
            trend_data = json.load(f)

        if 'trend_data' in trend_data:
            data['trend_data'] = trend_data['trend_data']

    # 读取并处理 keywords.json
    if os.path.exists(keywords_path):
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords_data = json.load(f)

        # 转换为 Dashboard 期望的格式
        keywords_summary = {}
        for kw_name, kw_data in keywords_data.items():
            if isinstance(kw_data, dict) and '关键词' in kw_data:
                keywords_summary[kw_name] = {
                    'monthly_search': int(float(kw_data.get('月搜索量', 0))),
                    'weekly_search': int(float(kw_data.get('周搜索量', 0))),
                    'cpc': float(kw_data.get('推荐cpc竞价', 0)),
                    'competition_count': int(float(kw_data.get('搜索结果竞品数量', 0)))
                }

        data['keywords'] = keywords_summary

    # 计算市场概览指标（从 top100 数据）
    if os.path.exists(top100_path):
        with open(top100_path, 'r', encoding='utf-8') as f:
            top100_data = json.load(f)

        products = top100_data.get('Top100产品', [])
        stats = top100_data.get('类目统计报告', {})

        if products and stats:
            total_sales = sum(float(p.get('月销量', 0)) for p in products)
            total_revenue = sum(float(p.get('月销额', 0)) for p in products)

            # 计算品牌集中度
            brand_sales = {}
            for p in products:
                brand = p.get('品牌', 'Unknown')
                sales = float(p.get('月销量', 0))
                brand_sales[brand] = brand_sales.get(brand, 0) + sales

            sorted_brands = sorted(brand_sales.items(), key=lambda x: x[1], reverse=True)
            top3_brand_sales = sum(sales for _, sales in sorted_brands[:3])
            top10_brand_sales = sum(sales for _, sales in sorted_brands[:10])

            data['market_overview'] = {
                'top100_monthly_sales': int(total_sales),
                'top100_monthly_revenue': int(total_revenue),
                'avg_price': total_revenue / total_sales if total_sales > 0 else 0,
                'median_price': sorted([float(p.get('价格', 0)) for p in products])[len(products)//2] if products else 0,
                'top3_product_concentration': 0,  # 简化
                'top3_brand_concentration': top3_brand_sales / total_sales if total_sales > 0 else 0,
                'top10_brand_concentration': top10_brand_sales / total_sales if total_sales > 0 else 0,
                'amazon_share': 0,  # 需要从卖家数据计算
                'china_seller_share': 0,
                'new_product_share': 0,
                'keyword_monthly_search': data.get('keywords', {}).get(data.get('metadata', {}).get('keyword', ''), {}).get('monthly_search', 0)
            }

    # 保存更新后的 data.json
    save_json(data, data_json_path)
    print(f"  ✓ data.json 已更新")
    return True


def render_dashboard_html(output_dir, check_complete=False):
    """
    渲染 Dashboard HTML

    Args:
        output_dir: 输出目录
        check_complete: 是否检查分析数据完整性（用于 --final 模式）
    """
    print("\n[Dashboard] 渲染可视化看板...")

    # 导入 render_dashboard
    try:
        from render_dashboard import DashboardRenderer

        data_json_path = os.path.join(output_dir, 'data.json')
        dashboard_path = os.path.join(output_dir, 'dashboard.html')

        # 检查 data.json 是否存在
        if not os.path.exists(data_json_path):
            print(f"  ✗ data.json 不存在，无法渲染 Dashboard")
            return False

        # 如果是 --final 模式，先检查数据完整性
        if check_complete:
            print(f"  检查分析数据完整性...")
            with open(data_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            is_complete, missing = DashboardRenderer.validate_analysis_data(data)

            if not is_complete:
                print(f"  ✗ 分析数据不完整，缺少: {', '.join(missing)}")
                print(f"  ℹ️ 请先完成 LLM 分析（属性标注、交叉分析、VOC、决策评估）")
                return False

            print(f"  ✓ 数据完整，渲染最终版 Dashboard")

        # 渲染 Dashboard
        renderer = DashboardRenderer()
        result_path = renderer.render(data_json_path, dashboard_path)

        print(f"  ✓ Dashboard 已生成: {result_path}")
        return True

    except ImportError as e:
        print(f"  ✗ 无法导入 render_dashboard: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Dashboard 渲染失败: {e}")
        return False


def generate_report(keyword, site, output_dir, raw_dir, check_complete=False):
    """
    生成分析报告（Markdown + Dashboard）

    Args:
        keyword: 关键词
        site: 站点
        output_dir: 输出目录
        raw_dir: 原始数据目录
        check_complete: 是否检查分析数据完整性（用于 --final 模式）
    """
    print("\n[报告生成] 生成分析报告...")

    report_path = os.path.join(output_dir, 'report.md')
    dashboard_path = os.path.join(output_dir, 'dashboard.html')

    # 检查是否已有报告
    if os.path.exists(report_path):
        print(f"  ✓ 报告已存在: {report_path}")
    else:
        print(f"  ⚠ 报告需要 LLM 生成: {report_path}")

    # 自动渲染 Dashboard（如果 data.json 存在）
    if os.path.exists(dashboard_path) and not check_complete:
        print(f"  ✓ Dashboard 已存在: {dashboard_path}")
    else:
        # 尝试自动渲染
        render_dashboard_html(output_dir, check_complete=check_complete)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="选品分析主脚本（通用版本）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程：数据采集 + 分析
  python run_analysis.py "speaker" US

  # 仅数据采集，不生成报告
  python run_analysis.py "speaker" US --collect-only

  # 跳过差评采集
  python run_analysis.py "speaker" US --no-reviews

  # 最终渲染：LLM 分析完成后生成完整报告
  python run_analysis.py "speaker" US --final
        """
    )

    parser.add_argument('keyword', help='产品/类目关键词')
    parser.add_argument('site', nargs='?', default='US', help='站点代码 (默认: US)')
    parser.add_argument('--keywords', '-k', type=int, default=3, help='采集关键词数量 (默认: 3)')
    parser.add_argument('--no-reviews', action='store_true', help='跳过差评采集')
    parser.add_argument('--no-analysis', action='store_true', help='跳过市场分析')
    parser.add_argument('--collect-only', action='store_true', help='仅数据采集，不生成报告')
    parser.add_argument('--final', action='store_true', help='最终渲染模式：检查数据完整性后生成完整版 Dashboard')

    args = parser.parse_args()

    print("=" * 60)
    print(f"🔍 选品分析: {args.keyword} ({args.site})")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # --final 模式：仅渲染，不执行数据采集
    if args.final:
        output_dir, raw_dir, date_str = create_output_dir(args.keyword, args.site)

        data_json_path = os.path.join(output_dir, 'data.json')
        if not os.path.exists(data_json_path):
            print(f"\n✗ data.json 不存在: {data_json_path}")
            print(f"ℹ️ 请先运行数据采集: python run_analysis.py \"{args.keyword}\" {args.site}")
            return 1

        print(f"\n[最终渲染模式]")
        print(f"  检查分析数据完整性...")

        # 读取并验证数据
        from render_dashboard import DashboardRenderer
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        is_complete, missing = DashboardRenderer.validate_analysis_data(data)

        if not is_complete:
            print(f"  ✗ 分析数据不完整，缺少: {', '.join(missing)}")
            print(f"  ℹ️ 请先完成 LLM 分析：")
            print(f"     1. 属性标注（从 Top100 提取差异化维度）")
            print(f"     2. 交叉分析（发现供需缺口）")
            print(f"     3. VOC 分析（竞品差评维度归类）")
            print(f"     4. 决策评估（五维评分）")
            print(f"  ℹ️ 分析完成后，再次运行此命令")
            return 1

        print(f"  ✓ 数据完整，生成最终版 Dashboard")

        # 更新 data.json（确保最新）
        update_data_json(raw_dir, output_dir)

        # 生成最终报告
        generate_report(args.keyword, args.site, output_dir, raw_dir, check_complete=True)

        print("\n" + "=" * 60)
        print(f"✓ 最终报告生成完成!")
        print(f"输出目录: {output_dir}")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        return 0

    # 正常模式：数据采集流程
    # Step 1: 数据采集
    collect_result = collect_data(args.keyword, args.site, args.keywords)

    if not collect_result.get('steps_completed'):
        print("\n✗ 数据采集失败，无法继续")
        return 1

    # 获取输出目录
    output_dir, raw_dir, date_str = create_output_dir(args.keyword, args.site)

    # Step 2: 市场分析
    if not args.no_analysis and not args.collect_only:
        analysis = analyze_market_data(raw_dir, output_dir)

    # Step 3: 竞品差评采集
    if not args.no_reviews and not args.collect_only:
        node_id = collect_result.get('node_id')
        if node_id:
            collect_competitor_reviews(node_id, args.site, raw_dir)

    # Step 4: 更新 data.json (合并分析数据)
    if not args.collect_only:
        update_data_json(raw_dir, output_dir)

    # Step 5: 生成报告
    if not args.collect_only:
        generate_report(args.keyword, args.site, output_dir, raw_dir)

    print("\n" + "=" * 60)
    print(f"✓ 数据采集完成!")
    print(f"输出目录: {output_dir}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nℹ️ 下一步：完成 LLM 分析后，运行以下命令生成最终报告:")
    print(f"   python run_analysis.py \"{args.keyword}\" {args.site} --final")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())

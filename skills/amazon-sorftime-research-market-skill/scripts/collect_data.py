#!/usr/bin/env python3
"""
数据采集脚本 - product-research 技能

优化版本 v3.1 - 完全通用化（移除硬编码类别词）

使用方法:
    python collect_data.py "your keyword" US

或直接导入:
    from collect_data import collect_data
    result = collect_data("your keyword", "US")
"""

import sys
import os
import json
import re
from datetime import datetime

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from api_client import SorftimeClient


def create_output_dir(keyword, site):
    """创建输出目录（使用项目根目录）"""
    date_str = datetime.now().strftime('%Y%m%d')
    safe_keyword = keyword.replace(' ', '_').replace('/', '_')

    # 获取项目根目录
    # 脚本路径：.claude/skills/product-research/scripts/collect_data.py
    # 需要向上四级：scripts → product-research → skills → .claude → amazon-mcp
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

    output_dir = os.path.join(project_root, 'product-research-reports', f'{safe_keyword}_{site}_{date_str}')
    raw_dir = os.path.join(output_dir, 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    return output_dir, raw_dir, date_str


def save_json(data, filepath):
    """安全保存 JSON 文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  ✗ 保存失败：{e}")
        return False


def discover_blue_ocean_categories(client, site, keyword, max_categories=5):
    """
    【新增】蓝海市场发现 - 使用 search_categories_broadly

    Args:
        client: SorftimeClient 实例
        site: 站点
        keyword: 产品关键词（用于筛选相关类目）
        max_categories: 返回的类目数量

    Returns:
        list: 符合条件的类目列表
    """
    print("\n[Step 0.5] 蓝海市场发现...")

    # 筛选条件：适合新卖家的蓝海市场
    filters = {
        # 低集中度
        "top3Product_sales_share": 0.4,  # Top3 产品销量占比 < 40%
        "top3Brands_sales_share": 0.5,   # Top3 品牌销量占比 < 50%
        # 新品活跃
        "newProductSalesAmountShare": 0.15,  # 新品销量占比 > 15%
        # 市场分散
        "brandCount": 50,  # 品牌数量 > 50
        # 价格适中
        "priceRange_min": 10,
        "priceRange_max": 50,
        # 有一定规模
        "monthlySales_min": 5000,
    }

    try:
        result, _ = client.search_categories_broadly(site, filters)

        if result and isinstance(result, dict):
            categories = result.get('categories', [])

            # 过滤与关键词相关的类目
            if keyword:
                keyword_lower = keyword.lower()
                related_categories = []
                for cat in categories:
                    cat_name = cat.get('categoryName', '').lower()
                    if keyword_lower in cat_name or keyword_lower in cat.get('description', '').lower():
                        related_categories.append(cat)

                categories = related_categories[:max_categories]
            else:
                categories = categories[:max_categories]

            print(f"  ✓ 发现 {len(categories)} 个潜力类目:")
            for i, cat in enumerate(categories, 1):
                print(f"    {i}. {cat.get('categoryName', 'N/A')} "
                      f"(新品占比：{cat.get('newProductSalesAmountShare', 0)*100:.1f}%, "
                      f"Top3 占比：{cat.get('top3Product_sales_share', 0)*100:.1f}%)")

            return categories
        else:
            print(f"  ⚠ 未找到符合条件的类目")
            return []

    except Exception as e:
        print(f"  ⚠ 蓝海发现失败：{e} (非关键，继续执行)")
        return []


def find_potential_products(client, site, keyword, max_products=20):
    """
    【新增】潜力产品发现 - 使用 potential_product

    Args:
        client: SorftimeClient 实例
        site: 站点
        keyword: 产品关键词
        max_products: 返回的产品数量

    Returns:
        list: 潜力产品列表
    """
    print(f"\n[Step 1.3] 潜力产品发现：{keyword}...")

    # 筛选条件：有潜力的新品
    filters = {
        "monthlySales_min": 500,    # 月销量 > 500
        "price_min": 10,            # 价格 > $10
        "price_max": 50,            # 价格 < $50
        "rating_min": 4.0,          # 评分 > 4.0
        "daysOnMarket_max": 180,    # 上架时间 < 6 个月
    }

    try:
        result, _ = client.get_potential_products(site, keyword, **filters)

        if result and isinstance(result, dict):
            products = result.get('products', []) or result.get('productList', [])

            if not products:
                # 尝试不同的返回格式
                products = result.get('list', [])

            print(f"  ✓ 发现 {len(products)} 个潜力产品")

            # 显示 Top 5
            for i, p in enumerate(products[:5], 1):
                asin = p.get('ASIN', 'N/A')
                brand = p.get('品牌', 'N/A')
                sales = p.get('月销量', 'N/A')
                price = p.get('价格', 'N/A')
                rating = p.get('星级', 'N/A')
                days = p.get('上线天数', 'N/A')
                print(f"    {i}. {asin} | {brand} | 月销{sales} | ${price} | {rating}星 | {days}天")

            return products[:max_products]
        else:
            print(f"  ⚠ 未找到潜力产品")
            return []

    except Exception as e:
        print(f"  ⚠ 潜力产品发现失败：{e} (非关键，继续执行)")
        return []


def get_keyword_extends_data(client, site, keyword):
    """
    【新增】获取关键词延伸词 - 用于维度发现

    Args:
        client: SorftimeClient 实例
        site: 站点
        keyword: 关键词

    Returns:
        dict: 延伸词数据
    """
    print(f"\n[Step 1.4] 获取关键词延伸词：{keyword}...")

    try:
        result, _ = client.get_keyword_extends(site, keyword)

        if result:
            # 解析延伸词
            extends = result.get('extends', []) or result.get('keywords', []) or result.get('list', [])

            if isinstance(extends, list) and len(extends) > 0:
                print(f"  ✓ 获取 {len(extends)} 个延伸词")

                # 提取高频修饰词（用于维度发现）
                modifiers = []
                for item in extends:
                    if isinstance(item, dict):
                        word = item.get('keyword', item.get('word', ''))
                        search_volume = item.get('searchVolume', item.get('monthly_search', 0))
                    else:
                        word = str(item)
                        search_volume = 0

                    # 过滤掉品类通用词
                    if word and keyword.lower() not in word.lower():
                        modifiers.append({
                            'word': word,
                            'search_volume': search_volume
                        })

                # 按搜索量排序
                modifiers.sort(key=lambda x: x['search_volume'], reverse=True)

                print(f"  ✓ 提取 {len(modifiers)} 个修饰词（用于维度发现）")
                if modifiers:
                    print(f"    Top 5 修饰词：{', '.join([m['word'] for m in modifiers[:5]])}")

                return {
                    'extends': extends,
                    'modifiers': modifiers[:20]  # 保留 Top 20
                }

        print(f"  ⚠ 延伸词数据为空")
        return {}

    except Exception as e:
        print(f"  ⚠ 延伸词获取失败：{e} (非关键，继续执行)")
        return {}


def collect_data(keyword, site='US', max_keywords=3, use_blue_ocean=False):
    """
    执行完整的数据采集流程

    Args:
        keyword: 产品/类目关键词
        site: 站点代码 (US, GB, DE, etc.)
        max_keywords: 采集关键词数量
        use_blue_ocean: 是否启用蓝海发现模式

    Returns:
        dict: 采集结果摘要
    """
    print(f"🔍 选品数据采集：{keyword} ({site})")
    print("=" * 60)

    # 初始化
    client = SorftimeClient()
    output_dir, raw_dir, date_str = create_output_dir(keyword, site)

    # 结果摘要
    result = {
        'keyword': keyword,
        'site': site,
        'date': date_str,
        'category_name': None,
        'node_id': None,
        'steps_completed': [],
        'errors': [],
        'blue_ocean_categories': [],
        'potential_products': [],
        'keyword_extends': {}
    }

    # ========== Step 0.5: 蓝海市场发现（可选） ==========
    if use_blue_ocean:
        blue_ocean_cats = discover_blue_ocean_categories(client, site, keyword)
        if blue_ocean_cats:
            result['blue_ocean_categories'] = blue_ocean_cats
            save_json(blue_ocean_cats, os.path.join(raw_dir, 'blue_ocean_categories.json'))
            result['steps_completed'].append('blue_ocean_discovery')

    # ========== Step 1: 搜索类目 ==========
    print("\n[Step 1] 搜索类目...")

    category_result = None
    used_keyword = keyword

    try:
        print(f"  搜索: '{keyword}'...", end=' ')
        category_result, raw = client.search_category_by_product_name(site, keyword)

        if category_result and isinstance(category_result, list) and len(category_result) > 0:
            print(f"✓ 找到 {len(category_result)} 个类目")
        else:
            error_msg = f"类目搜索失败：未找到与 '{keyword}' 匹配的类目。请使用该类别最通用的核心名词（如使用 'camera' 而非 'digital wireless camera'）"
            print(f"  ✗ {error_msg}")
            raise Exception(error_msg)
    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        raise

    # 使用找到的类目
    first_cat = category_result[0]
    node_id = first_cat.get('nodeId') or first_cat.get('NodeId')
    category_name = first_cat.get('categoryName') or first_cat.get('Name')

    result['category_name'] = category_name
    result['node_id'] = str(node_id)
    result['searched_keyword'] = used_keyword  # 记录实际使用的搜索词

    print(f"  ✓ 最终类目：{category_name}")
    print(f"  ✓ Node ID: {node_id}")
    if used_keyword != keyword:
        print(f"  ℹ 使用搜索词: '{used_keyword}' (原词: '{keyword}')")

    save_json(category_result, os.path.join(raw_dir, 'category_info.json'))
    result['steps_completed'].append('category_search')

    # ========== Step 2: 获取 Top100 ==========
    print(f"\n[Step 2] 获取 Top100 产品数据...")
    top100 = None
    try:
        top100, raw_response = client.get_category_report(site, result['node_id'])

        # 检查返回的数据是否有效
        if top100 is None or not isinstance(top100, dict) or len(top100) == 0:
            raise ValueError("category_report 返回无效数据")

        products = top100.get('Top100产品', []) or top100.get('Top100 产品', []) or top100.get('products', [])
        stats = top100.get('类目统计报告', {})

        print(f"  ✓ 产品数量：{len(products)}")
        if stats:
            monthly_revenue = stats.get('top100 产品月销额', 0)
            print(f"  ✓ 类目月销额：${monthly_revenue}")

        save_json(top100, os.path.join(raw_dir, 'top100.json'))
        result['steps_completed'].append('top100')

    except Exception as e:
        # category_report 不可用时，使用 product_search 作为替代
        print(f"  ⚠ category_report 不可用，尝试使用 product_search 替代...")
        try:
            # 使用 product_search 工具获取产品数据
            search_result, _ = client._call('product_search', {
                'amzSite': site,
                'searchName': keyword,
                'page': 1
            })

            if isinstance(search_result, list) and len(search_result) > 0:
                # 构造类似 top100 的数据结构
                products = search_result

                # 计算类目统计数据
                total_monthly_sales = sum(p.get('月销量', 0) for p in products)
                total_monthly_revenue = sum(p.get('月销额', 0) for p in products)
                avg_price = total_monthly_revenue / len(products) if products else 0

                top100_data = {
                    'Top100产品': products,
                    '类目统计报告': {
                        'top100 产品月销额': total_monthly_revenue,
                        'top100 产品月销量': total_monthly_sales,
                        '平均价格': avg_price,
                        '产品数量': len(products),
                        '数据来源': 'product_search (替代 category_report)'
                    }
                }

                print(f"  ✓ 产品数量：{len(products)}")
                print(f"  ✓ 类目月销额：${total_monthly_revenue:,.2f}")
                print(f"  ℹ 注意：使用 product_search 数据（非完整 Top100）")

                save_json(top100_data, os.path.join(raw_dir, 'top100.json'))
                result['steps_completed'].append('top100')
            else:
                error_msg = f"product_search 返回空数据"
                print(f"  ✗ {error_msg}")
                result['errors'].append(error_msg)

        except Exception as e2:
            error_msg = f"Top100 获取失败（category_report 和 product_search 都失败）：{e}, {e2}"
            print(f"  ✗ {error_msg}")
            result['errors'].append(error_msg)

    # ========== Step 3: 获取趋势数据 ==========
    print(f"\n[Step 3] 获取类目趋势...")
    try:
        trend = client.get_category_trend(site, result['node_id'])
        if trend:
            print(f"  ✓ 趋势数据已获取")
            save_json(trend, os.path.join(raw_dir, 'trend.json'))
            result['steps_completed'].append('trend')
        else:
            print(f"  ⚠ 趋势数据为空（非关键）")
    except Exception as e:
        error_msg = f"趋势获取失败：{e}"
        print(f"  ⚠ {error_msg} (非关键)")
        result['errors'].append(error_msg)

    # ========== Step 4: 获取关键词详情（通用关键词生成） ==========
    print(f"\n[Step 4] 获取关键词详情...")
    keywords_data = {}

    def generate_keyword_variants(base_kw, max_count=5):
        """
        通用关键词变体生成策略

        策略：
        1. 原始词
        2. 尝试生成复数形式
        3. 添加常见修饰前缀
        """
        variants = [base_kw]

        # 复数形式生成（通用规则）
        # 规则1: 添加 's'
        if not base_kw.endswith('s'):
            variants.append(base_kw + 's')
        # 规则2: 以 y 结尾，变 'ies'
        if base_kw.endswith('y') and len(base_kw) > 1:
            variants.append(base_kw[:-1] + 'ies')
        # 规则3: 以 s, x, ch, sh 结尾，添加 'es'
        if base_kw.endswith(('s', 'x', 'ch', 'sh')):
            variants.append(base_kw + 'es')

        # 添加常见修饰前缀（完全通用）
        common_prefixes = ['portable', 'wireless', 'digital', 'smart']
        for prefix in common_prefixes:
            variants.append(f"{prefix} {base_kw}")

        # 去重并限制数量
        seen = set()
        unique_variants = []
        for v in variants:
            v_lower = v.lower().strip()
            if v_lower and v_lower not in seen and len(unique_variants) < max_count:
                seen.add(v_lower)
                unique_variants.append(v)

        return unique_variants

    base_keywords = generate_keyword_variants(keyword, max_keywords)

    for kw in base_keywords:
        try:
            print(f"  - {kw}...", end=' ', flush=True)
            kw_data, _ = client.get_keyword_detail(site, kw)
            if kw_data:
                keywords_data[kw] = kw_data
                print("✓")
            else:
                print("✗ (空响应)")
        except Exception as e:
            print(f"✗ ({str(e)[:50]})")

    if keywords_data:
        save_json(keywords_data, os.path.join(raw_dir, 'keywords.json'))
        result['steps_completed'].append('keywords')
        print(f"  ✓ 成功：{len(keywords_data)}/{len(base_keywords)} 个关键词")

    # ========== Step 5: 获取关键词延伸词（新增） ==========
    extends_data = get_keyword_extends_data(client, site, keyword)
    if extends_data:
        result['keyword_extends'] = extends_data
        save_json(extends_data, os.path.join(raw_dir, 'keyword_extends.json'))
        result['steps_completed'].append('keyword_extends')

    # ========== Step 6: 发现潜力产品（新增） ==========
    potential_products = find_potential_products(client, site, keyword)
    if potential_products:
        result['potential_products'] = potential_products
        save_json(potential_products, os.path.join(raw_dir, 'potential_products.json'))
        result['steps_completed'].append('potential_products')

    # ========== Step 7: 保存汇总数据 ==========
    print(f"\n[Step 7] 保存汇总数据...")

    summary = {
        "metadata": {
            "keyword": keyword,
            "site": site,
            "date": date_str,
            "node_id": result['node_id'],
            "category_name": result['category_name'],
            "collected_at": datetime.now().isoformat()
        },
        "files": {
            "category_info": "raw/category_info.json",
            "top100": "raw/top100.json",
            "trend": "raw/trend.json",
            "keywords": "raw/keywords.json",
            "keyword_extends": "raw/keyword_extends.json" if extends_data else None,
            "potential_products": "raw/potential_products.json" if potential_products else None,
            "blue_ocean_categories": "raw/blue_ocean_categories.json" if result['blue_ocean_categories'] else None
        },
        "status": "success" if len(result['errors']) == 0 else "partial",
        "steps_completed": result['steps_completed'],
        "errors": result['errors'],
        # 预留 Dashboard 需要的数据结构（初始为空，由后续分析填充）
        "market_overview": {},
        "price_ranges": [],
        "product_types": [],
        "cross_analysis": {"price_type_matrix": []},
        "top_brands": [],
        "competitors": [],
        "voc_analysis": {"dimensions": [], "summary": ""},
        "barriers": [],
        "decision": {},
        "trend_data": [],
        "keywords": {}
    }

    save_json(summary, os.path.join(output_dir, 'data.json'))

    # ========== 完成 ==========
    print("\n" + "=" * 60)
    print(f"✓ 数据采集完成!")
    print(f"  输出目录：{output_dir}")
    print(f"  完成步骤：{', '.join(result['steps_completed'])}")

    if result['errors']:
        print(f"\n⚠ 错误 ({len(result['errors'])}):")
        for err in result['errors']:
            print(f"  - {err}")

    print("=" * 60)

    return result


# ============================================================================
# 命令行接口
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="product-research 数据采集脚本（通用版本）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python collect_data.py "speaker" US
  python collect_data.py "sofa" DE --keywords 5
  python collect_data.py "mat" US --blue-ocean  # 启用蓝海发现
        """
    )

    parser.add_argument('keyword', help='产品/类目关键词')
    parser.add_argument('site', nargs='?', default='US', help='站点代码 (默认：US)')
    parser.add_argument('--keywords', '-k', type=int, default=3, help='采集关键词数量 (默认：3)')
    parser.add_argument('--blue-ocean', action='store_true', help='启用蓝海发现模式')

    args = parser.parse_args()

    collect_data(args.keyword, args.site, args.keywords, use_blue_ocean=args.blue_ocean)

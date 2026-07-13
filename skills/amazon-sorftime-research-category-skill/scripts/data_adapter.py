#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据结构适配器
将 sse_decoder.py 输出的中文键数据转换为 generate_excel_report.py 期望的英文键格式
"""

import json
import os
from typing import Dict, List


class DataAdapter:
    """将中文键数据转换为英文键数据"""

    # 评分键名映射
    SCORE_KEY_MAP = {
        '市场规模': 'market_size',
        '增长潜力': 'growth_potential',
        '竞争烈度': 'competition',
        '进入壁垒': 'entry_barrier',
        '利润空间': 'profit_margin',
        '总分': 'total',
        '评级': 'rating'
    }

    # 统计数据键名映射
    STATS_KEY_MAP = {
        '类目名称': 'category_name',
        'nodeid': 'node_id',
        'top100产品月销量': 'total_monthly_sales',
        'top100产品月销额': 'total_monthly_revenue',
        'average_price': 'average_price',
        'median_price': 'median_price',
        'top3_brands_sales_volume_share': 'top3_brand_share',
        'amazonOwned_sales_volume_share': 'amazon_own_share',
        'high_rated_sales_volume_share': 'high_rated_share',
        'low_reviews_sales_volume_share': 'low_reviews_share'
    }

    # 产品键名映射
    PRODUCT_KEY_MAP = {
        'ASIN': 'asin',
        '标题': 'title',
        '品牌': 'brand',
        '价格': 'price',
        '星级': 'rating',
        '评论数': 'review_count',
        '月销量': 'monthly_sales',
        '月销额': 'monthly_revenue',
        '卖家': 'seller',
        '卖家来源': 'seller_source',
        '上架天数': 'days_online',
        '类目排名': 'category_rank',
        '图片': 'image'
    }

    @classmethod
    def convert_scores(cls, scores: Dict) -> Dict:
        """转换评分数据"""
        converted = {}
        for cn_key, value in scores.items():
            en_key = cls.SCORE_KEY_MAP.get(cn_key, cn_key)
            converted[en_key] = value
        return converted

    @classmethod
    def convert_stats(cls, stats: Dict) -> Dict:
        """转换统计数据"""
        converted = {}
        for cn_key, value in stats.items():
            en_key = cls.STATS_KEY_MAP.get(cn_key, cn_key)
            converted[en_key] = value
        return converted

    @classmethod
    def convert_products(cls, products: List[Dict]) -> List[Dict]:
        """转换产品列表"""
        converted_list = []
        for p in products:
            converted = {}
            for cn_key, value in p.items():
                en_key = cls.PRODUCT_KEY_MAP.get(cn_key, cn_key)
                converted[en_key] = value
            converted_list.append(converted)
        return converted_list

    @classmethod
    def adapt_for_excel(cls, data_dir: str) -> Dict:
        """
        将 sse_decoder 输出的数据转换为 generate_excel_report 期望的格式

        Args:
            data_dir: 包含 data.json, top_products.json, scores.json 的目录

        Returns:
            适配后的数据字典
        """
        # 读取数据文件
        data_file = os.path.join(data_dir, 'data.json')
        products_file = os.path.join(data_dir, 'top_products.json')
        scores_file = os.path.join(data_dir, 'scores.json')

        with open(data_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        with open(products_file, 'r', encoding='utf-8') as f:
            raw_products = json.load(f)

        with open(scores_file, 'r', encoding='utf-8') as f:
            raw_scores = json.load(f)

        # 提取统计数据
        stats = raw_data.get('类目统计报告', {})

        # 转换评分
        five_dimension_score = cls.convert_scores(raw_scores)

        # 转换产品列表
        top100_products = cls.convert_products(raw_products)

        # 计算市场份额
        total_revenue = sum(p.get('monthly_revenue', 0) for p in top100_products)
        for p in top100_products:
            p['market_share'] = (p.get('monthly_revenue', 0) / total_revenue * 100) if total_revenue > 0 else 0

        # 构建品牌分析
        brand_data = cls._analyze_brands(top100_products)

        # 构建价格分布
        price_distribution = cls._analyze_price_distribution(top100_products)

        # 构建评分分布
        rating_distribution = cls._analyze_rating_distribution(top100_products)

        # 构建卖家分布
        seller_distribution = cls._analyze_seller_distribution(top100_products)

        # 构建新产品分析
        new_products = cls._filter_new_products(top100_products)

        # 构建KPI
        kpi = cls._build_kpi(stats, top100_products, brand_data)

        # 构建最终数据结构
        adapted_data = {
            'category_name': stats.get('类目名称', ''),
            'site': 'US',  # 默认，可以从外部传入
            'node_id': stats.get('nodeid', ''),
            'five_dimension_score': five_dimension_score,
            'kpi': kpi,
            'top100_products': top100_products,
            'brand_analysis': brand_data,
            'price_distribution': price_distribution,
            'rating_distribution': rating_distribution,
            'seller_distribution': seller_distribution,
            'new_products': new_products,
            # 趋势数据 (占位符)
            'sales_trend': {'dates': [], 'sales': []},
            'price_trend': {'dates': [], 'prices': []},
            'rating_trend': {'dates': [], 'ratings': []},
            'brand_count_trend': {'dates': [], 'count': []}
        }

        return adapted_data

    @staticmethod
    def _analyze_brands(products: List[Dict]) -> List[Dict]:
        """分析品牌数据"""
        brands = {}
        for p in products:
            brand = p.get('brand', 'Unknown')
            if brand not in brands:
                brands[brand] = {
                    'brand': brand,
                    'product_count': 0,
                    'monthly_sales': 0,
                    'monthly_revenue': 0,
                    'ratings': []
                }
            brands[brand]['product_count'] += 1
            brands[brand]['monthly_sales'] += p.get('monthly_sales', 0)
            brands[brand]['monthly_revenue'] += p.get('monthly_revenue', 0)
            if p.get('rating'):
                brands[brand]['ratings'].append(p['rating'])

        # 计算市场份额和平均评分
        total_revenue = sum(b['monthly_revenue'] for b in brands.values())
        result = []
        for b in brands.values():
            b['market_share'] = (b['monthly_revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            b['avg_rating'] = sum(b['ratings']) / len(b['ratings']) if b['ratings'] else 0
            result.append(b)

        # 按市场份额排序
        result.sort(key=lambda x: x['market_share'], reverse=True)
        return result

    @staticmethod
    def _analyze_price_distribution(products: List[Dict]) -> List[Dict]:
        """分析价格分布"""
        ranges = [
            {"name": "超低价", "min": 0, "max": 50},
            {"name": "低价", "min": 50, "max": 150},
            {"name": "中价", "min": 150, "max": 300},
            {"name": "高价", "min": 300, "max": 500},
            {"name": "超高价", "min": 500, "max": float('inf')},
        ]

        result = []
        for r in ranges:
            group_products = [p for p in products if r['min'] <= p.get('price', 0) < r['max']]
            count = len(group_products)
            sales = sum(p.get('monthly_sales', 0) for p in group_products)
            revenue = sum(p.get('monthly_revenue', 0) for p in group_products)
            ratings = [p.get('rating', 0) for p in group_products if p.get('rating')]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0

            result.append({
                'range': f"{r['name']} (${r['min']}-{r['max'] if r['max'] != float('inf') else '+'})",
                'count': count,
                'percentage': (count / len(products) * 100) if products else 0,
                'sales': sales,
                'revenue': revenue,
                'avg_rating': avg_rating
            })

        return result

    @staticmethod
    def _analyze_rating_distribution(products: List[Dict]) -> List[Dict]:
        """分析评分分布"""
        ranges = [
            {"name": "低分", "min": 0, "max": 3.5},
            {"name": "中低分", "min": 3.5, "max": 4.0},
            {"name": "中等", "min": 4.0, "max": 4.3},
            {"name": "中高分", "min": 4.3, "max": 4.7},
            {"name": "高分", "min": 4.7, "max": 5.0},
        ]

        result = []
        for r in ranges:
            group_products = [p for p in products if r['min'] <= p.get('rating', 0) < r['max']]
            count = len(group_products)
            sales = sum(p.get('monthly_sales', 0) for p in group_products)

            result.append({
                'range': f"{r['name']} ({r['min']}-{r['max']})",
                'count': count,
                'sales': sales,
                'sales_percentage': (sales / sum(p.get('monthly_sales', 0) for p in products) * 100) if products else 0
            })

        return result

    @staticmethod
    def _analyze_seller_distribution(products: List[Dict]) -> List[Dict]:
        """分析卖家来源分布"""
        sources = {}
        for p in products:
            source = p.get('seller_source', '其他')
            if source not in sources:
                sources[source] = {'seller_count': set(), 'product_count': 0, 'revenue': 0}
            sources[source]['seller_count'].add(p.get('seller', ''))
            sources[source]['product_count'] += 1
            sources[source]['revenue'] += p.get('monthly_revenue', 0)

        total_revenue = sum(s['revenue'] for s in sources.values())
        result = []
        for source, data in sources.items():
            result.append({
                'source': source,
                'seller_count': len(data['seller_count']),
                'product_count': data['product_count'],
                'revenue': data['revenue'],
                'percentage': (data['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            })

        result.sort(key=lambda x: x['revenue'], reverse=True)
        return result

    @staticmethod
    def _filter_new_products(products: List[Dict]) -> Dict:
        """筛选新产品 (评论数<100视为新品)"""
        new_products = [p for p in products if p.get('review_count', 0) < 100]
        new_product_sales = sum(p.get('monthly_sales', 0) for p in new_products)
        total_sales = sum(p.get('monthly_sales', 0) for p in products)

        return {
            'count': len(new_products),
            'percentage': (len(new_products) / len(products) * 100) if products else 0,
            'sales_share': (new_product_sales / total_sales * 100) if total_sales > 0 else 0,
            'avg_rating': sum(p.get('rating', 0) for p in new_products) / len(new_products) if new_products else 0
        }

    @staticmethod
    def _build_kpi(stats: Dict, products: List[Dict], brands: List[Dict]) -> Dict:
        """构建KPI指标"""
        # 计算CR3
        total_revenue = sum(p.get('monthly_revenue', 0) for p in products)
        top3_revenue = sum(b['monthly_revenue'] for b in brands[:3]) if len(brands) >= 3 else total_revenue
        cr3 = (top3_revenue / total_revenue * 100) if total_revenue > 0 else 0

        # 计算HHI
        hhi = sum((b['market_share'] / 100) ** 2 for b in brands) if brands else 0

        return {
            'total_products': len(products),
            'avg_price': sum(p.get('price', 0) for p in products) / len(products) if products else 0,
            'avg_sales': sum(p.get('monthly_sales', 0) for p in products) / len(products) if products else 0,
            'avg_rating': sum(p.get('rating', 0) for p in products) / len(products) if products else 0,
            'total_sales': total_revenue,
            'cr3': cr3,
            'hhi': hhi * 100  # 转换为百分比形式
        }


def main():
    """命令行入口"""
    import sys
    if len(sys.argv) < 2:
        print("用法: python data_adapter.py <数据目录> [输出文件]")
        print("\n示例:")
        print("  python data_adapter.py category-reports/Sofas_US_20260304")
        print("  python data_adapter.py category-reports/Sofas_US_20260304 adapted_data.json")
        sys.exit(1)

    data_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(data_dir, 'adapted_data.json')

    # 适配数据
    adapted_data = DataAdapter.adapt_for_excel(data_dir)

    # 保存适配后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(adapted_data, f, ensure_ascii=False, indent=2)

    print(f"适配后的数据已保存到: {output_file}")
    print("\n数据结构:")
    print(f"  - category_name: {adapted_data.get('category_name', 'N/A')}")
    print(f"  - five_dimension_score: {list(adapted_data.get('five_dimension_score', {}).keys())}")
    print(f"  - top100_products: {len(adapted_data.get('top100_products', []))} 个产品")
    print(f"  - brand_analysis: {len(adapted_data.get('brand_analysis', []))} 个品牌")


if __name__ == "__main__":
    main()

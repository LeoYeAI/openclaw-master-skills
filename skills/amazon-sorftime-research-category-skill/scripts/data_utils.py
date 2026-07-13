#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品类选品数据处理工具
包含: HHI计算、价格/评分分组、新产品筛选、增长率计算等
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


class DataProcessor:
    """品类数据处理工具类"""

    @staticmethod
    def calculate_hhi(brand_shares: Dict[str, float]) -> float:
        """
        计算HHI指数 (Herfindahl-Hirschman Index)

        Args:
            brand_shares: {品牌名: 市场份额百分比}

        Returns:
            HHI指数
        """
        hhi = 0
        for share in brand_shares.values():
            hhi += share ** 2
        return round(hhi, 2)

    @staticmethod
    def calculate_cr(brand_shares: Dict[str, float], top_n: int = 3) -> float:
        """
        计算CRn集中度 (Concentration Ratio)

        Args:
            brand_shares: {品牌名: 市场份额百分比}
            top_n: 前n个品牌

        Returns:
            CRn百分比
        """
        # 按市场份额降序排序
        sorted_brands = sorted(brand_shares.items(), key=lambda x: x[1], reverse=True)
        top_shares = sorted_brands[:top_n]
        cr = sum(share for _, share in top_shares)
        return round(cr, 2)

    @staticmethod
    def group_by_price_range(products: List[Dict], ranges: List[Dict] = None) -> List[Dict]:
        """
        按价格区间分组产品

        Args:
            products: 产品列表
            ranges: 自定义价格区间，默认为5个区间

        Returns:
            分组结果
        """
        if ranges is None:
            ranges = [
                {"name": "超低价", "min": 0, "max": 20},
                {"name": "低价", "min": 20, "max": 50},
                {"name": "中价", "min": 50, "max": 100},
                {"name": "高价", "min": 100, "max": 200},
                {"name": "超高价", "min": 200, "max": float('inf')},
            ]

        result = []
        for range_def in ranges:
            group = {
                "range": f"{range_def['name']} (${range_def['min']}-{range_def['max'] if range_def['max'] != float('inf') else '+'})",
                "count": 0,
                "sales": 0,
                "revenue": 0,
                "ratings": [],
                "products": []
            }

            for product in products:
                price = product.get("price", 0)
                if range_def['min'] <= price < range_def['max']:
                    group["count"] += 1
                    group["sales"] += product.get("monthly_sales", 0)
                    group["revenue"] += product.get("monthly_revenue", 0)
                    if product.get("rating"):
                        group["ratings"].append(product["rating"])
                    group["products"].append(product)

            # 计算占比和平均评分
            total_products = len(products)
            total_revenue = sum(p.get("monthly_revenue", 0) for p in products)

            group["percentage"] = round(group["count"] / total_products * 100, 1) if total_products > 0 else 0
            group["avg_rating"] = round(sum(group["ratings"]) / len(group["ratings"]), 2) if group["ratings"] else 0

            result.append(group)

        return result

    @staticmethod
    def group_by_rating_range(products: List[Dict], ranges: List[Dict] = None) -> List[Dict]:
        """
        按评分区间分组产品

        Args:
            products: 产品列表
            ranges: 自定义评分区间，默认为5个区间

        Returns:
            分组结果
        """
        if ranges is None:
            ranges = [
                {"name": "低分", "min": 0, "max": 3.5},
                {"name": "中低分", "min": 3.5, "max": 4.0},
                {"name": "中等", "min": 4.0, "max": 4.3},
                {"name": "中高分", "min": 4.3, "max": 4.7},
                {"name": "高分", "min": 4.7, "max": 5.0},
            ]

        result = []
        for range_def in ranges:
            group = {
                "range": f"{range_def['name']} ({range_def['min']}-{range_def['max']})",
                "count": 0,
                "sales": 0,
                "sales_percentage": 0
            }

            for product in products:
                rating = product.get("rating", 0)
                if range_def['min'] <= rating < range_def['max']:
                    group["count"] += 1
                    group["sales"] += product.get("monthly_sales", 0)

            # 计算占比
            total_sales = sum(p.get("monthly_sales", 0) for p in products)
            group["sales_percentage"] = round(group["sales"] / total_sales * 100, 1) if total_sales > 0 else 0
            group["percentage"] = round(group["count"] / len(products) * 100, 1) if products else 0

            result.append(group)

        return result

    @staticmethod
    def filter_new_products(products: List[Dict], days_threshold: int = 90) -> List[Dict]:
        """
        筛选新产品 (上架时间小于指定天数)

        Args:
            products: 产品列表
            days_threshold: 天数阈值，默认90天(3个月)

        Returns:
            新产品列表
        """
        today = datetime.now()
        threshold_date = today - timedelta(days=days_threshold)

        new_products = []
        for product in products:
            days_online = product.get("days_online", 0)
            if days_online and days_online <= days_threshold:
                new_products.append(product)

        return new_products

    @staticmethod
    def analyze_brand_distribution(products: List[Dict]) -> List[Dict]:
        """
        分析品牌分布

        Args:
            products: 产品列表

        Returns:
            品牌分析列表，按市场份额降序排序
        """
        brand_data = {}

        for product in products:
            brand = product.get("brand", "Unknown")
            if brand not in brand_data:
                brand_data[brand] = {
                    "brand": brand,
                    "product_count": 0,
                    "monthly_sales": 0,
                    "monthly_revenue": 0,
                    "ratings": []
                }

            brand_data[brand]["product_count"] += 1
            brand_data[brand]["monthly_sales"] += product.get("monthly_sales", 0)
            brand_data[brand]["monthly_revenue"] += product.get("monthly_revenue", 0)
            if product.get("rating"):
                brand_data[brand]["ratings"].append(product["rating"])

        # 计算总销额
        total_revenue = sum(b["monthly_revenue"] for b in brand_data.values())

        # 计算市场份额和平均评分
        for brand in brand_data.values():
            brand["market_share"] = round(brand["monthly_revenue"] / total_revenue * 100, 2) if total_revenue > 0 else 0
            brand["avg_rating"] = round(sum(brand["ratings"]) / len(brand["ratings"]), 2) if brand["ratings"] else 0

        # 按市场份额降序排序
        sorted_brands = sorted(brand_data.values(), key=lambda x: x["market_share"], reverse=True)

        return sorted_brands

    @staticmethod
    def analyze_seller_distribution(products: List[Dict]) -> Dict[str, Dict]:
        """
        分析卖家来源分布

        Args:
            products: 产品列表

        Returns:
            按来源地分组的统计数据
        """
        source_data = {
            "中国": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "美国": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "品牌": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "其他": {"seller_count": set(), "product_count": 0, "revenue": 0}
        }

        for product in products:
            seller = product.get("seller", "")
            source = product.get("seller_source", "其他")

            if source in source_data:
                source_data[source]["seller_count"].add(seller)
                source_data[source]["product_count"] += 1
                source_data[source]["revenue"] += product.get("monthly_revenue", 0)

        # 转换为列表格式
        result = []
        total_revenue = sum(s["revenue"] for s in source_data.values())

        for source, data in source_data.items():
            result.append({
                "source": source,
                "seller_count": len(data["seller_count"]),
                "product_count": data["product_count"],
                "revenue": data["revenue"],
                "percentage": round(data["revenue"] / total_revenue * 100, 1) if total_revenue > 0 else 0
            })

        # 按销额降序排序
        result.sort(key=lambda x: x["revenue"], reverse=True)

        return result

    @staticmethod
    def calculate_growth_rate(trend_data: List[Dict], period_months: int = 3) -> Dict[str, float]:
        """
        计算增长率和环比

        Args:
            trend_data: 趋势数据列表，每个元素包含 {date, value}
            period_months: 对比周期月数

        Returns:
            {同比增长率, 环比增长率}
        """
        if len(trend_data) < period_months + 1:
            return {"yoy": 0, "mom": 0}

        current_avg = sum(d["value"] for d in trend_data[-period_months:]) / period_months
        previous_avg = sum(d["value"] for d in trend_data[-(period_months*2+1):-period_months]) / period_months

        yoy = round((current_avg - previous_avg) / previous_avg * 100, 2) if previous_avg > 0 else 0

        # 环比 (上个月 vs 这个月)
        if len(trend_data) >= 2:
            last_month = trend_data[-1]["value"]
            prev_month = trend_data[-2]["value"]
            mom = round((last_month - prev_month) / prev_month * 100, 2) if prev_month > 0 else 0
        else:
            mom = 0

        return {"yoy": yoy, "mom": mom}

    @staticmethod
    def calculate_five_dimension_score(data: Dict) -> Dict[str, float]:
        """
        计算五维评分 (标准版本 - 与需求文档一致)

        评分标准:
        - 市场规模 (20分): >10M=20, >5M=17, >1M=14, 其他=10
        - 增长潜力 (25分): 低评论占比>40%=22, >20%=18, 其他=14
        - 竞争烈度 (20分): Top3<30%=18, <50%=14, 其他=8
        - 进入壁垒 (20分): Amazon占比+新品机会组合评分
        - 利润空间 (15分): 均价>$300=12, >$150=10, >$50=7, 其他=4

        Args:
            data: 包含所有市场数据的字典

        Returns:
            五维评分结果
        """
        scores = {}

        # 1. 市场规模 (20分) - 标准版本
        total_revenue = data.get("total_monthly_revenue", 0)
        if total_revenue > 10_000_000:
            scores["market_size"] = 20
        elif total_revenue > 5_000_000:
            scores["market_size"] = 17
        elif total_revenue > 1_000_000:
            scores["market_size"] = 14
        else:
            scores["market_size"] = 10

        # 2. 增长潜力 (25分) - 基于低评论产品占比
        low_review_share = data.get("low_reviews_sales_volume_share", 0)
        if low_review_share > 40:
            scores["growth_potential"] = 22
        elif low_review_share > 20:
            scores["growth_potential"] = 18
        else:
            scores["growth_potential"] = 14

        # 3. 竞争烈度 (20分) - 基于 Top3 品牌占比
        top3_share = data.get("top3_brands_sales_volume_share", 0)
        if top3_share < 30:
            scores["competition"] = 18
        elif top3_share < 50:
            scores["competition"] = 14
        else:
            scores["competition"] = 8

        # 4. 进入壁垒 (20分) - Amazon 占比 + 新品机会
        amazon_share = data.get("amazonOwned_sales_volume_share", 0)
        low_review_share = data.get("low_reviews_sales_volume_share", 0)

        barrier_score = 0
        # Amazon 占比越低，壁垒越小 (0-10分)
        if amazon_share < 20:
            barrier_score += 10
        elif amazon_share < 40:
            barrier_score += 6
        else:
            barrier_score += 3

        # 新品机会越大，壁垒越小 (0-10分)
        if low_review_share > 40:
            barrier_score += 10
        elif low_review_share > 20:
            barrier_score += 6
        else:
            barrier_score += 3

        scores["entry_barrier"] = barrier_score

        # 5. 利润空间 (15分) - 基于平均价格
        avg_price = data.get("average_price", 0)
        if avg_price > 300:
            scores["profit_margin"] = 12
        elif avg_price > 150:
            scores["profit_margin"] = 10
        elif avg_price > 50:
            scores["profit_margin"] = 7
        else:
            scores["profit_margin"] = 4

        # 计算总分
        scores["total"] = (
            scores["market_size"] +
            scores["growth_potential"] +
            scores["competition"] +
            scores["entry_barrier"] +
            scores["profit_margin"]
        )

        # 评级
        if scores["total"] >= 80:
            scores["rating"] = "优秀"
        elif scores["total"] >= 70:
            scores["rating"] = "良好"
        elif scores["total"] >= 50:
            scores["rating"] = "一般"
        else:
            scores["rating"] = "较差"

        return scores

    @staticmethod
    def prepare_html_data(data: Dict) -> Dict:
        """
        准备HTML报告所需的数据格式

        Args:
            data: 原始数据

        Returns:
            HTML模板变量字典
        """
        return {
            # 基础信息
            "CATEGORY_NAME": data.get("category_name", ""),
            "SITE": data.get("site", "US"),
            "DATA_DATE": datetime.now().strftime("%Y-%m-%d"),

            # 五维评分
            "MARKET_SIZE_SCORE": data.get("scores", {}).get("market_size", 0),
            "MARKET_SIZE_PERCENT": int(data.get("scores", {}).get("market_size", 0) / 20 * 100),
            "GROWTH_POTENTIAL_SCORE": data.get("scores", {}).get("growth_potential", 0),
            "GROWTH_POTENTIAL_PERCENT": int(data.get("scores", {}).get("growth_potential", 0) / 25 * 100),
            "COMPETITION_SCORE": data.get("scores", {}).get("competition", 0),
            "COMPETITION_PERCENT": int(data.get("scores", {}).get("competition", 0) / 20 * 100),
            "ENTRY_BARRIER_SCORE": data.get("scores", {}).get("entry_barrier", 0),
            "ENTRY_BARRIER_PERCENT": int(data.get("scores", {}).get("entry_barrier", 0) / 20 * 100),
            "PROFIT_MARGIN_SCORE": data.get("scores", {}).get("profit_margin", 0),
            "PROFIT_MARGIN_PERCENT": int(data.get("scores", {}).get("profit_margin", 0) / 15 * 100),
            "TOTAL_SCORE": data.get("scores", {}).get("total", 0),
            "RATING": data.get("rating", ""),
            "RECOMMENDATION": data.get("recommendation", ""),

            # KPI
            "TOTAL_PRODUCTS": data.get("total_products", 0),
            "AVG_PRICE": f"${data.get("avg_price", 0):.2f}",
            "AVG_SALES": f"{data.get("avg_sales", 0):.0f}",
            "AVG_RATING": f"{data.get("avg_rating", 0):.2f}",
            "TOTAL_SALES": f"${data.get("total_sales", 0):,.0f}",
            "CR3": f"{data.get("cr3", 0):.2f}",

            # 趋势数据 (需要JSON序列化)
            "SALES_TREND_DATA": json.dumps(data.get("sales_trend", {"dates": [], "sales": []})),
            "PRICE_TREND_DATA": json.dumps(data.get("price_trend", {"dates": [], "prices": []})),
            "PRICE_DIST_DATA": json.dumps(data.get("price_dist", [])),
            "RATING_DIST_DATA": json.dumps(data.get("rating_dist", {"ranges": [], "counts": []})),
            "BRAND_SHARE_DATA": json.dumps(data.get("brand_share", {"brands": [], "shares": []})),
            "SELLER_SOURCE_DATA": json.dumps(data.get("seller_source", [])),
            "BRAND_RATING_TREND_DATA": json.dumps(data.get("brand_rating_trend", {"brands": [], "dates": [], "data": {}})),
            "TOP50_PRODUCTS": json.dumps(data.get("top50_products", [])),

            # 关键发现
            "CONCENTRATION_LEVEL": data.get("concentration_level", ""),
            "HHI": f"{data.get('hhi', 0):.2f}",
            "CR3_RAW": f"{data.get('cr3_raw', 0)}",
            "CONCLUSION_CR3": data.get("conclusion_cr3", ""),
            "BRAND_COUNT": data.get("brand_count", 0),
            "BRAND_DIVERSITY": data.get("brand_diversity", ""),
            "NEW_PRODUCT_PERCENT": f"{data.get('new_product_percent', 0)}%",
            "NEW_PRODUCT_CONCLUSION": data.get("new_product_conclusion", ""),
            "SELLER_DISTRIBUTION": data.get("seller_distribution", ""),
            "COMPETITION_CONCLUSION": data.get("competition_conclusion", ""),
            "STRATEGY": data.get("strategy", ""),
            "GENERATED_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# 使用示例
if __name__ == "__main__":
    # 示例产品数据
    sample_products = [
        {"asin": "B001", "brand": "Sony", "price": 150, "rating": 4.5, "monthly_sales": 1000,
         "monthly_revenue": 150000, "seller": "Amazon", "seller_source": "品牌", "days_online": 45},
        {"asin": "B002", "brand": "Samsung", "price": 120, "rating": 4.2, "monthly_sales": 800,
         "monthly_revenue": 96000, "seller": "Seller1", "seller_source": "中国", "days_online": 200},
        {"asin": "B003", "brand": "LG", "price": 180, "rating": 4.6, "monthly_sales": 500,
         "monthly_revenue": 90000, "seller": "Seller2", "seller_source": "韩国", "days_online": 30},
    ]

    processor = DataProcessor()

    # 品牌分布分析
    brands = processor.analyze_brand_distribution(sample_products)
    print("品牌分布:", brands)

    # 价格分组
    price_groups = processor.group_by_price_range(sample_products)
    print("价格分组:", price_groups)

    # 评分分组
    rating_groups = processor.group_by_rating_range(sample_products)
    print("评分分组:", rating_groups)

    # 新产品筛选
    new_products = processor.filter_new_products(sample_products)
    print("新产品:", new_products)

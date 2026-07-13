#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品类选品 Markdown 分析报告生成器 v2.0 - 稳定增强版

生成完整的品类分析 Markdown 报告，包含:
- 五维评分分析
- 关键市场指标
- 品牌分析
- Top 产品列表
- 关键词分析
- 选品建议

主要改进:
1. 支持直接从 data.json 读取产品数据
2. 自动从产品列表计算统计数据
3. 更健壮的数据处理
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any


def safe_float(value, default=0.0):
    """安全地转换为浮点数"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def safe_int(value, default=0):
    """安全地转换为整数"""
    return int(safe_float(value, default))


class MarkdownReportGenerator:
    """Markdown 报告生成器"""

    def __init__(self, data_dir: str, category_name: str, site: str = 'US'):
        """
        初始化报告生成器

        Args:
            data_dir: 数据目录路径
            category_name: 品类名称
            site: 站点代码
        """
        self.data_dir = data_dir
        self.category_name = category_name
        self.site = site.upper()
        self.raw_data = {}
        self.products = []
        self.scores = {}
        self.keywords = []

    def load_data(self):
        """加载所有数据文件"""
        # 加载主数据文件
        data_file = os.path.join(self.data_dir, 'data.json')
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)

            # 从 raw_data 中提取产品列表
            # 支持多种可能的键名
            for key in ['Top100产品', '产品列表', 'products', 'items']:
                if key in self.raw_data and isinstance(self.raw_data[key], list):
                    raw_products = self.raw_data[key]
                    # 标准化产品数据
                    self.products = self._normalize_products(raw_products)
                    break

            # 如果没有找到产品列表，直接从 raw_data 处理
            if not self.products:
                # 检查是否是产品列表格式
                if isinstance(self.raw_data, list):
                    self.products = self._normalize_products(self.raw_data)
                # 检查是否是单个产品对象
                elif 'ASIN' in self.raw_data or 'asin' in self.raw_data:
                    self.products = self._normalize_products([self.raw_data])

        # 加载单独的产品文件（如果有）
        if not self.products:
            products_file = os.path.join(self.data_dir, 'top_products.json')
            if os.path.exists(products_file):
                with open(products_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)

        # 加载评分数据
        scores_file = os.path.join(self.data_dir, 'scores.json')
        if os.path.exists(scores_file):
            with open(scores_file, 'r', encoding='utf-8') as f:
                self.scores = json.load(f)

        # 加载关键词数据
        keywords_file = os.path.join(self.data_dir, 'keywords.json')
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r', encoding='utf-8') as f:
                self.keywords = json.load(f)

    def _normalize_products(self, raw_products: list) -> list:
        """标准化产品数据格式"""
        normalized = []
        for p in raw_products:
            if not isinstance(p, dict):
                continue

            # 提取标准化的字段
            product = {
                'ASIN': p.get('ASIN', ''),
                '标题': p.get('标题', p.get('title', ''))[:80],
                '价格': safe_float(p.get('价格', p.get('price', 0))),
                '月销量': safe_int(p.get('月销量', p.get('monthlySales', 0))),
                '月销额': safe_float(p.get('月销额', p.get('monthlyRevenue', 0))),
                '评分': safe_float(p.get('星级', p.get('评分', p.get('rating', 0)))),
                '品牌': p.get('品牌', p.get('brand', 'Unknown')),
                '评论数': safe_int(p.get('评论数', p.get('reviews', 0))),
                '卖家来源': p.get('卖家来源', p.get('sellerSource', '')),
                '卖家': p.get('卖家', p.get('seller', '')),
            }

            # 如果月销额为0但有价格和销量，计算月销额
            if product['月销额'] == 0 and product['价格'] > 0 and product['月销量'] > 0:
                product['月销额'] = product['价格'] * product['月销量']

            # 如果月销额为0但只有价格，估算
            if product['月销额'] == 0 and product['价格'] > 0:
                # 使用平均销量估算
                product['月销额'] = product['价格'] * 100  # 保守估计

            normalized.append(product)

        return normalized

    def calculate_metrics(self) -> Dict[str, Any]:
        """从产品列表计算市场指标"""
        metrics = {}

        if not self.products:
            return metrics

        # 计算总销额和销量
        total_revenue = sum(p.get('月销额', 0) for p in self.products)
        total_sales = sum(p.get('月销量', 0) for p in self.products)

        # 计算平均值
        prices = [p.get('价格', 0) for p in self.products if p.get('价格', 0) > 0]
        ratings = [p.get('评分', 0) for p in self.products if p.get('评分', 0) > 0]

        avg_price = sum(prices) / len(prices) if prices else 0
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        # 价格区间
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        # 品牌分析
        brand_stats = {}
        for p in self.products:
            brand = p.get('品牌', 'Unknown')
            if brand not in brand_stats:
                brand_stats[brand] = {'count': 0, 'revenue': 0}
            brand_stats[brand]['count'] += 1
            brand_stats[brand]['revenue'] += p.get('月销额', 0)

        # 按销额排序
        sorted_brands = sorted(brand_stats.items(), key=lambda x: x[1]['revenue'], reverse=True)

        # Top3 品牌份额
        top3_revenue = sum(v['revenue'] for k, v in sorted_brands[:3])
        top3_share = top3_revenue / total_revenue * 100 if total_revenue > 0 else 0

        # HHI 计算
        brand_shares = {k: v['revenue'] / total_revenue * 100 for k, v in brand_stats.items()} if total_revenue > 0 else {}
        hhi = sum(s**2 for s in brand_shares.values())

        # Amazon 占比
        amazon_products = [p for p in self.products if p.get('卖家', '') == 'Amazon']
        amazon_revenue = sum(p.get('月销额', 0) for p in amazon_products)
        amazon_share = amazon_revenue / total_revenue * 100 if total_revenue > 0 else 0

        # 低评论产品占比
        low_review_products = [p for p in self.products if p.get('评论数', 0) < 300]
        low_review_revenue = sum(p.get('月销额', 0) for p in low_review_products)
        low_review_share = low_review_revenue / total_revenue * 100 if total_revenue > 0 else 0

        # 卖家来源分析
        seller_sources = {}
        for p in self.products:
            source = p.get('卖家来源', '其他')
            if not source:
                # 根据卖家名称推断来源
                seller = p.get('卖家', '')
                if 'Amazon' in seller:
                    source = 'Amazon自营'
                elif any(kw in seller.lower() for kw in ['china', 'cn', 'chinese']):
                    source = '中国卖家'
                elif any(kw in seller.lower() for kw in ['usa', 'us', 'american']):
                    source = '美国卖家'
                else:
                    source = '其他'

            if source not in seller_sources:
                seller_sources[source] = {'count': 0, 'revenue': 0}
            seller_sources[source]['count'] += 1
            seller_sources[source]['revenue'] += p.get('月销额', 0)

        return {
            'total_revenue': total_revenue,
            'total_sales': total_sales,
            'avg_price': avg_price,
            'avg_rating': avg_rating,
            'min_price': min_price,
            'max_price': max_price,
            'product_count': len(self.products),
            'brand_count': len(brand_stats),
            'sorted_brands': sorted_brands,
            'top3_share': top3_share,
            'hhi': hhi,
            'amazon_share': amazon_share,
            'low_review_share': low_review_share,
            'seller_sources': seller_sources,
        }

    def generate(self) -> str:
        """生成完整的 Markdown 报告"""
        self.load_data()
        metrics = self.calculate_metrics()

        # 使用评分数据（如果有）或计算新评分
        if self.scores:
            scores = self.scores
            total_score = safe_int(scores.get('总分', 0))
            rating = scores.get('评级', '未知')
        else:
            # 计算评分
            scores = self._calculate_scores(metrics)
            total_score = scores['total']
            rating = scores['rating']

        report = f"""# {self.category_name} 品类选品分析报告

**站点**: {self.site} | **分析日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 执行摘要

| 指标 | 数值 |
|------|------|
| **总分** | **{total_score}/100** |
| **评级** | **{rating}** |
| **建议** | **{self._get_recommendation(total_score)}** |
| 月市场规模 | \${metrics.get('total_revenue', 0):,.0f} |
| Top100 月销量 | {metrics.get('total_sales', 0):,} |
| 平均价格 | \${metrics.get('avg_price', 0):.2f} |
| 平均评分 | {metrics.get('avg_rating', 0):.2f} |

---

## 五维评分分析

### 评分概览

| 维度 | 得分 | 满分 | 说明 |
|------|------|------|------|
| 市场规模 | {scores.get('市场规模', 0)}/20 | 20 | {self._get_market_size_desc(metrics.get('total_revenue', 0))} |
| 增长潜力 | {scores.get('增长潜力', 0)}/25 | 25 | 低评论产品占比: {metrics.get('low_review_share', 0):.1f}% |
| 竞争烈度 | {scores.get('竞争烈度', 0)}/20 | 20 | Top3 品牌占比: {metrics.get('top3_share', 0):.1f}% |
| 进入壁垒 | {scores.get('进入壁垒', 0)}/20 | 20 | Amazon 占比: {metrics.get('amazon_share', 0):.1f}% |
| 利润空间 | {scores.get('利润空间', 0)}/15 | 15 | 平均价格: \${metrics.get('avg_price', 0):.2f} |

### 详细分析

#### 1. 市场规模 (得分: {scores.get('市场规模', 0)}/20)
- **月总销额**: \${metrics.get('total_revenue', 0):,.0f}
- **月总销量**: {metrics.get('total_sales', 0):,}
- **市场规模评估**: {self._get_market_size_desc(metrics.get('total_revenue', 0))}

#### 2. 增长潜力 (得分: {scores.get('增长潜力', 0)}/25)
- **低评论产品销额占比**: {metrics.get('low_review_share', 0):.1f}%
- **新品机会**: {'较高' if metrics.get('low_review_share', 0) > 20 else '一般'}
- **分析**: 低评论产品占比{'较高' if metrics.get('low_review_share', 0) > 20 else '较低'}，说明{'存在较多新品机会' if metrics.get('low_review_share', 0) > 20 else '市场较成熟，新品进入难度大'}

#### 3. 竞争烈度 (得分: {scores.get('竞争烈度', 0)}/20)
- **HHI 指数**: {metrics.get('hhi', 0):.1f} ({'高度集中' if metrics.get('hhi', 0) > 1800 else '中度集中' if metrics.get('hhi', 0) > 1000 else '低度集中'})
- **Top3 品牌份额**: {metrics.get('top3_share', 0):.1f}%
- **品牌数量**: {metrics.get('brand_count', 0)} 个

**竞争格局**: {'高度垄断，竞争激烈' if metrics.get('top3_share', 0) > 50 else '中度集中，有一定机会' if metrics.get('top3_share', 0) > 30 else '竞争分散，机会较多'}

#### 4. 进入壁垒 (得分: {scores.get('进入壁垒', 0)}/20)
- **Amazon 自营占比**: {metrics.get('amazon_share', 0):.1f}%

**进入难度**: {'较低' if metrics.get('amazon_share', 0) < 20 else '中等' if metrics.get('amazon_share', 0) < 40 else '较高'}

#### 5. 利润空间 (得分: {scores.get('利润空间', 0)}/15)
- **平均价格**: \${metrics.get('avg_price', 0):.2f}
- **价格区间**: \${metrics.get('min_price', 0):.2f} - \${metrics.get('max_price', 0):.2f}
- **利润评估**: {self._get_profit_desc(metrics.get('avg_price', 0))}

---

## 品牌分析

### Top 10 品牌

| 排名 | 品牌 | 产品数 | 月销额 | 市场份额 |
|------|------|--------|--------|----------|
"""

        # 添加品牌数据
        sorted_brands = metrics.get('sorted_brands', [])
        total_revenue = metrics.get('total_revenue', 1)

        for i, (brand, stats) in enumerate(sorted_brands[:10], 1):
            share = stats['revenue'] / total_revenue * 100 if total_revenue > 0 else 0
            report += f"| {i} | {brand} | {stats['count']} | \${stats['revenue']:,.0f} | {share:.2f}% |\n"

        report += f"""

### 品牌集中度分析

- **CR3 (Top3 集中度)**: {metrics.get('top3_share', 0):.2f}% - {'高度垄断' if metrics.get('top3_share', 0) > 50 else '中度集中' if metrics.get('top3_share', 0) > 30 else '竞争分散'}
- **HHI 指数**: {metrics.get('hhi', 0):.1f}

**主要竞争者**:
"""

        for i, (brand, stats) in enumerate(sorted_brands[:5], 1):
            share = stats['revenue'] / total_revenue * 100 if total_revenue > 0 else 0
            report += f"{i}. **{brand}**: 市场份额 {share:.2f}%, {stats['count']} 款产品\n"

        report += f"""

---

## Top 20 产品详情

| 排名 | ASIN | 品牌 | 价格 | 月销量 | 月销额 | 评分 | 评论数 |
|------|------|------|------|--------|--------|------|--------|
"""

        for i, p in enumerate(self.products[:20], 1):
            asin = p.get('ASIN', 'N/A')
            brand = p.get('品牌', 'N/A')[:15]
            price = p.get('价格', 0)
            sales = p.get('月销量', 0)
            revenue = p.get('月销额', 0)
            rating = p.get('评分', 0)
            reviews = p.get('评论数', 0)

            report += f"| {i} | {asin} | {brand} | \${price:.2f} | {sales:,} | \${revenue:,.0f} | {rating} | {reviews} |\n"

        report += f"""

---

## 卖家来源分析

| 来源 | 产品数 | 销额占比 |
|------|--------|----------|
"""

        seller_sources = metrics.get('seller_sources', {})
        total_revenue = metrics.get('total_revenue', 1)

        for source, stats in sorted(seller_sources.items(), key=lambda x: x[1]['revenue'], reverse=True):
            share = stats['revenue'] / total_revenue * 100 if total_revenue > 0 else 0
            report += f"| {source} | {stats['count']} | {share:.2f}% |\n"

        # 添加关键词分析（如果有）
        if self.keywords:
            report += f"""

---

## 关键词分析

### Top 15 核心关键词

| 排名 | 关键词 | 月搜索量 | 周搜索量 |
|------|--------|----------|----------|
"""
            for i, kw in enumerate(self.keywords[:15], 1):
                kw_name = kw.get('关键词', kw.get('keyword', 'N/A'))
                monthly = safe_int(kw.get('月搜索量', kw.get('monthlySearchVolume', 0)))
                weekly = safe_int(kw.get('周搜索量', kw.get('weeklySearchVolume', 0)))
                report += f"| {i} | {kw_name} | {monthly:,} | {weekly:,} |\n"

        report += f"""

---

## 市场机会与策略建议

### 优势
{self._generate_advantages(metrics)}

### 劣势
{self._generate_disadvantages(metrics)}

### 机会
{self._generate_opportunities(metrics)}

### 威胁
{self._generate_threats(metrics)}

### 选品建议
{self._generate_recommendations(metrics, scores)}

---

## 结论

**综合评分**: {total_score}/100 ({rating})

**最终建议**: {self._get_recommendation(total_score)}

**理由**:
{self._generate_conclusion(metrics, rating)}

**适合卖家**: {self._get_suitable_seller_profile(metrics, total_score)}

**不适合卖家**: {self._get_unsuitable_seller_profile(metrics, total_score)}

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源: Sorftime MCP*
"""

        return report

    def _calculate_scores(self, metrics: Dict) -> Dict:
        """计算五维评分"""
        scores = {}

        # 市场规模
        revenue = metrics.get('total_revenue', 0)
        if revenue > 10_000_000:
            scores['市场规模'] = 20
        elif revenue > 5_000_000:
            scores['市场规模'] = 17
        elif revenue > 1_000_000:
            scores['市场规模'] = 14
        else:
            scores['市场规模'] = 10

        # 增长潜力
        low_review_share = metrics.get('low_review_share', 0)
        if low_review_share > 40:
            scores['增长潜力'] = 22
        elif low_review_share > 20:
            scores['增长潜力'] = 18
        else:
            scores['增长潜力'] = 14

        # 竞争烈度
        top3_share = metrics.get('top3_share', 0)
        if top3_share < 30:
            scores['竞争烈度'] = 18
        elif top3_share < 50:
            scores['竞争烈度'] = 14
        else:
            scores['竞争烈度'] = 8

        # 进入壁垒
        amazon_share = metrics.get('amazon_share', 0)
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
        avg_price = metrics.get('avg_price', 0)
        if avg_price > 300:
            scores['利润空间'] = 12
        elif avg_price > 150:
            scores['利润空间'] = 10
        elif avg_price > 50:
            scores['利润空间'] = 7
        else:
            scores['利润空间'] = 4

        scores['total'] = sum(scores.values())

        if scores['total'] >= 80:
            scores['rating'] = '优秀'
        elif scores['total'] >= 70:
            scores['rating'] = '良好'
        elif scores['total'] >= 50:
            scores['rating'] = '一般'
        else:
            scores['rating'] = '较差'

        return scores

    def _get_market_size_desc(self, revenue: float) -> str:
        """获取市场规模描述"""
        if revenue > 10_000_000:
            return '> $10M (优秀)'
        elif revenue > 5_000_000:
            return '> $5M (良好)'
        elif revenue > 1_000_000:
            return '> $1M (一般)'
        return '< $1M (较差)'

    def _get_profit_desc(self, avg_price: float) -> str:
        """获取利润空间描述"""
        if avg_price > 300:
            return '高价值品类，利润空间大'
        elif avg_price > 150:
            return '中高价值，利润可观'
        elif avg_price > 50:
            return '中低端，利润一般'
        return '低价品类，利润空间小'

    def _get_recommendation(self, score: int) -> str:
        """获取建议"""
        if score >= 80:
            return '强烈推荐进入'
        elif score >= 70:
            return '可以考虑进入'
        elif score >= 50:
            return '谨慎进入'
        return '不建议进入'

    def _generate_advantages(self, metrics: Dict) -> str:
        """生成优势分析"""
        advantages = []
        revenue = metrics.get('total_revenue', 0)
        avg_price = metrics.get('avg_price', 0)

        if revenue > 10_000_000:
            advantages.append(f"1. **市场规模巨大**: 月销额超过 \${revenue/1_000_000:.1f}M，属于高流量品类")
        elif revenue > 1_000_000:
            advantages.append(f"1. **市场规模可观**: 月销额达 \${revenue/1_000_000:.1f}M")

        price_range = f"\${metrics.get('min_price', 0):.0f}-\${metrics.get('max_price', 0):.0f}"
        advantages.append(f"2. **价格带丰富**: {price_range} 价格区间，满足不同消费需求")

        return '\n'.join(advantages) if advantages else "暂无明显优势"

    def _generate_disadvantages(self, metrics: Dict) -> str:
        """生成劣势分析"""
        disadvantages = []
        top3_share = metrics.get('top3_share', 0)

        if top3_share > 50:
            disadvantages.append(f"1. **品牌集中度极高**: Top3 品牌占据 {top3_share:.1f}% 市场份额")

        amazon_share = metrics.get('amazon_share', 0)
        if amazon_share > 20:
            disadvantages.append(f"2. **Amazon 竞争**: Amazon 自营占比 {amazon_share:.1f}%")

        low_review_share = metrics.get('low_review_share', 0)
        if low_review_share < 20:
            disadvantages.append("3. **新品机会有限**: 市场成熟，低评论产品占比低")

        return '\n'.join(disadvantages) if disadvantages else "暂无明显劣势"

    def _generate_opportunities(self, metrics: Dict) -> str:
        """生成机会分析"""
        opportunities = []
        low_review_share = metrics.get('low_review_share', 0)

        if low_review_share > 20:
            opportunities.append("1. **新品机会**: 低评论产品占比较高，存在新品进入空间")
        else:
            opportunities.append("1. **细分市场**: 寻找未被满足的细分需求")

        top3_share = metrics.get('top3_share', 0)
        if top3_share < 50:
            opportunities.append("2. **品牌分散**: 竞争格局相对分散，有机会脱颖而出")

        avg_price = metrics.get('avg_price', 0)
        if avg_price > 100:
            opportunities.append("3. **中端市场**: \$$100-\$$300 价格区间有一定机会")

        return '\n'.join(opportunities) if opportunities else "需要深入调研寻找机会"

    def _generate_threats(self, metrics: Dict) -> str:
        """生成威胁分析"""
        threats = []

        top3_share = metrics.get('top3_share', 0)
        if top3_share > 70:
            threats.append("1. **头部品牌垄断**: 市场被少数品牌主导，新进入者竞争困难")

        amazon_share = metrics.get('amazon_share', 0)
        if amazon_share > 30:
            threats.append("2. **Amazon 自营压力**: 与 Amazon 自营产品直接竞争")

        avg_price = metrics.get('avg_price', 0)
        if avg_price < 50:
            threats.append("3. **价格战风险**: 低价品类利润空间小，容易陷入价格战")

        return '\n'.join(threats) if threats else "暂无明显威胁"

    def _generate_recommendations(self, metrics: Dict, scores: Dict) -> str:
        """生成选品建议"""
        total_score = scores.get('total', 0)
        avg_price = metrics.get('avg_price', 0)

        if total_score >= 70:
            return """**可以考虑的方向**:
- 该品类综合评分较高，值得深入研究
- 建议从中端价格区间切入
- 关注差异化产品定位

**注意事项**:
- 注意避开头部品牌强势产品线
- 确保供应链有成本优势"""
        elif total_score >= 50:
            return f"""**谨慎考虑的方向**:
- \${avg_price:.0f}-\${avg_price*1.5:.0f} 价格区间的产品
- 寻找细分市场机会

**建议谨慎**:
- 竞争较激烈，需要仔细评估
- 建议先小规模测试"""
        else:
            return """**不建议进入**:
- 该品类综合评分较低
- 建议寻找其他更合适的品类

**如仍想尝试**:
- 需要有强大的供应链优势
- 建议从配件或细分市场入手"""

    def _generate_conclusion(self, metrics: Dict, rating: str) -> str:
        """生成结论"""
        revenue = metrics.get('total_revenue', 0)
        top3_share = metrics.get('top3_share', 0)
        avg_price = metrics.get('avg_price', 0)

        if revenue > 1_000_000:
            desc = f"月销额达 \${revenue/1_000_000:.1f}M+"
        else:
            desc = f"月销额达 \${revenue:,.0f}"

        competition = "极其激烈" if top3_share > 50 else "较为激烈" if top3_share > 30 else "相对分散"
        value = "高价值" if avg_price > 300 else "中高价值" if avg_price > 150 else "中低端"

        return f"""{self.category_name} 品类是一个{value}市场，{desc}。但市场竞争{competition}{'，头部品牌占据主导地位' if top3_share > 50 else '，仍有进入机会'}。"""

    def _get_suitable_seller_profile(self, metrics: Dict, score: int) -> str:
        """获取适合的卖家画像"""
        if score >= 70:
            return "有一定资金实力、有供应链资源、有运营经验的卖家"
        elif score >= 50:
            return "有特定品类经验、能找到差异化定位的卖家"
        return "不推荐新手卖家进入"

    def _get_unsuitable_seller_profile(self, metrics: Dict, score: int) -> str:
        """获取不适合的卖家画像"""
        return "新手卖家、无供应链资源的小卖家、资金有限的卖家"

    def save(self, output_file: str = None):
        """保存报告到文件"""
        if output_file is None:
            output_file = os.path.join(self.data_dir, 'report.md')

        report = self.generate()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return output_file


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python generate_markdown_report.py <数据目录> [品类名称] [站点] [输出文件]")
        print("\n示例:")
        print("  python generate_markdown_report.py category-reports/Sofas_US_20260304")
        print("  python generate_markdown_report.py category-reports/Sofas_US_20260304 'Sofas' US report.md")
        sys.exit(1)

    data_dir = sys.argv[1]
    category_name = sys.argv[2] if len(sys.argv) > 2 else 'Unknown Category'
    site = sys.argv[3] if len(sys.argv) > 3 else 'US'
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    generator = MarkdownReportGenerator(data_dir, category_name, site)
    saved_file = generator.save(output_file)

    print(f"✓ 报告已生成: {saved_file}")


if __name__ == "__main__":
    main()

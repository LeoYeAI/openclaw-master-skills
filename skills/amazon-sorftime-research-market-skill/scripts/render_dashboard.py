#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard 渲染器 - 为 product-research 生成可视化看板

修复版本 v3.1 - 适配实际 data.json 数据结构

使用方式:
    from scripts.render_dashboard import DashboardRenderer
    renderer = DashboardRenderer()
    renderer.render("path/to/data.json")

输出:
    dashboard.html - 可在浏览器中直接打开的交互式看板
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class DashboardRenderer:
    """Dashboard 渲染器"""

    @staticmethod
    def validate_analysis_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证分析数据完整性

        返回: (is_complete, missing_fields)
        - is_complete: 数据是否完整
        - missing_fields: 缺失的字段列表
        """
        missing = []

        # 检查决策评估数据
        decision = data.get('decision', data.get('go_nogo', {}))
        if not decision.get('overall_score') and not decision.get('total_score'):
            missing.append('decision.overall_score')

        # 检查 VOC 分析数据
        voc = data.get('voc_analysis', {})
        if not voc.get('dimensions'):
            missing.append('voc_analysis.dimensions')

        # 检查壁垒评估数据
        barriers = data.get('barriers', [])
        if not barriers or (isinstance(barriers, list) and len(barriers) == 0):
            missing.append('barriers')

        # 检查交叉分析数据
        cross = data.get('cross_analysis', {})
        if not cross.get('price_type_matrix'):
            missing.append('cross_analysis.price_type_matrix')

        is_complete = len(missing) == 0
        return is_complete, missing

    # HTML 模板
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{CATEGORY}} - {{SITE}} 选品分析看板</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            color: #1a1a1a;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e1e8ef;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8px;
        }

        .header .subtitle {
            font-size: 14px;
            color: #64748b;
        }

        .section {
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e1e8ef;
        }

        /* KPI 卡片网格 */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .kpi-card {
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }

        .kpi-card .label {
            font-size: 12px;
            color: #64748b;
            margin-bottom: 8px;
        }

        .kpi-card .value {
            font-size: 24px;
            font-weight: 700;
            color: #1a1a1a;
        }

        .kpi-card .note {
            font-size: 11px;
            color: #94a3b8;
            margin-top: 4px;
        }

        /* Go/No-Go 评分卡 */
        .gogono-card {
            background: linear-gradient(135deg, {{GO_GRADIENT}} 100%);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            color: white;
        }

        .gogono-card .score {
            font-size: 48px;
            font-weight: 700;
            margin: 12px 0;
        }

        .gogono-card .verdict {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .gogono-card .verdict-detail {
            font-size: 14px;
            opacity: 0.9;
        }

        /* 表格样式 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e1e8ef;
        }

        th {
            background: #f8fafc;
            font-weight: 600;
            color: #475569;
        }

        tr:hover {
            background: #f8fafc;
        }

        /* 标签 */
        .tag {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }

        .tag-green { background: #dcfce7; color: #166534; }
        .tag-yellow { background: #fef9c3; color: #854d0e; }
        .tag-red { background: #fee2e2; color: #991b1b; }
        .tag-blue { background: #dbeafe; color: #1e40af; }
        .tag-gray { background: #f1f5f9; color: #475569; }

        /* 机会卡片 */
        .opportunity-card {
            background: #f0fdf4;
            border-left: 4px solid #16a34a;
            padding: 16px;
            margin-bottom: 12px;
            border-radius: 4px;
        }

        .opportunity-card .rank {
            display: inline-block;
            width: 24px;
            height: 24px;
            background: #16a34a;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-weight: 600;
            margin-right: 12px;
        }

        /* 页脚 */
        .footer {
            text-align: center;
            padding: 24px;
            color: #64748b;
            font-size: 13px;
            border-top: 1px solid #e1e8ef;
            margin-top: 40px;
        }

        /* 维度分布表格 */
        .dimension-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        /* 响应式 */
        @media (max-width: 768px) {
            .kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .dimension-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{{CATEGORY}} 选品分析看板</h1>
            <div class="subtitle">
                站点: {{SITE}} | 分析日期: {{DATA_DATE}}
            </div>
        </div>

        <!-- Go/No-Go 评分 -->
        <div class="section">
            <div class="section-title">选品决策评估</div>
            <div class="gogono-card" style="background: linear-gradient(135deg, {{GO_GRADIENT}} 100%);">
                <div class="verdict">{{GOGO_VERDICT}}</div>
                <div class="score">{{GOGO_SCORE}}</div>
                <div class="verdict-detail">{{GOGO_DETAIL}}</div>
            </div>
        </div>

        <!-- 市场概况 KPI -->
        <div class="section">
            <div class="section-title">市场概况</div>
            <div class="kpi-grid">
                {{KPI_CARDS}}
            </div>
        </div>

        <!-- 维度分布 -->
        <div class="section">
            <div class="section-title">产品维度分布</div>
            {{DIMENSION_TABLES}}
        </div>

        <!-- 交叉分析 -->
        {{CROSS_ANALYSIS_SECTION}}

        <!-- VOC 分析 -->
        {{VOC_SECTION}}

        <!-- 竞品格局 -->
        {{COMPETITOR_SECTION}}

        <!-- 进入壁垒 -->
        {{BARRIERS_SECTION}}

        <!-- 页脚 -->
        <div class="footer">
            <p>数据来源: Sorftime MCP | 生成时间: {{GENERATED_TIME}}</p>
            <p>完整报告请查看 Markdown 文件</p>
        </div>
    </div>

    <script>
        // 页面交互脚本
        console.log('Dashboard loaded successfully');
    </script>
</body>
</html>
"""

    def __init__(self):
        """初始化渲染器"""
        self.template = self.HTML_TEMPLATE

    def _load_data(self, data_path: str) -> Dict[str, Any]:
        """加载分析数据"""
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _render_kpi_cards(self, market_overview: Dict) -> str:
        """渲染 KPI 卡片"""
        kpis = [
            ('Top100 月销量', f"{market_overview.get('top100_monthly_sales', 0):,}", '件'),
            ('Top100 月销额', f"${market_overview.get('top100_monthly_revenue', 0):,.0f}", ''),
            ('平均价格', f"${market_overview.get('avg_price', 0):.2f}", ''),
            ('Top3 品牌集中度', f"{market_overview.get('top3_brand_concentration', 0)*100:.1f}%", ''),
            ('亚马逊自营份额', f"{market_overview.get('amazon_owned_share', 0)*100:.1f}%", ''),
            ('中国卖家份额', f"{market_overview.get('chinese_seller_share', 0)*100:.1f}%", ''),
        ]

        cards_html = []
        for label, value, note in kpis:
            cards_html.append(f'''
                <div class="kpi-card">
                    <div class="label">{label}</div>
                    <div class="value">{value}</div>
                    <div class="note">{note}</div>
                </div>
            ''')

        return ''.join(cards_html)

    def _render_dimension_tables(self, data: Dict) -> str:
        """渲染产品维度分布表格 - 适配实际数据结构"""
        # 从价格区间和产品类型数据生成表格
        price_ranges = data.get('price_ranges', [])
        product_types = data.get('product_types', [])
        dimensions = data.get('dimensions', [])

        tables_html = '<div class="dimension-grid">'

        # 价格区间表格
        if price_ranges:
            total = sum(p.get('count', 0) for p in price_ranges)
            rows = ''
            for pr in price_ranges:
                range_label = pr.get('range', '')
                count = pr.get('count', 0)
                share = pr.get('share', 0) * 100

                if share >= 30:
                    tag_class = 'tag-blue'
                elif share >= 20:
                    tag_class = 'tag-green'
                elif share >= 10:
                    tag_class = 'tag-yellow'
                else:
                    tag_class = 'tag-gray'

                rows += f'<tr><td>{range_label}</td><td>{count}</td><td><span class="tag {tag_class}">{share:.0f}%</span></td></tr>'

            tables_html += f'''
                <div>
                    <h4 style="margin-bottom: 12px; color: #475569; font-size: 14px;">价格区间分布</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>价格区间</th>
                                <th>产品数</th>
                                <th>占比</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </div>
            '''

        # 产品类型表格
        if product_types:
            total = sum(pt.get('count', 0) for pt in product_types)
            rows = ''
            for pt in product_types:
                type_name = pt.get('type', '')
                count = pt.get('count', 0)
                share = pt.get('share', 0) * 100

                if share >= 30:
                    tag_class = 'tag-blue'
                elif share >= 20:
                    tag_class = 'tag-green'
                elif share >= 10:
                    tag_class = 'tag-yellow'
                else:
                    tag_class = 'tag-gray'

                rows += f'<tr><td>{type_name}</td><td>{count}</td><td><span class="tag {tag_class}">{share:.0f}%</span></td></tr>'

            tables_html += f'''
                <div>
                    <h4 style="margin-bottom: 12px; color: #475569; font-size: 14px;">产品类型分布</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>产品类型</th>
                                <th>产品数</th>
                                <th>占比</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </div>
            '''

        tables_html += '</div>'
        return tables_html

    def _render_cross_analysis(self, data: Dict) -> str:
        """渲染交叉分析部分 - 使用实际数据结构"""
        cross_analysis = data.get('cross_analysis', {})
        price_type_matrix = cross_analysis.get('price_type_matrix', [])

        if not price_type_matrix:
            return ''

        # 从矩阵数据中提取列（产品类型）
        product_types = set()
        price_ranges = []

        for row in price_type_matrix:
            price_range = row.get('price_range', '')
            if price_range not in price_ranges:
                price_ranges.append(price_range)
            # 获取除 price_range 外的所有键作为产品类型
            for key in row.keys():
                if key != 'price_range':
                    product_types.add(key)

        product_types = sorted(list(product_types))

        # 生成表头
        header_cols = ''.join(f'<th>{pt}</th>' for pt in product_types)

        # 生成表格行
        rows = ''
        for price_range in price_ranges:
            # 找到对应的价格区间行
            row_data = next((r for r in price_type_matrix if r.get('price_range') == price_range), {})
            row_cells = ''
            row_total = 0

            for pt in product_types:
                count = row_data.get(pt, 0)
                row_total += count

                # 标记特殊值
                if count == 0:
                    cell_content = '<span class="tag tag-gray">0</span>'
                elif count >= 15:
                    cell_content = f'{count} <span class="tag tag-red" style="font-size: 10px;">红海</span>'
                else:
                    cell_content = str(count)

                row_cells += f'<td>{cell_content}</td>'

            rows += f'<tr><td><strong>{price_range}</strong></td>{row_cells}<td><strong>{row_total}</strong></td></tr>'

        # 计算列合计
        col_totals = []
        for pt in product_types:
            col_total = sum(r.get(pt, 0) for r in price_type_matrix)
            col_totals.append(col_total)

        total_row = ''.join(f'<td><strong>{t}</strong></td>' for t in col_totals)
        grand_total = sum(col_totals)

        # 获取机会和红海信息
        opportunities = cross_analysis.get('opportunities', [])
        red_ocean = cross_analysis.get('red_ocean', [])

        insight_text = []
        if red_ocean:
            for ro in red_ocean:
                insight_text.append(f"<strong>红海:</strong> {ro.get('combination', '')} ({ro.get('products', 0)}款)")
        if opportunities:
            for opp in opportunities:
                insight_text.append(f"<strong>机会:</strong> {opp.get('combination', '')} ({opp.get('status', '')})")

        insight_html = f'<div style="margin-top: 16px; padding: 12px; background: #fefce8; border-radius: 8px; font-size: 13px; color: #854d0e;"><strong>洞察：</strong>{" | ".join(insight_text)}</div>' if insight_text else ''

        return f'''
        <div class="section">
            <div class="section-title">价格区间 × 产品类型 交叉分析</div>
            <table>
                <thead>
                    <tr>
                        <th>价格区间 \\ 产品类型</th>
                        {header_cols}
                        <th>合计</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                    <tr style="background: #f8fafc; font-weight: 600;">
                        <td><strong>合计</strong></td>
                        {total_row}
                        <td><strong>{grand_total}</strong></td>
                    </tr>
                </tbody>
            </table>
            {insight_html}
        </div>
        '''

    def _render_voc_analysis(self, voc_analysis: Dict) -> str:
        """渲染 VOC 分析"""
        if not voc_analysis or not voc_analysis.get('dimensions'):
            return ''

        dimensions = voc_analysis.get('dimensions', [])
        summary = voc_analysis.get('summary', '')

        rows = ''
        for dim in dimensions:
            dimension = dim.get('dimension', '')
            pain_point = dim.get('pain_point', '')
            frequency = dim.get('frequency', 0)
            percentage = dim.get('percentage', '')
            affected_brands = ', '.join(dim.get('affected_brands', []))
            brand_opportunity = dim.get('brand_opportunity', '')
            product_solution = dim.get('product_solution', '')

            rows += f'''
                <tr>
                    <td><strong>{dimension}</strong></td>
                    <td>{pain_point}</td>
                    <td>{frequency}<br><small>{percentage}</small></td>
                    <td>{affected_brands}</td>
                    <td>{brand_opportunity}</td>
                    <td>{product_solution}</td>
                </tr>
            '''

        summary_html = f'<div style="margin-top: 12px; padding: 12px; background: #f0f9ff; border-radius: 8px; font-size: 13px; color: #0369a1;"><strong>总结：</strong>{summary}</div>' if summary else ''

        return f'''
        <div class="section">
            <div class="section-title">VOC 分析 - 用户痛点洞察</div>
            <table>
                <thead>
                    <tr>
                        <th>维度</th>
                        <th>痛点</th>
                        <th>频次/占比</th>
                        <th>涉及品牌</th>
                        <th>品牌机会</th>
                        <th>产品方案</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            {summary_html}
        </div>
        '''

    def _render_competitors(self, competitors: List[Dict]) -> str:
        """渲染竞品格局 - 适配实际数据结构"""
        if not competitors:
            return ''

        rows = ''
        for comp in competitors[:8]:
            asin = comp.get('asin', '')
            brand = comp.get('brand', '')
            model = comp.get('model', '')
            price = comp.get('price', 0)
            monthly_sales = comp.get('monthly_sales', 0)
            type_label = comp.get('type', '')
            positioning = comp.get('positioning', '')

            rows += f'''
                <tr>
                    <td>{brand}<br><small>{model}</small></td>
                    <td>${price:.2f}</td>
                    <td>{monthly_sales:,}</td>
                    <td>{type_label}</td>
                    <td><small>{positioning}</small></td>
                </tr>
            '''

        return f'''
        <div class="section">
            <div class="section-title">竞品格局 (Top8)</div>
            <table>
                <thead>
                    <tr>
                        <th>品牌/型号</th>
                        <th>价格</th>
                        <th>月销量</th>
                        <th>类型</th>
                        <th>定位</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        '''

    def _render_barriers(self, barriers: List[Dict]) -> str:
        """渲染进入壁垒 - 适配实际数据结构"""
        if not barriers:
            return ''

        rows = ''
        for barrier in barriers:
            barrier_type = barrier.get('type', '')
            level = barrier.get('level', '中')
            level_class = {'高': 'tag-red', '中': 'tag-yellow', '低': 'tag-green'}.get(level, 'tag-gray')
            cost = barrier.get('estimated_cost', 'N/A')
            data_anchor = barrier.get('data_anchor', '')
            solution = barrier.get('solution', '')

            rows += f'''
                <tr>
                    <td>{barrier_type}</td>
                    <td><span class="tag {level_class}">{level}</span></td>
                    <td>{cost}</td>
                    <td><small>{data_anchor}</small></td>
                    <td>{solution}</td>
                </tr>
            '''

        return f'''
        <div class="section">
            <div class="section-title">进入壁垒评估</div>
            <table>
                <thead>
                    <tr>
                        <th>壁垒类型</th>
                        <th>等级</th>
                        <th>预估成本</th>
                        <th>数据锚点</th>
                        <th>缓解方案</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        '''

    def render(self, data_path: str, output_path: Optional[str] = None) -> str:
        """
        渲染 Dashboard

        Args:
            data_path: data.json 文件路径
            output_path: 输出 HTML 文件路径，默认与 data.json 同目录

        Returns:
            str: 生成的 HTML 文件路径
        """
        # 加载数据
        data = self._load_data(data_path)

        # 验证分析数据完整性
        is_complete, missing = self.validate_analysis_data(data)

        if not is_complete:
            print(f"⚠️  数据不完整，缺少分析字段: {', '.join(missing)}")
            print(f"ℹ️  将渲染基础版本（不含分析结论）")
            print(f"ℹ️  完成分析后请使用 --final 参数重新渲染")

        # 解析数据 - 适配实际结构
        metadata = data.get('metadata', {})
        market_overview = data.get('market_overview', {})
        # 兼容新旧字段名：decision 或 go_nogo
        decision = data.get('decision', data.get('go_nogo', {}))
        competitors = data.get('competitors', [])
        voc_analysis = data.get('voc_analysis', {})
        barriers = data.get('barriers', [])

        # 解析数据 - 适配实际结构
        metadata = data.get('metadata', {})
        market_overview = data.get('market_overview', {})
        # 兼容新旧字段名：decision 或 go_nogo
        decision = data.get('decision', data.get('go_nogo', {}))
        competitors = data.get('competitors', [])
        voc_analysis = data.get('voc_analysis', {})
        barriers = data.get('barriers', [])

        # 确定输出路径
        if output_path is None:
            data_dir = Path(data_path).parent
            output_path = data_dir / 'dashboard.html'

        # 准备模板变量
        # 兼容新旧字段名：keyword 或 category 或 category_name
        category = metadata.get('category', metadata.get('category_name', metadata.get('keyword', 'Unknown')))
        site = metadata.get('site', 'US')
        data_date = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Go/No-Go 样式映射
        # 兼容新旧字段名：verdict 或 decision
        verdict = decision.get('verdict', decision.get('decision', '暂缓观望'))
        # 兼容新旧字段名：overall_score 或 total_score
        score = decision.get('overall_score', decision.get('total_score', 0))

        verdict_mapping = {
            '建议进入': '#22c55e, #16a34a',
            '谨慎进入': '#f59e0b, #d97706',
            '暂缓观望': '#64748b, #475569',
            '不建议进入': '#ef4444, #dc2626',
        }

        go_gradient = verdict_mapping.get(verdict, '#64748b, #475569')

        # 决策详情 - 兼容新旧字段名
        scores = decision.get('dimensions', decision.get('scores', []))
        decision_basis = decision.get('decision_text', decision.get('decision_basis', ''))
        verdict_detail = decision_basis if decision_basis else verdict

        # KPI 卡片
        kpi_cards = self._render_kpi_cards(market_overview)

        # 维度分布表格
        dimension_tables = self._render_dimension_tables(data)

        # 交叉分析
        cross_section = self._render_cross_analysis(data)

        # VOC 分析
        voc_section = self._render_voc_analysis(voc_analysis)

        # 竞品格局
        competitor_section = self._render_competitors(competitors)

        # 进入壁垒
        barriers_section = self._render_barriers(barriers)

        # 渲染模板
        html = self.template.replace('{{CATEGORY}}', category) \
            .replace('{{SITE}}', site) \
            .replace('{{DATA_DATE}}', data_date) \
            .replace('{{GENERATED_TIME}}', datetime.now().strftime('%Y-%m-%d %H:%M')) \
            .replace('{{GO_GRADIENT}}', go_gradient) \
            .replace('{{GOGO_VERDICT}}', verdict) \
            .replace('{{GOGO_SCORE}}', f'{score:.1f} / 10') \
            .replace('{{GOGO_DETAIL}}', verdict_detail) \
            .replace('{{KPI_CARDS}}', kpi_cards) \
            .replace('{{DIMENSION_TABLES}}', dimension_tables) \
            .replace('{{CROSS_ANALYSIS_SECTION}}', cross_section) \
            .replace('{{VOC_SECTION}}', voc_section) \
            .replace('{{COMPETITOR_SECTION}}', competitor_section) \
            .replace('{{BARRIERS_SECTION}}', barriers_section)

        # 写入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path)


# ============================================================================
# 命令行接口
# ============================================================================

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Dashboard 渲染器 - 为选品分析生成可视化看板",
        epilog="""
示例:
  # 渲染 Dashboard（自动检测数据完整性）
  python render_dashboard.py data.json

  # 检查数据完整性（不生成文件）
  python render_dashboard.py data.json --check

  # 指定输出路径
  python render_dashboard.py data.json -o output/dashboard.html
        """
    )
    parser.add_argument("data", help="data.json 文件路径")
    parser.add_argument("-o", "--output", help="输出 HTML 文件路径")
    parser.add_argument("--check", action="store_true", help="仅检查数据完整性，不生成文件")

    args = parser.parse_args()

    renderer = DashboardRenderer()

    # 仅检查模式
    if args.check:
        data = renderer._load_data(args.data)
        is_complete, missing = renderer.validate_analysis_data(data)

        if is_complete:
            print("✓ 数据完整，可以渲染完整版 Dashboard")
            print(f"  包含: decision.overall_score, voc_analysis.dimensions, barriers, cross_analysis")
            sys.exit(0)
        else:
            print("⚠️  数据不完整，缺少以下字段:")
            for field in missing:
                print(f"  - {field}")
            print(f"\nℹ️  请先完成 LLM 分析，然后重新运行渲染")
            sys.exit(1)

    # 渲染模式
    output_path = renderer.render(args.data, args.output)

    print(f"✓ Dashboard 已生成: {output_path}")

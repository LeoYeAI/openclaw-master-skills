#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用创意投放效果诊断脚本
支持任何平台的 CSV 报表，通过用户提供的列映射进行解析。
"""
import pandas as pd
import numpy as np
import argparse
import json
import os
import re
from datetime import datetime
from collections import Counter
import sys,io

# 在 Windows 下设置控制台编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def parse_arguments():
    parser = argparse.ArgumentParser(description='通用创意投放效果诊断')
    parser.add_argument('--file', required=True, help='数据文件路径 (CSV)')
    parser.add_argument('--platform', default='通用平台', help='平台名称，用于报告标题')
    parser.add_argument('--config', help='JSON配置文件，包含列映射')
    # 列映射参数（优先级高于配置文件）
    parser.add_argument('--id-col', help='素材ID列名')
    parser.add_argument('--name-col', help='素材名称列名')
    parser.add_argument('--impressions-col', help='展现量列名')
    parser.add_argument('--clicks-col', help='点击量列名')
    parser.add_argument('--spend-col', help='花费列名')
    parser.add_argument('--revenue-col', help='成交金额列名')
    parser.add_argument('--orders-col', help='成交笔数列名')
    parser.add_argument('--cart-col', help='购物车数列名 (可选)')
    parser.add_argument('--favorite-col', help='收藏数列名 (可选)')
    parser.add_argument('--date-col', help='日期列名 (可选)')
    return parser.parse_args()


def load_column_mapping(args):
    """从配置文件或命令行参数加载列映射"""
    mapping = {}
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
    # 命令行参数覆盖
    for key in ['id', 'name', 'impressions', 'clicks', 'spend', 'revenue', 'orders', 'cart', 'favorite', 'date']:
        arg_val = getattr(args, f"{key}_col", None)
        if arg_val:
            mapping[key] = arg_val
    return mapping


def safe_divide(a, b):
    """安全除法，避免除零"""
    return a / b if b != 0 else 0


def analyze_generic(df, mapping, platform_name):
    """通用分析函数"""
    # 重命名列为标准名称
    rename_dict = {v: k for k, v in mapping.items() if
                   k in ['id', 'name', 'impressions', 'clicks', 'spend', 'revenue', 'orders', 'cart', 'favorite',
                         'date']}
    df = df.rename(columns=rename_dict)

    # 检查必要列
    required = ['id', 'name', 'impressions', 'clicks', 'spend', 'revenue', 'orders']
    missing = [r for r in required if r not in df.columns]
    if missing:
        return f"错误：缺少必要列 {missing}，请检查映射。"

    # 数值列转换
    numeric_cols = ['impressions', 'clicks', 'spend', 'revenue', 'orders', 'cart', 'favorite']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 处理日期列
    date_range = None
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        min_date = df['date'].min()
        max_date = df['date'].max()
        if pd.notna(min_date) and pd.notna(max_date):
            date_range = (min_date.strftime('%Y-%m-%d'), max_date.strftime('%Y-%m-%d'))

    # 按素材分组聚合
    agg_dict = {
        'impressions': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'revenue': 'sum',
        'orders': 'sum',
    }
    if 'cart' in df.columns:
        agg_dict['cart'] = 'sum'
    if 'favorite' in df.columns:
        agg_dict['favorite'] = 'sum'

    grouped = df.groupby(['id', 'name']).agg(agg_dict).reset_index()

    # 计算衍生指标
    grouped['ctr'] = grouped.apply(lambda r: safe_divide(r['clicks'], r['impressions']), axis=1)
    grouped['cvr'] = grouped.apply(lambda r: safe_divide(r['orders'], r['clicks']), axis=1)
    grouped['roi'] = grouped.apply(lambda r: safe_divide(r['revenue'], r['spend']), axis=1)
    grouped['cpc'] = grouped.apply(lambda r: safe_divide(r['spend'], r['clicks']), axis=1)
    if 'cart' in grouped.columns:
        grouped['cart_rate'] = grouped.apply(lambda r: safe_divide(r['cart'], r['clicks']), axis=1)
    if 'favorite' in grouped.columns:
        grouped['fav_cost'] = grouped.apply(lambda r: safe_divide(r['spend'], r['favorite']), axis=1)

    grouped = grouped.fillna(0)

    # 整体汇总
    total = {
        'impressions': grouped['impressions'].sum(),
        'clicks': grouped['clicks'].sum(),
        'spend': grouped['spend'].sum(),
        'revenue': grouped['revenue'].sum(),
        'orders': grouped['orders'].sum(),
    }
    if 'cart' in grouped.columns:
        total['cart'] = grouped['cart'].sum()
    if 'favorite' in grouped.columns:
        total['favorite'] = grouped['favorite'].sum()
    total['ctr'] = safe_divide(total['clicks'], total['impressions'])
    total['cvr'] = safe_divide(total['orders'], total['clicks'])
    total['roi'] = safe_divide(total['revenue'], total['spend'])
    total['cpc'] = safe_divide(total['spend'], total['clicks'])

    avg_ctr = total['ctr']
    avg_cvr = total['cvr']

    grouped['ctr_rating'] = grouped['ctr'].apply(
        lambda x: '高' if x > avg_ctr else ('中' if x > avg_ctr * 0.8 else '低')
    )
    grouped['cvr_rating'] = grouped['cvr'].apply(
        lambda x: '高' if x > avg_cvr else ('中' if x > avg_cvr * 0.8 else '低')
    )

    def quadrant(row):
        if row['ctr_rating'] == '高' and row['cvr_rating'] == '高':
            return '明星素材'
        elif row['ctr_rating'] == '高' and row['cvr_rating'] in ['中', '低']:
            return '引流型素材'
        elif row['ctr_rating'] in ['中', '低'] and row['cvr_rating'] == '高':
            return '转化型素材'
        else:
            return '问题素材'

    grouped['quadrant'] = grouped.apply(quadrant, axis=1)
    top_roi = grouped.nlargest(10, 'roi').reset_index(drop=True)
    bottom_roi = grouped.nsmallest(10, 'roi').reset_index(drop=True)
    word_counter = Counter()
    for name in grouped['name']:
        words = re.split(r'[，。！？、\s\|,，;；:：()（）【】「」]+', str(name))
        for w in words:
            w = w.strip()
            if w and len(w) > 1:
                word_counter[w] += 1
    top_words = word_counter.most_common(20)
    analysis_keywords = [w for w, _ in top_words[:10]]

    report = []
    report.append(f"# 投放素材效果诊断报告 ({datetime.now().strftime('%Y-%m-%d')})")
    report.append(f"**分析平台**: {platform_name}")
    if date_range:
        report.append(f"**数据期间**: {date_range[0]} 至 {date_range[1]}")
    report.append(f"**分析素材数**: {len(grouped)} 个")
    report.append("")
    report.append("## 1. 整体表现概览")
    report.append("| 指标 | 数值 |")
    report.append("|------|------|")
    report.append(f"| 展现量 | {total['impressions']:,.0f} |")
    report.append(f"| 点击量 | {total['clicks']:,.0f} |")
    report.append(f"| 花费 (元) | {total['spend']:.2f} |")
    report.append(f"| 成交金额 (元) | {total['revenue']:.2f} |")
    report.append(f"| 成交笔数 | {total['orders']:,.0f} |")
    if 'cart' in total:
        report.append(f"| 购物车数 | {total['cart']:,.0f} |")
    if 'favorite' in total:
        report.append(f"| 收藏数 | {total['favorite']:,.0f} |")
    report.append(f"| 点击率 (CTR) | {total['ctr']:.2%} |")
    report.append(f"| 点击转化率 (CVR) | {total['cvr']:.2%} |")
    report.append(f"| 投入产出比 (ROI) | {total['roi']:.2f} |")
    report.append(f"| 平均点击花费 (CPC) | {total['cpc']:.2f} 元 |")
    report.append("")
    report.append("## 2. 素材表现排名")
    report.append("### ROI Top 10")
    report.append("| 排名 | 素材名称 | ROI | CTR | CVR | 花费 | 成交额 |")
    report.append("|------|----------|-----|-----|-----|------|--------|")
    for i, row in top_roi.iterrows():
        report.append(f"| {i + 1} | {row['name']} | {row['roi']:.2f} | {row['ctr']:.2%} | {row['cvr']:.2%} | {row['spend']:.2f} | {row['revenue']:.2f} |")
    report.append("")
    report.append("### ROI Bottom 10")
    report.append("| 排名 | 素材名称 | ROI | CTR | CVR | 花费 | 成交额 |")
    report.append("|------|----------|-----|-----|-----|------|--------|")
    for i, row in bottom_roi.iterrows():
        report.append(f"| {i + 1} | {row['name']} | {row['roi']:.2f} | {row['ctr']:.2%} | {row['cvr']:.2%} | {row['spend']:.2f} | {row['revenue']:.2f} |")
    report.append("")
    report.append("## 3. 素材分类分析")
    quadrant_counts = grouped['quadrant'].value_counts()
    for q, cnt in quadrant_counts.items():
        report.append(f"- **{q}**: {cnt} 个")
    report.append("")
    star = grouped[grouped['quadrant'] == '明星素材']
    if not star.empty:
        report.append("### 明星素材")
        report.append("| 素材名称 | CTR | CVR | ROI | 花费 | 成交额 |")
        report.append("|----------|-----|-----|-----|------|--------|")
        for _, row in star.nlargest(5, 'roi').iterrows():
            report.append(f"| {row['name']} | {row['ctr']:.2%} | {row['cvr']:.2%} | {row['roi']:.2f} | {row['spend']:.2f} | {row['revenue']:.2f} |")
        report.append("")
    traffic = grouped[grouped['quadrant'] == '引流型素材']
    if not traffic.empty:
        report.append("### 引流型素材")
        report.append("| 素材名称 | CTR | CVR | ROI | 花费 | 成交额 |")
        report.append("|----------|-----|-----|-----|------|--------|")
        for _, row in traffic.nlargest(5, 'ctr').iterrows():
            report.append(f"| {row['name']} | {row['ctr']:.2%} | {row['cvr']:.2%} | {row['roi']:.2f} | {row['spend']:.2f} | {row['revenue']:.2f} |")
        report.append("")
    convert = grouped[grouped['quadrant'] == '转化型素材']
    if not convert.empty:
        report.append("### 转化型素材")
        report.append("| 素材名称 | CTR | CVR | ROI | 花费 | 成交额 |")
        report.append("|----------|-----|-----|-----|------|--------|")
        for _, row in convert.nlargest(5, 'cvr').iterrows():
            report.append(f"| {row['name']} | {row['ctr']:.2%} | {row['cvr']:.2%} | {row['roi']:.2f} | {row['spend']:.2f} | {row['revenue']:.2f} |")
        report.append("")
    poor = grouped[grouped['quadrant'] == '问题素材']
    if not poor.empty:
        report.append("### 问题素材")
        report.append("| 素材名称 | CTR | CVR | ROI | 花费 | 成交额 |")
        report.append("|----------|-----|-----|-----|------|--------|")
        for _, row in poor.nsmallest(5, 'roi').iterrows():
            report.append(f"| {row['name']} | {row['ctr']:.2%} | {row['cvr']:.2%} | {row['roi']:.2f} | {row['spend']:.2f} | {row['revenue']:.2f} |")
        report.append("")

    report.append("## 4. 创意关键词洞察")
    if top_words:
        report.append("高频词（TOP20）：")
        report.append("| 关键词 | 出现次数 |")
        report.append("|--------|----------|")
        for word, count in top_words:
            report.append(f"| {word} | {count} |")
        report.append("")
        report.append("关键词平均表现对比：")
        report.append("| 关键词 | 素材数 | 平均CTR | 平均CVR | 平均ROI |")
        report.append("|--------|--------|---------|---------|---------|")
        for kw in analysis_keywords:
            mask = grouped['name'].str.contains(kw, na=False, regex=False)
            if mask.sum() >= 2:
                avg_ctr_kw = grouped.loc[mask, 'ctr'].mean()
                avg_cvr_kw = grouped.loc[mask, 'cvr'].mean()
                avg_roi_kw = grouped.loc[mask, 'roi'].mean()
                report.append(f"| {kw} | {mask.sum()} | {avg_ctr_kw:.2%} | {avg_cvr_kw:.2%} | {avg_roi_kw:.2f} |")
        report.append("")

    report.append("## 5. 综合优化建议")
    if not star.empty:
        report.append(f"- **放大优势**: 明星素材（如「{star.iloc[0]['name']}」等）建议增加预算、复制创意元素。")
    if not traffic.empty:
        report.append("- **优化转化**: 引流型素材建议检查落地页匹配度，强化促销信息。")
    if not convert.empty:
        report.append("- **提升点击**: 转化型素材建议优化封面和标题。")
    if not poor.empty:
        report.append("- **暂停重构**: 问题素材建议暂停投放，重新构思。")

    return "\n".join(report)

def main():
    args = parse_arguments()
    mapping = load_column_mapping(args)

    try:
        df = pd.read_csv(args.file, encoding='utf-8-sig')
    except (UnicodeDecodeError, TypeError):
        try:
            df = pd.read_csv(args.file, encoding='gbk')
        except Exception as e:
            print(f"错误：无法读取文件。\n{e}")
            return

    report = analyze_generic(df, mapping, args.platform)
    print(report)

if __name__ == "__main__":
    main()

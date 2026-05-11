"""
案例3：多股票批量对比
场景：对比多只股票的行情指标 + 归一化走势 + 相关性热力图
输出：第一步表格 → 第二步图表（show_widget 渲染）
"""

from thsdk import THS
from collections import defaultdict
import pandas as pd
import numpy as np

# ── 配置：要对比的股票 ────────────────────────────────────────
STOCK_NAMES = ["贵州茅台", "五粮液", "泸州老窖", "山西汾酒"]
KLINE_DAYS  = 30      # 对比走势天数
ADJUST      = "forward"  # 前复权（量化对比推荐）

# ── 1. 批量解析代码 ──────────────────────────────────────────
stock_list = []   # [{'name': '贵州茅台', 'code': 'USHA600519'}, ...]

with THS() as ths:
    for name in STOCK_NAMES:
        resp = ths.search_symbols(name)
        if not resp or not resp.data:
            print(f"⚠️ 未找到：{name}")
            continue
        a_shares = [s for s in resp.data
                    if any(m in s.get('MarketDisplay', '') for m in ['沪A', '深A'])]
        if not a_shares:
            print(f"⚠️ {name} 无A股数据")
            continue
        # 多只A股时取第一只，实际使用时可让用户选择
        stock_list.append({'name': name, 'code': a_shares[0]['THSCODE']})

    print(f"已解析 {len(stock_list)} 只股票：{[s['name'] for s in stock_list]}")

    # ── 2. 按市场分组批量查行情（market_data_cn 要求同市场） ──
    by_market = defaultdict(list)
    for s in stock_list:
        by_market[s['code'][:4]].append(s)

    quote_rows = []
    for market, stocks in by_market.items():
        codes = [s['code'] for s in stocks]
        resp = ths.market_data_cn(codes, "汇总")
        if not resp:
            print(f"⚠️ 行情查询失败：{resp.error}")
            continue
        for i, row in enumerate(resp.data):
            row['股票名称'] = stocks[i]['name']
            quote_rows.append(row)

    quote_df = pd.DataFrame(quote_rows)

    # ── 3. 批量拉日K线 ────────────────────────────────────────
    klines_data = {}
    for s in stock_list:
        resp = ths.klines(s['code'], interval="day", count=KLINE_DAYS, adjust=ADJUST)
        if resp and not resp.df.empty:
            klines_data[s['name']] = resp.df
        else:
            print(f"⚠️ {s['name']} K线获取失败")

# ── 4. 第一步：关键指标表格 ──────────────────────────────────
KEY_COLS = ['股票名称', '价格', '涨幅', '涨跌', '总金额', '换手率', '量比', '主力净流入', '总市值']
available_cols = [c for c in KEY_COLS if c in quote_df.columns]
table_df = quote_df[available_cols].copy()

# 格式化
if '总金额' in table_df:
    table_df['成交额(亿)'] = (table_df['总金额'] / 1e8).round(2)
if '总市值' in table_df:
    table_df['总市值(亿)'] = (table_df['总市值'] / 1e8).round(0)

print("\n=== 关键指标对比 ===")
print(table_df.to_string(index=False))

# ── 5. 第二步-A：归一化走势数据（供 show_widget 折线图） ─────
normalized = {}
for name, df in klines_data.items():
    df = df.copy()
    df['归一化'] = (df['收盘价'] / df['收盘价'].iloc[0] * 100).round(2)
    normalized[name] = df[['时间', '归一化']].rename(columns={'时间': 'date'})

# 合并为宽表（方便前端渲染）
wide_df = None
for name, df in normalized.items():
    df = df.rename(columns={'归一化': name})
    wide_df = df if wide_df is None else wide_df.merge(df, on='date', how='outer')

print("\n=== 归一化走势（最近5日） ===")
print(wide_df.tail(5).to_string(index=False))

# ── 5. 第二步-B：相关性分析（量化场景） ─────────────────────
returns = pd.DataFrame({
    name: df['收盘价'].pct_change()
    for name, df in klines_data.items()
})
corr_matrix = returns.corr().round(3)

print("\n=== 收益率相关性矩阵 ===")
print(corr_matrix.to_string())

# ── 输出给 show_widget 的数据结构 ──────────────────────────
viz_data = {
    "table": table_df.to_dict('records'),
    "trend_chart": {
        "dates": [str(d) for d in wide_df['date']],
        "series": {name: wide_df[name].tolist() for name in [s['name'] for s in stock_list]}
    },
    "correlation": corr_matrix.to_dict(),
}
# Claude 会基于 viz_data 调用 show_widget 渲染：
# 1. 关键指标表格（高亮涨跌）
# 2. 归一化走势折线图（多线，颜色区分，y轴=相对涨跌%）
# 3. 相关性热力图（可选，量化场景）

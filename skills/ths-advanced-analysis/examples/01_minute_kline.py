"""
案例1：分钟K线 + 可视化
场景：查看某只股票当日5分钟K线，叠加均线，标注成交量异动
"""

from thsdk import THS
import pandas as pd

# ── 1. 解析代码 ──────────────────────────────────────────────
with THS() as ths:
    r = ths.search_symbols("宁德时代")
    code = next(
        s['THSCODE'] for s in r.data
        if any(m in s.get('MarketDisplay', '') for m in ['沪A', '深A'])
    )  # → 'USZA300750'

# ── 2. 拉5分钟K线（一个交易日约78根） ───────────────────────
with THS() as ths:
    resp = ths.klines(code, interval="5m", count=78)

if not resp:
    raise RuntimeError(resp.error)

df = resp.df
# 字段：时间(datetime), 开盘价, 最高价, 最低价, 收盘价, 成交量

# ── 3. 计算指标 ──────────────────────────────────────────────
df['ma5']     = df['收盘价'].rolling(5).mean()
df['ma10']    = df['收盘价'].rolling(10).mean()
df['vol_avg'] = df['成交量'].rolling(20).mean()
df['vol_spike'] = df['成交量'] > df['vol_avg'] * 2   # 成交量异动标记

support    = df['最低价'].tail(20).min()
resistance = df['最高价'].tail(20).max()

# ── 4. 输出结果（传给 show_widget 渲染） ────────────────────
# Claude 会用以下数据渲染 K 线图 + 成交量柱状图：
result = {
    "title": f"{code} 5分钟K线",
    "kline": df[['时间','开盘价','最高价','最低价','收盘价']].to_dict('records'),
    "volume": df[['时间','成交量','vol_spike']].to_dict('records'),
    "ma": df[['时间','ma5','ma10']].to_dict('records'),
    "support": support,
    "resistance": resistance,
    "spike_times": df[df['vol_spike']]['时间'].astype(str).tolist(),
}
print(result)

# ── 其他周期示例 ─────────────────────────────────────────────
# 1分钟K线（适合超短线）
# resp = ths.klines(code, interval="1m", count=240)

# 30分钟K线（适合波段）
# resp = ths.klines(code, interval="30m", count=60)

# 按时间范围拉（count 与 start/end 二选一！）
# from datetime import datetime
# from zoneinfo import ZoneInfo
# tz = ZoneInfo('Asia/Shanghai')
# resp = ths.klines(code, interval="5m",
#                   start_time=datetime(2025, 3, 1, tzinfo=tz),
#                   end_time=datetime(2025, 3, 10, tzinfo=tz))

# 前复权日K（量化回测常用）
# resp = ths.klines(code, interval="day", count=250, adjust="forward")

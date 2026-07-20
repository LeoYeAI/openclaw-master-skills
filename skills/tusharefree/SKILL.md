---
name: tushare
description: Tushare Pro 金融大数据平台 - 提供A股、指数、基金、期货、债券、宏观数据，Token认证方式访问。
version: 1.2.0
homepage: https://tushare.pro
metadata: {"clawdbot":{"emoji":"📉","requires":{"bins":["python3"]}}}
---

# Tushare Pro（大数据开放社区）

[Tushare Pro](https://tushare.pro) is a widely used financial data platform in China, serving over 300,000 users. It provides a standardized Python API covering A-shares, indices, funds, futures, bonds, and macro data. All interfaces return `pandas.DataFrame`.

> ⚠️ **Token Required**: Register at https://tushare.pro and obtain your personal Token from the User Center. Some interfaces require a higher credit level. See the Credit System section below.

## 安装

```bash
pip install tushare --upgrade
```

## 初始化与基本用法

```python
import tushare as ts

# Set Token (only needs to be set once per session)
ts.set_token('your_token_here')

# Initialize the Pro API
pro = ts.pro_api()

# Call any data interface
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
print(df)
```

You can also pass the Token directly during initialization:

```python
# Initialize with Token directly
pro = ts.pro_api('your_token_here')
```

## 股票代码格式（ts_code）

- Shanghai: `600000.SH`, `601398.SH`
- Shenzhen: `000001.SZ`, `300750.SZ`
- Beijing: `430047.BJ`
- Indices: `000001.SH` (SSE Composite Index), `399001.SZ` (SZSE Component Index)

---

## 沪深股票数据

### 股票列表

```python
# Get basic information for all currently listed stocks
df = pro.stock_basic(
    exchange='',
    list_status='L',      # L=Listed, D=Delisted, P=Suspended
    fields='ts_code,symbol,name,area,industry,list_date'
)
```

Credit requirement: 120

### 日K线数据

```python
# Get daily market data for a specified stock
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240630'
)
# Returned fields: ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
```

Credit requirement: 120

### 周线/月线数据

```python
# Get weekly data
df = pro.weekly(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
# Get monthly data
df = pro.monthly(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

### 分钟级K线数据

```python
# Get minute-level K-line data
df = pro.stk_mins(
    ts_code='000001.SZ',
    freq='5min',           # Options: 1min, 5min, 15min, 30min, 60min
    start_date='2024-01-02 09:30:00',
    end_date='2024-01-02 15:00:00'
)
```

Credit requirement: 2000+

### 复权因子

```python
# Get adjustment factors for calculating forward/backward adjusted prices
df = pro.adj_factor(ts_code='000001.SZ', trade_date='20240102')
```

### 每日指标

```python
# Get daily market indicator data (PE ratio, PB ratio, turnover rate, market cap, etc.)
df = pro.daily_basic(
    ts_code='000001.SZ',
    trade_date='20240102',
    fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_mv,circ_mv'
)
```

Credit requirement: 120

### 停复牌信息

```python
# Get suspension & resumption info, S=Suspended
df = pro.suspend_d(ts_code='000001.SZ', suspend_type='S')
```

---

## 财务数据

### 利润表

```python
# Get listed company income statement data
df = pro.income(ts_code='000001.SZ', period='20231231')
```

### 资产负债表

```python
# Get listed company balance sheet data
df = pro.balancesheet(ts_code='000001.SZ', period='20231231')
```

### 现金流量表

```python
# Get listed company cash flow statement data
df = pro.cashflow(ts_code='000001.SZ', period='20231231')
```

### 财务指标

```python
# Get financial indicator data (ROE, EPS, revenue growth rate, net profit growth rate, etc.)
df = pro.fina_indicator(ts_code='000001.SZ', period='20231231')
```

### 业绩预告

```python
# Get listed company earnings forecast data
df = pro.forecast(ts_code='000001.SZ', period='20231231')
```

### 业绩快报

```python
# Get listed company earnings express report data
df = pro.express(ts_code='000001.SZ', period='20231231')
```

### 分红送股

```python
# Get listed company dividend and share distribution data
df = pro.dividend(ts_code='000001.SZ')
```

---

## 市场参考数据

### 个股资金流向

```python
# Get individual stock money flow data
df = pro.moneyflow(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

Credit requirement: 2000+

### 龙虎榜

```python
# 获取龙虎榜数据
df = pro.top_list(trade_date='20240102')
```

### 大宗交易

```python
# Get block trade data
df = pro.block_trade(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

### 融资融券

```python
# Get margin trading detail data
df = pro.margin_detail(trade_date='20240102')
```

### 股东增减持

```python
# Get shareholder increase/decrease in holdings data
df = pro.stk_holdertrade(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

---

## 指数数据

### 指数日K线

```python
# Get index daily market data
df = pro.index_daily(ts_code='000300.SH', start_date='20240101', end_date='20240630')
```

### 指数成分股

```python
# Get index constituents and weights
df = pro.index_weight(index_code='000300.SH', start_date='20240101', end_date='20240630')
```

### 指数基本信息

```python
# Get index basic information; market options: SSE (Shanghai Stock Exchange), SZSE (Shenzhen Stock Exchange), etc.
df = pro.index_basic(market='SSE')
```

---

## 基金数据

### 基金列表

```python
# Get fund list; E=Exchange-traded, O=OTC (over-the-counter)
df = pro.fund_basic(market='E')
```

### 基金日行情

```python
# Get exchange-traded fund daily market data
df = pro.fund_daily(ts_code='510300.SH', start_date='20240101', end_date='20240630')
```

### 基金净值

```python
# Get OTC fund net asset value data
df = pro.fund_nav(ts_code='000001.OF')
```

---

## 期货数据

### 期货日行情

```python
# Get futures daily market data
df = pro.fut_daily(ts_code='IF2401.CFX', start_date='20240101', end_date='20240131')
```

### 期货基本信息

```python
# Get futures contract basic information
# exchange options: CFFEX (China Financial Futures Exchange), SHFE (Shanghai Futures Exchange), DCE (Dalian Commodity Exchange), CZCE (Zhengzhou Commodity Exchange), INE (Shanghai International Energy Exchange)
df = pro.fut_basic(exchange='CFFEX', fut_type='1')
```

---

## 债券数据

### 可转债列表

```python
# Get convertible bond basic information
df = pro.cb_basic()
```

### 可转债日行情

```python
# Get convertible bond daily market data
df = pro.cb_daily(ts_code='113009.SH', start_date='20240101', end_date='20240630')
```

---

## 宏观经济数据

### Shibor利率

```python
# Get Shanghai Interbank Offered Rate
df = pro.shibor(start_date='20240101', end_date='20240630')
```

### GDP（国内生产总值）

```python
# Get China GDP data
df = pro.cn_gdp()
```

### CPI（居民消费价格指数）

```python
# Get China Consumer Price Index
df = pro.cn_cpi(start_m='202401', end_m='202406')
```

### PPI（生产者物价指数）

```python
# Get China Producer Price Index
df = pro.cn_ppi(start_m='202401', end_m='202406')
```

### 货币供应量

```python
# Get China money supply data (M0, M1, M2)
df = pro.cn_m(start_m='202401', end_m='202406')
```

---

## 交易日历

```python
# Get trading calendar
df = pro.trade_cal(
    exchange='SSE',        # Exchange: SSE (Shanghai), SZSE (Shenzhen), BSE (Beijing)
    start_date='20240101',
    end_date='20241231',
    fields='exchange,cal_date,is_open,pretrade_date'
)
```

---

## 完整示例：下载股票数据并保存为CSV

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get Kweichow Moutai daily K-line data
df = pro.daily(ts_code='600519.SH', start_date='20240101', end_date='20241231')

# Get adjustment factors and calculate forward-adjusted closing price
adj = pro.adj_factor(ts_code='600519.SH', start_date='20240101', end_date='20241231')
df = df.merge(adj[['trade_date', 'adj_factor']], on='trade_date')
df['adj_close'] = df['close'] * df['adj_factor']  # Calculate forward-adjusted price

# Save as CSV file
df.to_csv('moutai_2024.csv', index=False)
print(df.head())
```

## 积分系统

| 等级 | 积分 | 可用接口示例 |
|---|---|---|
| **基础** | 120 | `stock_basic`, `daily`, `weekly`, `monthly`, `trade_cal`, `daily_basic` |
| **中级** | 2000 | `stk_mins`（分钟数据）, `moneyflow`, `margin_detail`, `fina_indicator` |
| **高级** | 5000+ | Tick数据、大单数据、更高频率限制 |

### 如何免费获取积分

1. 注册并完善个人信息 → 获得120积分
2. 每日在tushare.pro签到
3. 社区贡献（分享、回答问题）
4. 邀请好友注册

## 使用技巧

- **需要Token** — 在 https://tushare.pro 免费注册获取（用户中心）。
- **日期格式**：`YYYYMMDD`（无连字符），所有日期参数使用此格式。
- **ts_code格式**：`{code}.{exchange}` — 如 `000001.SZ`、`600519.SH`。
- 所有接口返回 **pandas DataFrame**。
- 频率限制取决于积分等级 — 积分越高，每分钟调用次数越多。
- 使用 `fields` 参数仅选择需要的字段，提升查询性能。
- 本地缓存参考数据（股票列表、交易日历）以避免重复调用。
- Documentation: https://tushare.pro/document/2

---

## 进阶示例

### 批量下载多只股票

```python
import tushare as ts
import pandas as pd
import time

ts.set_token('your_token_here')
pro = ts.pro_api()

# 定义要下载的股票列表
stock_list = ['000001.SZ', '600519.SH', '300750.SZ', '601318.SH', '000858.SZ']

all_data = []
for ts_code in stock_list:
    # Get daily K-line data
    df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20240630')
    all_data.append(df)
    print(f"Downloaded {ts_code}, {len(df)} records")
    time.sleep(0.3)  # Throttle request frequency to avoid rate limiting

# Combine all data
combined = pd.concat(all_data, ignore_index=True)
combined.to_csv("multi_stock_tushare.csv", index=False)
print(f"合并总计: {len(combined)} 条记录")
```

### 计算前复权价格

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

ts_code = '600519.SH'

# Get daily K-line and adjustment factors
df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20241231')
adj = pro.adj_factor(ts_code=ts_code, start_date='20240101', end_date='20241231')

# Merge data
df = df.merge(adj[['trade_date', 'adj_factor']], on='trade_date')

# Calculate forward-adjusted prices (using the latest date's adjustment factor as the base)
latest_factor = df['adj_factor'].iloc[0]  # Latest adjustment factor
df['adj_open'] = df['open'] * df['adj_factor'] / latest_factor
df['adj_high'] = df['high'] * df['adj_factor'] / latest_factor
df['adj_low'] = df['low'] * df['adj_factor'] / latest_factor
df['adj_close'] = df['close'] * df['adj_factor'] / latest_factor

print(df[['trade_date', 'close', 'adj_factor', 'adj_close']].head(10))
```

### 获取全市场每日指标并筛选

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get market-wide daily indicators for a given date
df = pro.daily_basic(trade_date='20240628',
    fields='ts_code,trade_date,close,turnover_rate,pe_ttm,pb,ps_ttm,dv_ratio,total_mv,circ_mv')

# Filter criteria: PE between 5-20, PB between 0.5-3, dividend yield above 2%
filtered = df[
    (df['pe_ttm'] > 5) & (df['pe_ttm'] < 20) &
    (df['pb'] > 0.5) & (df['pb'] < 3) &
    (df['dv_ratio'] > 2)
].sort_values('pe_ttm')

print(f"Filtered {len(filtered)} stocks")
print(filtered[['ts_code', 'close', 'pe_ttm', 'pb', 'dv_ratio', 'total_mv']].head(20))
```

### 获取财务数据并分析

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

# 获取沪深300成分股
hs300 = pro.index_weight(index_code='000300.SH', start_date='20240601', end_date='20240630')
stock_codes = hs300['con_code'].unique().tolist()

# Get financial indicators (first 10 stocks as example)
fin_data = []
for code in stock_codes[:10]:
    df = pro.fina_indicator(ts_code=code, period='20231231',
        fields='ts_code,ann_date,roe,roa,grossprofit_margin,netprofit_yoy,or_yoy')
    if not df.empty:
        fin_data.append(df.iloc[0])

fin_df = pd.DataFrame(fin_data)
print("CSI 300 Selected Constituent Financial Indicators:")
print(fin_df[['ts_code', 'roe', 'roa', 'grossprofit_margin', 'netprofit_yoy']].to_string())
```

### 获取资金流向数据

```python
import tushare as ts

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get individual stock money flow (requires 2000+ credits)
df = pro.moneyflow(ts_code='000001.SZ', start_date='20240601', end_date='20240630')
# Fields include: buy_sm_vol (small order buy volume), sell_sm_vol (small order sell volume),
#                 buy_md_vol (medium order buy volume), buy_lg_vol (large order buy volume),
#                 buy_elg_vol (extra-large order buy volume), etc.
print(df.head())
```

### 完整示例：简单回测框架

```python
import tushare as ts
import pandas as pd
import numpy as np

ts.set_token('your_token_here')
pro = ts.pro_api()

# 获取平安银行日K线数据
df = pro.daily(ts_code='000001.SZ', start_date='20230101', end_date='20231231')
df = df.sort_values('trade_date').reset_index(drop=True)  # Sort by date ascending

# Get adjustment factors and calculate forward-adjusted closing price
adj = pro.adj_factor(ts_code='000001.SZ', start_date='20230101', end_date='20231231')
df = df.merge(adj[['trade_date', 'adj_factor']], on='trade_date')
latest_factor = df['adj_factor'].iloc[-1]
df['adj_close'] = df['close'] * df['adj_factor'] / latest_factor

# Calculate dual moving averages
df['MA5'] = df['adj_close'].rolling(5).mean()
df['MA20'] = df['adj_close'].rolling(20).mean()

# Simple backtest
initial_cash = 100000
cash = initial_cash
shares = 0
trades = []

for i in range(20, len(df)):
    # 金叉 — buy signal
    if df['MA5'].iloc[i] > df['MA20'].iloc[i] and df['MA5'].iloc[i-1] <= df['MA20'].iloc[i-1]:
        if cash > 0:
            price = df['adj_close'].iloc[i]
            shares = int(cash / price / 100) * 100
            cash -= shares * price
            trades.append(f"{df['trade_date'].iloc[i]} BUY {shares} shares @ {price:.2f}")
    # 死叉 — sell signal
    elif df['MA5'].iloc[i] < df['MA20'].iloc[i] and df['MA5'].iloc[i-1] >= df['MA20'].iloc[i-1]:
        if shares > 0:
            price = df['adj_close'].iloc[i]
            cash += shares * price
            trades.append(f"{df['trade_date'].iloc[i]} SELL {shares} shares @ {price:.2f}")
            shares = 0

final_value = cash + shares * df['adj_close'].iloc[-1]
print(f"初始资金: {initial_cash:.2f}")
print(f"最终组合价值: {final_value:.2f}")
print(f"Return: {(final_value/initial_cash - 1)*100:.2f}%")
for t in trades:
    print(f"  {t}")
```

---

---

## 🤖 AI Agent 高阶使用指南

对于 AI Agent，在使用该量化/数据工具时应遵循以下高阶策略和最佳实践，以确保任务的高效完成：

### 1. 数据校验与错误处理
在获取数据或执行操作后，AI 应当主动检查返回的结果格式是否符合预期，以及是否存在缺失值（NaN）或空数据。
* **示例策略**：在通过 API 获取数据框（DataFrame）后，使用 `if df.empty:` 进行校验；捕获 `Exception` 以防网络或接口错误导致进程崩溃。

### 2. 多步组合分析
AI 经常需要进行宏观经济分析或跨市场对比。应善于将当前接口与其他数据源或工具组合使用。
* **示例策略**：先获取板块或指数的宏观数据，再筛选成分股，最后对具体标的进行深入的财务或技术面分析，形成完整的决策链条。

### 3. 构建动态监控与日志
对于交易和策略类任务，AI 可以定期拉取数据并建立监控机制。
* **示例策略**：使用循环或定时任务检查特定标的的异动（如涨跌停、放量），并在发现满足条件的信号时输出结构化日志或触发预警。

---

## 社区与支持

由 **大佬量化** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** — 微信公众号 / Bilibili / 抖音

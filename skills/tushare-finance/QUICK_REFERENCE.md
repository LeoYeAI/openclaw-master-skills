# Tushare API 快速参考

本文档提供最常用的 Tushare API 接口和代码示例。

**作者**: [StanleyChanH](https://github.com/StanleyChanH)

## 股票数据

### 获取股票列表
```python
import tushare as ts
pro = ts.pro_api()

# 获取所有正常上市的股票
df = pro.stock_basic(list_status='L')

# 筛选特定交易所
df_sz = pro.stock_basic(exchange='SZSE')  # 深交所
df_sh = pro.stock_basic(exchange='SSE')   # 上交所
```

### 获取日线行情
```python
# 单只股票
df = pro.daily(ts_code='000001.SZ', start_date='20241201', end_date='20241231')

# 多只股票
df = pro.daily(ts_code='000001.SZ,600000.SH', start_date='20241201', end_date='20241231')

# 某日所有股票
df = pro.daily(trade_date='20241231')
```

### 获取财务数据
```python
# 利润表
df = pro.income(ts_code='600000.SH', start_date='20240101', end_date='20241231')

# 资产负债表
df = pro.balancesheet(ts_code='600000.SH', start_date='20240101', end_date='20241231')

# 现金流量表
df = pro.cashflow(ts_code='600000.SH', start_date='20240101', end_date='20241231')

# 财务指标
df = pro.fina_indicator(ts_code='600000.SH', start_date='20240101', end_date='20241231')
```

## 指数数据

### 获取指数列表
```python
df = pro.index_basic(market='SSE')  # 上交所指数
df = pro.index_basic(market='SZSE') # 深交所指数
```

### 获取指数行情
```python
# 上证指数
df = pro.index_daily(ts_code='000001.SH', start_date='20241201', end_date='20241231')

# 深证成指
df = pro.index_daily(ts_code='399001.SZ', start_date='20241201', end_date='20241231')
```

## 基金数据

### 获取基金列表
```python
df = pro.fund_basic(market='E')  # 场内基金
df = pro.fund_basic(market='O')  # 场外基金
```

### 获取基金净值
```python
df = pro.fund_nav(ts_code='000001.OF', start_date='20241201', end_date='20241231')
```

## 宏观经济

### GDP 数据
```python
df = pro.gdp(start_q='2020011', end_q='2024044')
```

### CPI 数据
```python
df = pro.cpi(start_date='20240101', end_date='20241231')
```

### PMI 数据
```python
df = pro.pmi(start_date='20240101', end_date='20241231')
```

### 利率数据
```python
# Shibor
df = pro.shibor(start_date='20241201', end_date='20241231')

# LPR
df = pro.lpr(start_date='20241201', end_date='20241231')
```

## 港股美股

### 港股数据
```python
# 港股列表
df = pro.hk_basic()

# 港股行情
df = pro.hk_daily(ts_code='00700.HK', start_date='20241201', end_date='20241231')
```

### 美股数据
```python
# 美股列表
df = pro.us_basic()

# 美股行情
df = pro.us_daily(ts_code='AAPL', start_date='20241201', end_date='20241231')
```

## 常见查询模式

### 按日期范围查询
```python
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',  # YYYYMMDD
    end_date='20241231'
)
```

### 按交易日查询
```python
df = pro.daily(trade_date='20241231')
```

### 获取最新数据
```python
# 先获取最近的交易日
import datetime
today = datetime.datetime.now().strftime('%Y%m%d')
df = pro.daily(trade_date=today)
```

## 数据处理技巧

### 数据清洗
```python
# 去除停牌数据
df = df[df['vol'] > 0]

# 排序
df = df.sort_values('trade_date')

# 重置索引
df = df.reset_index(drop=True)
```

### 数据保存
```python
# 保存到 CSV
df.to_csv('data.csv', index=False)

# 保存到 Excel
df.to_excel('data.xlsx', index=False)
```

## 错误处理

```python
import tushare as ts

try:
    pro = ts.pro_api('your_token')
    df = pro.daily(ts_code='000001.SZ', start_date='20241201', end_date='20241231')
    print(df.head())
except ts.errors.TushareException as e:
    print(f"Tushare API 错误: {e}")
except Exception as e:
    print(f"错误: {e}")
```

## 性能优化

### 批量获取
```python
# 一次获取多只股票
stock_codes = ['000001.SZ', '600000.SH', '000002.SZ']
df = pro.daily(ts_code=','.join(stock_codes), start_date='20241201', end_date='20241231')
```

### 控制请求频率
```python
import time

for stock in stock_codes:
    df = pro.daily(ts_code=stock, start_date='20241201', end_date='20241231')
    time.sleep(0.3)  # 避免超限
```

## 常用字段说明

### 日线行情字段
- `trade_date`: 交易日期
- `ts_code`: 股票代码
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `vol`: 成交量（手）
- `amount`: 成交额（千元）

### 财务指标字段
- `end_date`: 报告期
- `roe`: 净资产收益率
- `net_profit_margin`: 销售净利率
- `gross_margin`: 销售毛利率
- `debt_to_assets`: 资产负债率

## 更多接口

完整接口列表和详细说明请查看：
- [接口文档索引](docs/README.md)
- [Tushare 官方文档](https://tushare.pro/document/2)

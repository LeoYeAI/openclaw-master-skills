# Tushare Pro API 快速参考

本文档提供最常用的 Tushare Pro API 接口和代码示例。

**维护者**: 大佬量化 (Boss Quant)

## 初始化

```python
import tushare as ts

ts.set_token('YOUR_TUSHARE_TOKEN')
pro = ts.pro_api()
```

## 日线行情

```python
# 获取日线行情
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20241231')
# 返回字段：ts_code, trade_date, open, high, low, close, vol, amount
```

## 股票列表

```python
# 获取股票基本信息
df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
# list_status: L-上市, D-退市, P-暂停上市
```

## 每日指标

```python
# 每日指标（市盈率、换手率等）
df = pro.daily_basic(ts_code='000001.SZ', trade_date='20241231')
# 返回字段：pe, pe_ttm, pb, turnover_rate, total_mv, circ_mv
```

## 财务数据

```python
# 利润表
df = pro.income(ts_code='000001.SZ', period='20240331', fields='ts_code,ann_date,end_date,revenue,operate_profit,n_income')

# 资产负债表
df = pro.balancesheet(ts_code='000001.SZ', period='20240331', fields='ts_code,ann_date,end_date,total_assets,total_liab')
```

## 指数行情

```python
# 指数日线行情
df = pro.index_daily(ts_code='000300.SH', start_date='20240101', end_date='20241231')
# 支持：000001.SH(上证指数), 000300.SH(沪深300), 399001.SZ(深证成指)
```

## 基金行情

```python
# 基金日线行情
df = pro.fund_daily(ts_code='510300.SH', start_date='20240101', end_date='20241231')
```

## 常用参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| ts_code | 股票代码 | `000001.SZ` |
| trade_date | 交易日期 | `20241231` |
| start_date | 开始日期 | `20240101` |
| end_date | 结束日期 | `20241231` |
| period | 报告期 | `20240331` |
| fields | 返回字段 | `ts_code,name` |

## 更多接口

完整接口列表请查看：
- [Tushare Pro 官方文档](https://tushare.pro/document/2)
- [接口列表](https://tushare.pro/document/1)

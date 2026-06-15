# XtQuant QMT SDK 快速参考

本文档提供最常用的 XtQuant 行情和交易接口代码示例。

**维护者**: 大佬量化 (Boss Quant)

## 连接行情

```python
from xtquant import xtdata

# 连接行情服务（需miniQMT运行）
xtdata.connect()
```

## K线数据

```python
# 获取日K线
data = xtdata.get_market_data_ex([], ['000001.SZ'], period='1d', start_time='20240101')
df = data['000001.SZ']
# 返回字段：open, high, low, close, volume, amount

# 下载历史数据
xtdata.download_history_data('000001.SZ', '1d', start_time='20240101')

# 订阅实时行情
xtdata.subscribe_quote('000001.SZ', period='tick', callback=on_data)
```

## 创建交易实例

```python
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount

# 创建交易实例
xt_trader = XtQuantTrader(r'D:\国金QMT\userdata_mini', 123456)
xt_trader.start()
xt_trader.connect()

# 创建账户对象
acc = StockAccount('your_account_id')
```

## 下单交易

```python
# 买入（xtconstant: 1-买入, 2-卖出）
order_id = xt_trader.order_stock(acc, '000001.SZ', 1, 100, 0, 10.5)
# 参数：账户, 代码, 方向, 数量, 价格类型, 价格

# 卖出
order_id = xt_trader.order_stock(acc, '000001.SZ', 2, 100, 0, 11.0)

# 撤单
xt_trader.cancel_order_stock(acc, order_id)
```

## 持仓查询

```python
# 查询持仓
positions = xt_trader.query_stock_positions(acc)
for pos in positions:
    print(f"{pos.stock_code}: {pos.volume}股, 成本:{pos.avg_price}")

# 查询单只股票持仓
pos = xt_trader.query_stock_positions(acc, stock_code='000001.SZ')
```

## 资产查询

```python
# 查询账户资产
asset = xt_trader.query_stock_asset(acc)
print(f"总资产: {asset.total_asset}")
print(f"可用资金: {asset.cash}")
print(f"持仓市值: {asset.market_value}")
```

## 账户类型

```python
from xtquant.xttype import StockAccount

# 普通股票账户
acc = StockAccount('your_account_id')

# 信用账户（融资融券）
acc = StockAccount('your_account_id', 'CREDIT')
```

## 委托查询

```python
# 查询当日委托
orders = xt_trader.query_stock_orders(acc)
for o in orders:
    print(f"{o.stock_code}: 状态={o.order_status}, 数量={o.order_volume}")
```

## 更多接口

完整接口列表请查看：
- [XtQuant 官方文档](http://dict.thinktrader.net/nativeApi/start_now.html)

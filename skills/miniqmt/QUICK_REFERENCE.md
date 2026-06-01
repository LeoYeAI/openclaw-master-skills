# miniQMT 快速参考

本文档提供最常用的 miniQMT (xtquant) 接口和代码示例。

**维护者**: 大佬量化 (Boss Quant)

## 行情连接

```python
from xtquant import xtdata

# 连接行情服务（需先启动 miniQMT 客户端）
xtdata.connect()
```

## 下载历史数据

```python
# 下载日K线
xtdata.download_history_data("000001.SZ", "1d", start_time="20240101")

# 下载分钟K线
xtdata.download_history_data("000001.SZ", "1m", start_time="20240101")

# 批量下载
stock_list = ["000001.SZ", "600000.SH", "000002.SZ"]
for stock in stock_list:
    xtdata.download_history_data(stock, "1d", start_time="20240101")
```

## 获取K线数据

```python
# 获取日K线
data = xtdata.get_market_data_ex([], ["000001.SZ"], period="1d", start_time="20240101", end_time="20241231")
df = data["000001.SZ"]
print(df.head())

# 获取多只股票
data = xtdata.get_market_data_ex([], ["000001.SZ", "600000.SH"], period="1d", start_time="20240101", end_time="20241231")

# 支持的周期: 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mon
```

## 订阅实时行情

```python
def on_data(datas):
    for stock, data in datas.items():
        print(f"{stock}: 最新价={data['lastPrice']}, 成交量={data['volume']}")

# 订阅实时行情
xtdata.subscribe_quote("000001.SZ", period="tick", callback=on_data)

# 订阅多只股票
for stock in ["000001.SZ", "600000.SH"]:
    xtdata.subscribe_quote(stock, period="tick", callback=on_data)

# 保持运行
xtdata.run()
```

## 下单交易

```python
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount
from xtquant import xtconstant

trader = XtQuantTrader("path_to_userdata", session_id=123456)
account = StockAccount("your_account_id")
trader.start()

# 买入（限价）
trader.order_stock(account, "000001.SZ", xtconstant.STOCK_BUY, 100, xtconstant.FIX_PRICE, 10.5)

# 查询持仓
positions = trader.query_stock_positions(account)
for pos in positions:
    print(f"{pos.stock_code}: 数量={pos.volume}, 可用={pos.can_use_volume}")
```

## 更多资源

- [xtquant 官方文档](http://dict.thinktrader.net/nativeApi/start_now.html)
- [miniQMT 使用指南](http://dict.thinktrader.net/nativeApi/xtdata.html)

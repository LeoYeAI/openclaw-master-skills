# Quote Service 文档

所属项目：**Futu Trade Bot Skills**

## 模块位置
`src/quote_service.py`

## 概述
行情模块负责：
- 基础行情拉取
- K 线与逐笔拉取
- 行情订阅与回调
- 统一启动实时报价/摆盘监听

## 拉取型函数
- `get_stock_basicinfo(...)`
- `get_market_state(...)`
- `get_market_snapshot(...)`
- `get_cur_kline(...)`
- `request_history_kline(...)`
- `get_rt_ticker(...)`

说明：
- 拉取型函数返回后会显式关闭 quote context。
- `get_cur_kline(...)` 和 `get_rt_ticker(...)` 在遇到“请先订阅”时会自动补订阅后重试。

## 订阅/回调型函数
- `set_quote_callback(callback)`
- `set_orderbook_callback(callback)`
- `subscribe(...)`
- `unsubscribe(...)`
- `unsubscribe_all()`
- `query_subscription()`

说明：
- 这些函数不会自动关闭 quote context。
- 用于长连接 / 回调推送场景。
- 调用方结束时应显式 `close_quote_service()`。

## 统一启动函数

### `start_quote_stream(...)`
完成两步：
1. 注册 `QUOTE` 回调
2. 发起 `QUOTE` 订阅

### `start_orderbook_stream(...)`
完成两步：
1. 注册 `ORDER_BOOK` 回调
2. 发起 `ORDER_BOOK` 订阅

这两个函数适合策略脚本，避免把“设置回调 + 订阅”拆开写。

## 使用示例
```python
from quote_service import start_quote_stream, unsubscribe_all, close_quote_service

def on_quote(payload):
    print(payload)

start_quote_stream(["HK.00700"], on_quote)

# done
unsubscribe_all()
close_quote_service()
```

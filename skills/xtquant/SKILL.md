---
name: xtquant
description: XtQuant QMT Python SDK - 集成行情数据(xtdata)和交易接口(xttrade)，支持A股、期货、期权等中国证券市场。
version: 1.2.0
homepage: http://dict.thinktrader.net/nativeApi/start_now.html
metadata: {"clawdbot":{"emoji":"⚡","requires":{"bins":["python3"]}}}
---

# XtQuant（迅投QMT Python SDK）

XtQuant is the Python SDK for the [QMT/miniQMT](http://www.thinktrader.net) quantitative trading platform, developed by ThinkTrader (XunTou Technology). It contains two core modules:

- **xtdata** — Market Data Module: real-time quotes, historical K-lines, tick data, Level 2 data, financial data, sector management
- **xttrade** — Trading Module: order placement, position/order queries, account management, margin trading, futures/options, smart algorithms

> ⚠️ **Requires miniQMT or QMT client running on Windows**. XtQuant connects to the QMT process via local TCP. You need QMT/miniQMT access enabled by your broker.

## 安装

```bash
pip install xtquant
```

You can also download from the official website: http://dict.thinktrader.net/nativeApi/download_xtquant.html

## 架构概述

```
Your Python script (any IDE, any Python version)
    ↓ (xtquant SDK, pip install)
    ├── xtdata  → miniQMT (market data service, TCP connection)
    └── xttrade → miniQMT (trading service, TCP connection)
         ↓
    Broker trading system
```

## 核心模块参考

| Module | Import | Purpose |
|---|---|---|
| `xtdata` | `from xtquant import xtdata` | Market data: K-lines, tick, Level 2, financials, sectors |
| `xttrader` | `from xtquant.xttrader import XtQuantTrader` | Trading: order placement, queries, callbacks |
| `xtconstant` | `from xtquant import xtconstant` | Constants: order types, price types, market codes |
| `xttype` | `from xtquant.xttype import StockAccount` | Account types: STOCK, CREDIT, FUTURE |

---

## 快速入门 — 行情数据


```python
from xtquant import xtdata

# Connect to local miniQMT (default: localhost)
xtdata.connect()

# Download historical K-line data (must download to local cache before first access)
xtdata.download_history_data('000001.SZ', '1d', start_time='20240101', end_time='20240630')

# Get local K-line data (returns a dict of DataFrames keyed by stock code)
data = xtdata.get_market_data_ex(
    [],                    # field_list, empty list means all fields
    ['000001.SZ'],         # stock_list, list of stock codes
    period='1d',
    start_time='20240101',
    end_time='20240630',
    dividend_type='front'  # 复权类型: none (unadjusted), front (forward-adjusted), back (backward-adjusted), front_ratio (proportional forward), back_ratio (proportional backward)
)
print(data['000001.SZ'])
```

### 实时行情订阅

```python
def on_data(datas):
    """Quote data callback function, receives pushed real-time data"""
    for stock_code, data in datas.items():
        print(stock_code, data)

# Subscribe to tick data for a single stock
xtdata.subscribe_quote('000001.SZ', period='tick', callback=on_data)

# Subscribe to full-market quote push
xtdata.subscribe_whole_quote(['SH', 'SZ'], callback=on_data)

xtdata.run()  # Block the current thread, continuously receiving callback data
```

### 财务数据

```python
# First download financial data to local cache
xtdata.download_financial_data(['000001.SZ'])
# Then retrieve financial data from local cache
data = xtdata.get_financial_data(['000001.SZ'])
# Available financial reports: Balance (balance sheet), Income (income statement), CashFlow (cash flow statement),
# PershareIndex (per-share indicators), CapitalStructure (capital structure), TOP10HOLDER (top 10 shareholders),
# TOP10FLOWHOLDER (top 10 tradable shareholders), SHAREHOLDER (shareholder count)
```

### 合约信息与板块

```python
# Get detailed instrument info (name, price limits, tick size, etc.)
info = xtdata.get_instrument_detail('000001.SZ')
# Get security type (stock/index/fund/bond, etc.)
itype = xtdata.get_instrument_type('000001.SZ')
# Get list of stocks in a sector
stocks = xtdata.get_stock_list_in_sector('沪深A股')
# Get list of trading dates
days = xtdata.get_trading_dates('SH', start_time='20240101', end_time='20240630')
```

---

## 快速入门 — 交易

```python
from xtquant import xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

# Create a trader instance (path points to miniQMT's userdata_mini directory)
path = r'D:\国金证券QMT交易端\userdata_mini'
session_id = 123456  # Each strategy must use a unique session_id
xt_trader = XtQuantTrader(path, session_id)

# Register a callback class to receive real-time push notifications
class MyCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print('Disconnected')
    def on_stock_order(self, order):
        print(f'Order update: {order.stock_code} status={order.order_status}')
    def on_stock_trade(self, trade):
        print(f'Trade update: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, order_error):
        print(f'Order error: {order_error.error_msg}')
    def on_order_stock_async_response(self, response):
        print(f'Async order response: order_id={response.order_id}')

xt_trader.register_callback(MyCallback())
xt_trader.start()
connect_result = xt_trader.connect()  # 收益率 0 on successful connection

# Create an account object and subscribe to push notifications
account = StockAccount('your_account_id')
xt_trader.subscribe(account)  # Enable push notifications for this account

# Place order: limit buy 600000.SH, 1000 shares at price 10.5
order_id = xt_trader.order_stock(
    account, '600000.SH', xtconstant.STOCK_BUY, 1000,
    xtconstant.FIX_PRICE, 10.5, 'strategy1', 'test_order'
)
# 收益率 order_id > 0 on success, -1 on failure

# 查询持仓
positions = xt_trader.query_stock_positions(account)
for pos in positions:
    print(pos.stock_code, pos.volume, pos.can_use_volume, pos.market_value)

# Query orders
orders = xt_trader.query_stock_orders(account)

# Query assets
asset = xt_trader.query_stock_asset(account)
print(f'Available cash: {asset.cash}, Total assets: {asset.total_asset}')

# 撤单
xt_trader.cancel_order_stock(account, order_id)

# Block the main thread, waiting for callbacks
xt_trader.run_forever()
```

---

## 股票代码格式

| Market | Format | Example |
|---|---|---|
| Shanghai A-shares | `XXXXXX.SH` | `600000.SH` |
| Shenzhen A-shares | `XXXXXX.SZ` | `000001.SZ` |
| Beijing Stock Exchange | `XXXXXX.BJ` | `430047.BJ` |
| Shanghai Index | `XXXXXX.SH` | `000001.SH` (SSE Composite Index) |
| Shenzhen Index | `XXXXXX.SZ` | `399001.SZ` (SZSE Component Index) |
| CFFEX Futures | `XXXX.IF` | `IF2401.IF` (CSI 300 Futures) |
| SHFE Futures | `XXXX.SF` | `ag2407.SF` (Silver Futures) |
| DCE Futures | `XXXX.DF` | `m2405.DF` (Soybean Meal Futures) |
| ZCE Futures | `XXXX.ZF` | `CF405.ZF` (Cotton Futures) |
| INE Futures | `XXXX.INE` | `sc2407.INE` (Crude Oil Futures) |
| Shanghai Options | `XXXXXXXX.SHO` | `10004358.SHO` |
| Shenzhen Options | `XXXXXXXX.SZO` | `90000001.SZO` |
| ETF | `XXXXXX.SH/SZ` | `510300.SH` |
| Convertible Bonds | `XXXXXX.SH/SZ` | `113050.SH` |


## 数据周期

`tick`, `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1mon`

## 支持的资产类型

| Asset | Market Data (xtdata) | Trading (xttrade) |
|---|---|---|
| A-shares (Shanghai & Shenzhen) | ✅ K-lines, tick, Level 2, financials | ✅ Buy/Sell |
| ETF | ✅ K-lines, tick, IOPV | ✅ Buy/Sell, Subscribe/Redeem |
| Convertible Bonds | ✅ K-lines, tick | ✅ Buy/Sell |
| Futures | ✅ K-lines, tick | ✅ Open long/Close long/Open short/Close short |
| Options | ✅ K-lines, tick | ✅ Buy/Sell open/close, Exercise |
| Indices | ✅ K-lines, tick | ❌ |
| Funds | ✅ K-lines, tick | ✅ Buy/Sell |
| Margin Trading | ✅ Via credit account | ✅ Full credit trading |

## 订单类型常量（xtconstant）

| Category | Constants |
|---|---|
| **Stock** | `STOCK_BUY` (23, buy), `STOCK_SELL` (24, sell) |
| **Credit** | `CREDIT_FIN_BUY` (margin buy), `CREDIT_SLO_SELL` (short sell), `CREDIT_BUY_SECU_REPAY` (buy to repay securities), `CREDIT_DIRECT_CASH_REPAY` (direct cash repayment), etc. |
| **Futures** | `FUTURE_BUY_OPEN` (open long), `FUTURE_SELL_CLOSE` (close long), `FUTURE_SELL_OPEN` (open short), `FUTURE_BUY_CLOSE` (close short) |
| **Options** | `STOCK_OPTION_BUY_OPEN` (buy to open), `STOCK_OPTION_SELL_CLOSE` (sell to close), `STOCK_OPTION_EXERCISE` (exercise), etc. |
| **Price Type** | `FIX_PRICE` (11, limit), `ANY_PRICE` (12, market), `LATEST_PRICE` (5, latest price), `MARKET_PEER_PRICE_FIRST` (best counterparty price), etc. |

## 账户类型

```python
StockAccount('id')            # Regular stock account
StockAccount('id', 'CREDIT')  # Credit account (margin trading)
StockAccount('id', 'FUTURE')  # Futures account
```

## xtdata接口模式

The market data module follows a unified **download → retrieve** pattern:

1. **Subscribe** (subscribe): `subscribe_quote`, `subscribe_whole_quote` — real-time push
2. **Download** (download): `download_history_data`, `download_financial_data` — download from server to local cache (synchronous/blocking)
3. **Retrieve** (get): `get_market_data_ex`, `get_financial_data` — read from local cache (fast)

## xttrade回调系统

Register an `XtQuantTraderCallback` subclass to receive real-time push notifications:

| Callback | Data Type | Trigger Event |
|---|---|---|
| `on_stock_order(order)` | XtOrder | Order status change |
| `on_stock_trade(trade)` | XtTrade | Trade execution |
| `on_stock_position(position)` | XtPosition | Position change |
| `on_stock_asset(asset)` | XtAsset | Asset change |
| `on_order_error(error)` | XtOrderError | Order placement failure |
| `on_cancel_error(error)` | XtCancelError | Order cancellation failure |
| `on_disconnected()` | — | Connection lost |
| `on_order_stock_async_response(resp)` | XtOrderResponse | Async order response |

## 高级功能

- **Smart Algorithm Trading**: Execute algorithmic orders such as VWAP via `smart_algo_order_async`
- **Securities Lending**: Query available securities, apply for lending, manage contracts
- **Bank-Securities Transfer**: Transfer funds between bank and securities accounts
- **CTP Internal Transfer**: Transfer funds between futures and options accounts
- **Custom Sectors**: Create, manage, and query custom stock groups
- **Level 2 Data**: l2quote, l2order, l2transaction, l2quoteaux, l2orderqueue, l2thousand (1000-level order book), limitupperformance (consecutive limit-up tracking), snapshotindex, hfiopv, fullspeedorderbook

## 使用技巧

- **miniQMT must be running on Windows** — xtquant connects via local TCP.
- `session_id` must be unique per strategy — different strategies need different IDs.
- `connect()` is a one-time connection — it does not auto-reconnect after disconnection; you must call it again manually.
- Always call `subscribe(account)` to receive trading push callbacks.
- Data is cached locally after download — subsequent reads are extremely fast.
- Use `dividend_type='front'` to get forward-adjusted K-line data.
- In push callbacks, use async query methods to avoid deadlocks.
- Documentation: http://dict.thinktrader.net/nativeApi/start_now.html

---

## 进阶示例

### 批量下载全市场日K线数据

```python
from xtquant import xtdata

xtdata.connect()

# Get the full list of Shanghai & Shenzhen A-shares
stock_list = xtdata.get_stock_list_in_sector('沪深A股')
print(f"Total {len(stock_list)} A-shares")

# Batch download daily K-line data (recommended to download in batches to avoid timeout)
batch_size = 50
for i in range(0, len(stock_list), batch_size):
    batch = stock_list[i:i+batch_size]
    for stock in batch:
        try:
            xtdata.download_history_data(stock, '1d', start_time='20240101', end_time='20240630')
        except Exception as e:
            print(f"Failed to download {stock}: {e}")
    print(f"Downloaded {min(i+batch_size, len(stock_list))}/{len(stock_list)}")

# Batch retrieve data
data = xtdata.get_market_data_ex(
    [], stock_list[:10], period='1d',
    start_time='20240101', end_time='20240630',
    dividend_type='front'
)
for code, df in data.items():
    print(f"{code}: {len(df)} records, latest close={df['close'].iloc[-1]}")
```


### 实时行情监控 + 条件触发下单

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import threading

# === Trading Callbacks ===
class MyCallback(XtQuantTraderCallback):
    def on_stock_order(self, order):
        print(f'Order: {order.stock_code} status={order.order_status} {order.status_msg}')
    def on_stock_trade(self, trade):
        print(f'Trade: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, error):
        print(f'Error: {error.error_msg}')

# === Initialize Trading ===
path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 888888)
xt_trader.register_callback(MyCallback())
xt_trader.start()
xt_trader.connect()
account = StockAccount('your_account')
xt_trader.subscribe(account)

# === Quote Monitoring Parameters ===
target_stock = '000001.SZ'
buy_price = 10.50    # Target buy price
sell_price = 11.50   # Target sell price
bought = False

def on_tick(datas):
    """Real-time tick callback: automatically places orders when price hits target"""
    global bought
    for code, tick in datas.items():
        price = tick['lastPrice']
        print(f'{code}: latest price={price}')

        # Price drops to or below target buy price, buy
        if price <= buy_price and not bought:
            order_id = xt_trader.order_stock(
                account, code, xtconstant.STOCK_BUY, 100,
                xtconstant.FIX_PRICE, buy_price, 'auto_buy', '条件触发买入'
            )
            print(f'Buy triggered: order_id={order_id}')
            bought = True

        # Price rises to or above target sell price, sell
        elif price >= sell_price and bought:
            order_id = xt_trader.order_stock(
                account, code, xtconstant.STOCK_SELL, 100,
                xtconstant.FIX_PRICE, sell_price, 'auto_sell', '条件触发卖出'
            )
            print(f'Sell triggered: order_id={order_id}')
            bought = False

# === Start quote subscription (separate thread) ===
xtdata.connect()
def run_data():
    xtdata.subscribe_quote(target_stock, period='tick', callback=on_tick)
    xtdata.run()

t = threading.Thread(target=run_data, daemon=True)
t.start()

# Keep the main thread running
xt_trader.run_forever()
```

### 多股票均线策略

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import pandas as pd

xtdata.connect()

# Define stock pool
stock_pool = ['000001.SZ', '600036.SH', '601318.SH', '000858.SZ', '300750.SZ']

# Download historical data
for stock in stock_pool:
    xtdata.download_history_data(stock, '1d', start_time='20240101', end_time='20241231')

# Retrieve data and compute signals
signals = {}
for stock in stock_pool:
    data = xtdata.get_market_data_ex([], [stock], period='1d',
        start_time='20240101', end_time='20241231', dividend_type='front')
    df = data[stock]

    # Calculate 5-day and 20-day moving averages
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma20'] = df['close'].rolling(20).mean()

    # Determine the latest signal
    if len(df) >= 21:
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        if prev['ma5'] <= prev['ma20'] and latest['ma5'] > latest['ma20']:
            signals[stock] = 'BUY'   # 金叉
        elif prev['ma5'] >= prev['ma20'] and latest['ma5'] < latest['ma20']:
            signals[stock] = 'SELL'  # 死叉
        else:
            signals[stock] = 'HOLD'  # Hold

print("Trading signals:")
for stock, signal in signals.items():
    print(f"  {stock}: {signal}")
```

### 获取财务数据并筛选股票

```python
from xtquant import xtdata

xtdata.connect()

# Get the list of Shanghai & Shenzhen A-shares
stock_list = xtdata.get_stock_list_in_sector('沪深A股')

# Download financial data
xtdata.download_financial_data(stock_list[:100])  # Download the first 100

# Retrieve financial data
for stock in stock_list[:10]:
    data = xtdata.get_financial_data([stock])
    if stock in data and 'PershareIndex' in data[stock]:
        psi = data[stock]['PershareIndex']
        if len(psi) > 0:
            latest = psi[-1]
            roe = latest.get('du_return_on_equity', 0)
            eps = latest.get('s_fa_eps_basic', 0)
            print(f"{stock}: ROE={roe}, EPS={eps}")
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

---
name: miniqmt
description: miniQMT 极简量化交易终端 - 支持外接Python获取行情数据和程序化交易，基于xtquant SDK。
version: 1.2.0
homepage: http://dict.thinktrader.net/nativeApi/start_now.html
metadata: {"clawdbot":{"emoji":"🚀","requires":{"bins":["python3"]}}}
---

# miniQMT（迅投极简量化交易终端）

miniQMT 是迅投科技开发的轻量级量化交易终端，专为外接Python设计。它作为本地Windows服务运行，通过 [XtQuant](http://dict.thinktrader.net/nativeApi/start_now.html) Python SDK（`xtdata` + `xttrade`）提供行情数据和交易功能。

> ⚠️ **需要券商开通miniQMT权限**。联系您的证券公司开通。多家国内券商支持（国金、华鑫、中泰、东方财富、国信、方正等）。

## miniQMT 概述

- **轻量级QMT客户端**，在Windows上作为后台服务运行
- 为外部Python程序提供**行情数据服务** + **交易服务**
- Python脚本通过 `xtquant` SDK经本地TCP连接（xtdata获取行情，xttrade执行交易）
- 支持品种：A股、ETF、可转债、期货、期权、融资融券
- 部分券商提供免费的 **Level 2数据**

## 架构

```
Python脚本（任意IDE: VS Code, PyCharm, Jupyter等）
    ↓ xtquant SDK（pip install xtquant）
    ├── xtdata  ──TCP──→ miniQMT（行情数据服务）
    └── xttrade ──TCP──→ miniQMT（交易服务）
                              ↓
                    券商交易系统
```

## 如何获取 miniQMT

1. 在支持QMT的券商开立证券账户
2. 申请miniQMT权限（部分券商要求最低资产，如5万-10万元）
3. 从券商处下载安装QMT客户端
4. 以miniQMT模式（极简模式）启动并登录

## 使用流程

### 1. 启动 miniQMT

以极简模式启动QMT客户端并登录。miniQMT界面非常简洁——只有一个登录窗口。

### 2. 安装 xtquant

```bash
pip install xtquant
```

### 3. 使用Python连接行情数据

```python
from xtquant import xtdata

# 连接本地miniQMT行情数据服务
xtdata.connect()

# 下载历史数据（首次访问前必须下载）
xtdata.download_history_data('000001.SZ', '1d', start_time='20240101', end_time='20240630')

# 获取K线数据（返回以股票代码为键的DataFrame字典）
data = xtdata.get_market_data_ex(
    [], ['000001.SZ'], period='1d',
    start_time='20240101', end_time='20240630',
    dividend_type='front'  # 前复权
)
print(data['000001.SZ'].tail())
```

### 4. 使用Python连接交易服务

```python
from xtquant import xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

# path必须指向QMT安装目录下的userdata_mini文件夹
path = r'D:\券商QMT\userdata_mini'
# session_id对每个策略/脚本必须唯一
session_id = 123456
xt_trader = XtQuantTrader(path, session_id)

# 注册回调接收实时推送通知
class MyCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print('已断开连接 — 需要重新连接')
    def on_stock_order(self, order):
        print(f'Order update: {order.stock_code} status={order.order_status} msg={order.status_msg}')
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, order_error):
        print(f'Order error: {order_error.error_msg}')

xt_trader.register_callback(MyCallback())
xt_trader.start()
connect_result = xt_trader.connect()  # 收益率 0 on success, non-zero on failure

account = StockAccount('your_account')
xt_trader.subscribe(account)  # 订阅账户推送通知

# 下买入单
order_id = xt_trader.order_stock(
    account, '000001.SZ', xtconstant.STOCK_BUY, 100,
    xtconstant.FIX_PRICE, 11.50, 'my_strategy', 'test_order'
)
# order_id > 0 表示成功，-1 表示失败
```

---

## miniQMT 与完整版 QMT 对比

| 特性 | miniQMT | QMT（完整版） |
|---|---|---|
| **Python** | 外接Python（任意版本） | 内置Python（版本受限） |
| **IDE** | 任意（VS Code, PyCharm, Jupyter等） | 仅内置编辑器 |
| **第三方库** | 所有pip包（pandas, numpy等） | 仅内置库 |
| **界面** | 极简（仅登录窗口） | 完整交易UI + 图表 |
| **行情数据** | 通过xtdata API | 内置 + xtdata API |
| **交易** | 通过xttrade API | 内置 + xttrade API |
| **资源占用** | 轻量（~50 MB内存） | 较重（完整GUI，~500 MB+） |
| **调试** | 完整IDE调试支持 | 有限 |
| **使用场景** | 自动化策略、外部集成 | 可视化分析 + 手动交易 |
| **连接方式** | 一次性连接，无自动重连 | 持久连接 |

---

## 数据能力（通过xtdata）

| 类别 | 详情 |
|---|---|
| **K-line** | tick, 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mon — supports adjustment (forward / backward / proportional) |
| **Tick** | Real-time tick data with 5-level bid/ask, volume, turnover, trade count |
| **Level 2** | l2quote (real-time snapshot), l2order (order-by-order), l2transaction (trade-by-trade), l2quoteaux (aggregate buy/sell), l2orderqueue (order queue), l2thousand (1000-level order book), fullspeedorderbook (full-speed 20-level) |
| **Financials** | Balance sheet, income statement, cash flow statement, per-share metrics, share structure, top 10 shareholders / free-float holders, shareholder count |
| **Reference** | Trading calendar, holidays, sector lists, index constituents & weights, ex-dividend data, contract info |
| **Real-time** | Single-stock subscription (`subscribe_quote`), market-wide push (`subscribe_whole_quote`) |
| **Special** | Convertible bond info, IPO subscription data, ETF creation/redemption lists, announcements & news, consecutive limit-up tracking, snapshot indicators (volume ratio / price velocity), high-frequency IOPV |

### 数据访问模式

```
download_history_data() → get_market_data_ex()  # Historical data: download to local cache first, then read from cache
subscribe_quote()       → callback               # Real-time data: subscribe and receive via callback
get_full_tick()                                   # Snapshot data: get latest tick for the entire market
```

## 交易能力（通过xttrade）

| 类别 | 操作 |
|---|---|
| **Stocks** | Buy/sell (sync and async), limit/market/best price orders |
| **ETF** | Buy/sell, creation/redemption |
| **Convertible bonds** | Buy/sell |
| **Futures** | Open long/close long/open short/close short |
| **Options** | Buy/sell open/close, covered open/close, exercise, lock/unlock |
| **Margin trading** | Margin buy, short sell, buy to cover, direct return, sell to repay, direct repayment, special margin/short |
| **IPO** | New share/bond subscription, query subscription quota |
| **Cancel** | Cancel by order_id or broker contract number (sync and async) |
| **Query** | Assets, orders, trades, positions, futures position summary |
| **Credit query** | Credit assets, liability contracts, margin-eligible securities, available-to-short data, collateral |
| **Bank-broker transfer** | Bank to securities, securities to bank (sync and async) |
| **Smart algorithms** | VWAP and other algorithmic execution |
| **Securities lending** | Query available securities, apply for lending, manage contracts |

### 账户类型

```python
StockAccount('id')            # 普通股票账户
StockAccount('id', 'CREDIT')  # 信用账户（融资融券）
StockAccount('id', 'FUTURE')  # 期货账户
```

### 关键交易回调

| 回调函数 | 触发时机 |
|---|---|
| `on_stock_order(order)` | Order status change (submitted, partially filled, fully filled, cancelled, rejected) |
| `on_stock_trade(trade)` | Trade execution report |
| `on_stock_position(position)` | Position change |
| `on_stock_asset(asset)` | Asset/fund change |
| `on_order_error(error)` | Order placement failure |
| `on_cancel_error(error)` | Order cancellation failure |
| `on_disconnected()` | Disconnected from miniQMT |

### 订单状态码

| 值 | 状态 |
|---|---|
| 48 | 未报 |
| 50 | 已报 |
| 54 | 已撤 |
| 55 | 部分成交 |
| 56 | 已成 |
| 57 | 废单 |

---

## 常见券商路径

```python
# 国金证券
path = r'D:\国金证券QMT交易端\userdata_mini'
# 华鑫证券
path = r'D:\华鑫证券\userdata_mini'
# 中泰证券
path = r'D:\中泰证券\userdata_mini'
# 东方财富
path = r'D:\东方财富证券QMT交易端\userdata_mini'
```

## 股票代码格式

| 市场 | 示例 |
|---|---|
| 上海A股 | `600000.SH` |
| 深圳A股 | `000001.SZ` |
| 北交所 | `430047.BJ` |
| 指数 | `000001.SH`（上证综指）, `399001.SZ`（深证成指） |
| 中金所期货 | `IF2401.IF` |
| 上期所期货 | `ag2407.SF` |
| 期权 | `10004358.SHO` |
| ETF | `510300.SH` |
| 可转债 | `113050.SH` |

---

## 完整示例：行情数据 + 交易策略

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

# === 回调类定义 ===
class MyCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print('已断开连接')
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, order_error):
        print(f'Error: {order_error.error_msg}')

# === 1. 连接行情数据服务 ===
xtdata.connect()

# === 2. 下载并获取历史数据 ===
stock = '000001.SZ'
xtdata.download_history_data(stock, '1d', start_time='20240101', end_time='20240630')
data = xtdata.get_market_data_ex(
    [], [stock], period='1d',
    start_time='20240101', end_time='20240630',
    dividend_type='front'  # 前复权
)
df = data[stock]

# === 3. 计算简单均线交叉信号 ===
df['ma5'] = df['close'].rolling(5).mean()    # 5日均线
df['ma20'] = df['close'].rolling(20).mean()  # 20日均线
latest = df.iloc[-1]   # 最新K线
prev = df.iloc[-2]     # 前一根K线

# === 4. 连接交易服务 ===
path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 123456)
xt_trader.register_callback(MyCallback())
xt_trader.start()
if xt_trader.connect() != 0:
    print('连接失败！')
    exit()

account = StockAccount('your_account')
xt_trader.subscribe(account)  # 订阅账户推送通知

# === 5. 执行交易信号 ===
if prev['ma5'] <= prev['ma20'] and latest['ma5'] > latest['ma20']:
    # 金叉信号：5日均线上穿20日均线，买入
    order_id = xt_trader.order_stock(
        account, stock, xtconstant.STOCK_BUY, 100,
        xtconstant.LATEST_PRICE, 0, 'ma_cross', 'golden_cross'
    )
    print(f'Golden cross buy — {stock}, order_id={order_id}')
elif prev['ma5'] >= prev['ma20'] and latest['ma5'] < latest['ma20']:
    # 死叉信号：5日均线下穿20日均线，卖出
    order_id = xt_trader.order_stock(
        account, stock, xtconstant.STOCK_SELL, 100,
        xtconstant.LATEST_PRICE, 0, 'ma_cross', 'death_cross'
    )
    print(f'Death cross sell — {stock}, order_id={order_id}')

# === 6. 查询结果 ===
asset = xt_trader.query_stock_asset(account)
print(f'Available cash: {asset.cash}, Total assets: {asset.total_asset}')

positions = xt_trader.query_stock_positions(account)
for pos in positions:
    print(f'{pos.stock_code}: {pos.volume} shares, available={pos.can_use_volume}, cost={pos.open_price}')
```

## 完整示例：实时行情监控

```python
from xtquant import xtdata
import threading

def on_tick(datas):
    """Tick数据回调函数"""
    for code, tick in datas.items():
        print(f'{code}: latest={tick["lastPrice"]}, volume={tick["volume"]}')

# 连接行情数据服务
xtdata.connect()

# 在单独线程中运行订阅（xtdata.run()会阻塞当前线程）
def run_data():
    xtdata.subscribe_quote('000001.SZ', period='tick', callback=on_tick)
    xtdata.subscribe_quote('600000.SH', period='tick', callback=on_tick)
    xtdata.run()  # 阻塞线程，持续接收数据

t = threading.Thread(target=run_data, daemon=True)
t.start()

# 主线程可以执行交易或其他操作
# ...
```

## 使用技巧

- miniQMT **仅支持Windows** — 如果TCP可达，Python脚本可以在同一台或不同机器上运行。
- Python脚本运行期间，miniQMT必须保持**登录状态**。
- `connect()` 是**一次性连接** — 断开后不会自动重连，需要自行实现重连逻辑。
- `session_id` 对**每个策略必须唯一** — 不同Python脚本必须使用不同的session_id。
- 实时订阅时，`xtdata.run()` 会阻塞线程 — 请在**单独线程**中运行，主线程用于交易。
- 下载的数据会**本地缓存** — 后续读取速度极快。
- 在推送回调（`on_stock_order`等）中，使用**异步查询方法**（如 `query_stock_orders_async`）避免死锁。或启用 `set_relaxed_response_order_enabled(True)`。
- 部分券商提供miniQMT免费**Level 2数据** — 请咨询您的券商。
- 文档：http://dict.thinktrader.net/nativeApi/start_now.html

---

## 进阶示例

### 网格交易策略

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import threading

class GridCallback(XtQuantTraderCallback):
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, error):
        print(f'Error: {error.error_msg}')

# 初始化交易
path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 100001)
xt_trader.register_callback(GridCallback())
xt_trader.start()
xt_trader.connect()
account = StockAccount('your_account')
xt_trader.subscribe(account)

# 网格参数
stock = '000001.SZ'
grid_base = 11.0       # 基准价格
grid_step = 0.2        # 网格间距
grid_shares = 100      # 每格交易股数
grid_levels = 5        # 上下各5档
last_grid = 0          # 当前网格层级

xtdata.connect()

def on_tick(datas):
    global last_grid
    for code, tick in datas.items():
        price = tick['lastPrice']
        # 计算价格对应的当前网格层级
        current_grid = int((price - grid_base) / grid_step)

        if current_grid < last_grid:
            # 价格下穿网格线，买入
            for _ in range(last_grid - current_grid):
                xt_trader.order_stock(
                    account, code, xtconstant.STOCK_BUY, grid_shares,
                    xtconstant.LATEST_PRICE, 0, 'grid', f'网格买入_level{current_grid}'
                )
            last_grid = current_grid

        elif current_grid > last_grid:
            # 价格上穿网格线，卖出
            for _ in range(current_grid - last_grid):
                xt_trader.order_stock(
                    account, code, xtconstant.STOCK_SELL, grid_shares,
                    xtconstant.LATEST_PRICE, 0, 'grid', f'网格卖出_level{current_grid}'
                )
            last_grid = current_grid

# 启动行情数据订阅
def run_data():
    xtdata.subscribe_quote(stock, period='tick', callback=on_tick)
    xtdata.run()

t = threading.Thread(target=run_data, daemon=True)
t.start()
xt_trader.run_forever()
```

### 可转债T+0日内交易

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import threading

class CBCallback(XtQuantTraderCallback):
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')

path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 100002)
xt_trader.register_callback(CBCallback())
xt_trader.start()
xt_trader.connect()
account = StockAccount('your_account')
xt_trader.subscribe(account)

# 可转债代码（可转债支持T+0交易）
cb_code = '113050.SH'
buy_threshold = -0.5   # 跌幅超过0.5%买入
sell_threshold = 0.5   # 涨幅超过0.5%卖出
position = 0

xtdata.connect()

def on_tick(datas):
    global position
    for code, tick in datas.items():
        price = tick['lastPrice']
        pre_close = tick['lastClose']
        if pre_close == 0:
            continue
        pct_change = (price - pre_close) / pre_close * 100

        # 跌幅达到阈值，买入10手
        if pct_change <= buy_threshold and position == 0:
            xt_trader.order_stock(
                account, code, xtconstant.STOCK_BUY, 10,
                xtconstant.LATEST_PRICE, 0, 'cb_t0', '可转债T0买入'
            )
            position = 10

        # 涨幅达到阈值，卖出
        elif pct_change >= sell_threshold and position > 0:
            xt_trader.order_stock(
                account, code, xtconstant.STOCK_SELL, position,
                xtconstant.LATEST_PRICE, 0, 'cb_t0', '可转债T0卖出'
            )
            position = 0

def run_data():
    xtdata.subscribe_quote(cb_code, period='tick', callback=on_tick)
    xtdata.run()

t = threading.Thread(target=run_data, daemon=True)
t.start()
xt_trader.run_forever()
```

### 定时打新申购

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import datetime
import time

class IPOCallback(XtQuantTraderCallback):
    def on_stock_order(self, order):
        print(f'IPO subscription: {order.stock_code} status={order.order_status} {order.status_msg}')

path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 100003)
xt_trader.register_callback(IPOCallback())
xt_trader.start()
xt_trader.connect()
account = StockAccount('your_account')
xt_trader.subscribe(account)

# 查询新股申购额度
limits = xt_trader.query_new_purchase_limit(account)
print(f"Subscription quota: {limits}")

# 查询今日新股数据
ipo_data = xt_trader.query_ipo_data()
if ipo_data:
    for code, info in ipo_data.items():
        print(f"New stock: {code} {info['name']} issue price={info['issuePrice']} max subscription={info['maxPurchaseNum']}")
        # 以最大允许量申购
        max_vol = info['maxPurchaseNum']
        if max_vol > 0:
            order_id = xt_trader.order_stock(
                account, code, xtconstant.STOCK_BUY, max_vol,
                xtconstant.FIX_PRICE, info['issuePrice'], 'ipo', '新股申购'
            )
            print(f"  Subscription submitted: order_id={order_id}")
else:
    print("今日无新股可申购")
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

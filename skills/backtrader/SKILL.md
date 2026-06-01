---
name: backtrader
description: Backtrader 开源量化回测框架 - 支持多数据源、多策略、多周期回测与实盘交易，纯Python实现。
version: 1.1.0
homepage: https://github.com/mementum/backtrader
metadata: {"clawdbot":{"emoji":"🔄","requires":{"bins":["python3"]}}}
---

# Backtrader（开源量化回测框架）

[Backtrader](https://github.com/mementum/backtrader) 是一个强大的开源Python量化回测框架，支持多数据源、多策略、多周期回测与实盘交易。纯Python实现，无外部依赖，架构清晰且易于扩展。

> 文档：https://www.backtrader.com/docu/

## 安装

```bash
pip install backtrader
# 如需绘图
pip install backtrader[plotting]
# 或者
pip install matplotlib
```

## 核心概念

Backtrader 使用面向对象的事件驱动架构：

- **Cerebro**：策略引擎，负责协调数据、策略和经纪商
- **Strategy**：策略类，编写交易逻辑的地方
- **Data Feed**：数据源，支持CSV、Pandas和在线数据
- **Broker**：经纪商模拟，管理资金和订单
- **Indicator**：技术指标，内置100+常用指标
- **Analyzer**：分析器，计算策略绩效指标
- **Observer**：观察器，记录策略运行时状态

## 最简示例

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    """简单均线策略"""
    params = (('period', 20),)  # 策略参数：均线周期

    def __init__(self):
        # 初始化指标（在__init__中定义，自动计算）
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)

    def next(self):
        # 每根K线触发一次，在此编写交易逻辑
        if self.data.close[0] > self.sma[0]:
            if not self.position:  # 无持仓则买入
                self.buy()
        elif self.data.close[0] < self.sma[0]:
            if self.position:      # 有持仓则卖出
                self.sell()

# 创建引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)

# 加载数据（Yahoo CSV格式）
data = bt.feeds.YahooFinanceCSVData(dataname='stock_data.csv')
cerebro.adddata(data)

# 设置初始资金
cerebro.broker.setcash(100000.0)
# 设置手续费
cerebro.broker.setcommission(commission=0.001)

# 运行回测
print(f'初始资金: {cerebro.broker.getvalue():.2f}')
cerebro.run()
print(f'最终资金: {cerebro.broker.getvalue():.2f}')

# 绘制结果
cerebro.plot()
```

---

## 数据源

### 从Pandas DataFrame加载

```python
import backtrader as bt
import pandas as pd

# 从CSV读取数据
df = pd.read_csv('stock_data.csv', parse_dates=['date'], index_col='date')
# DataFrame必须包含列: open, high, low, close, volume（小写列名）

data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
```

### 从CSV文件加载

```python
# 通用CSV格式
data = bt.feeds.GenericCSVData(
    dataname='stock_data.csv',
    dtformat='%Y-%m-%d',    # 日期格式
    datetime=0,              # 日期列索引
    open=1,                  # 开盘价列索引
    high=2,                  # 最高价列索引
    low=3,                   # 最低价列索引
    close=4,                 # 收盘价列索引
    volume=5,                # 成交量列索引
    openinterest=-1          # 持仓量列索引（-1表示无此列）
)
cerebro.adddata(data)
```

### 多股票 / 多周期

```python
# 加载多只股票数据
data1 = bt.feeds.PandasData(dataname=df1, name='stock1')
data2 = bt.feeds.PandasData(dataname=df2, name='stock2')
cerebro.adddata(data1)
cerebro.adddata(data2)

# 在策略中访问多只股票
class MultiStockStrategy(bt.Strategy):
    def __init__(self):
        # self.datas[0]是第一只股票，self.datas[1]是第二只
        self.sma1 = bt.indicators.SMA(self.datas[0].close, period=20)
        self.sma2 = bt.indicators.SMA(self.datas[1].close, period=20)

    def next(self):
        for i, d in enumerate(self.datas):
            print(f'{d._name}: close={d.close[0]:.2f}')
```

### 数据重采样（分钟线转日线）

```python
# 加载分钟数据
data_min = bt.feeds.GenericCSVData(dataname='1min_data.csv', timeframe=bt.TimeFrame.Minutes)
cerebro.adddata(data_min)

# 重采样为日线
cerebro.resampledata(data_min, timeframe=bt.TimeFrame.Days)
```


---

## 策略类详解

### 策略参数

```python
class MyStrategy(bt.Strategy):
    # 定义可调参数（元组格式）
    params = (
        ('fast_period', 5),     # 快速均线周期
        ('slow_period', 20),    # 慢速均线周期
        ('stake', 100),         # 每次交易手数
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(period=self.p.fast_period)
        self.slow_ma = bt.indicators.SMA(period=self.p.slow_period)
        # self.p 是 self.params 的简写

    def next(self):
        if self.fast_ma[0] > self.slow_ma[0]:
            self.buy(size=self.p.stake)

# 参数可在运行时覆盖
cerebro.addstrategy(MyStrategy, fast_period=10, slow_period=30)
```

### 交易方法

```python
class MyStrategy(bt.Strategy):
    def next(self):
        # 按数量买入
        self.buy(size=100)                    # 买入100股
        self.sell(size=100)                   # 卖出100股

        # 调整到目标仓位
        self.order_target_size(target=500)    # 调整持仓为500股
        self.order_target_value(target=50000) # 调整持仓为5万元市值
        self.order_target_percent(target=0.5) # 调整持仓为总资产的50%

        # 限价单
        self.buy(size=100, price=10.5, exectype=bt.Order.Limit)
        # 止损单
        self.sell(size=100, price=9.0, exectype=bt.Order.Stop)
        # 止损限价单
        self.buy(size=100, price=10.5, pricelimit=10.8, exectype=bt.Order.StopLimit)

        # 撤单
        order = self.buy(size=100)
        self.cancel(order)

        # 对其他股票下单
        self.buy(data=self.datas[1], size=200)  # 买入第二只股票
```

### 订单通知回调

```python
class MyStrategy(bt.Strategy):
    def notify_order(self, order):
        """订单状态变化时触发"""
        if order.status in [order.Submitted, order.Accepted]:
            return  # 订单已提交/已接受，等待执行

        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'Buy executed: price={order.executed.price:.2f}, '
                      f'size={order.executed.size}, commission={order.executed.comm:.2f}')
            else:
                print(f'Sell executed: price={order.executed.price:.2f}, '
                      f'size={order.executed.size}, commission={order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f'Order failed: status={order.getstatusname()}')

    def notify_trade(self, trade):
        """交易完成时触发（一买一卖构成完整交易）"""
        if trade.isclosed:
            print(f'Trade completed: gross P&L={trade.pnl:.2f}, net P&L={trade.pnlcomm:.2f}')
```

### 获取数据与持仓

```python
class MyStrategy(bt.Strategy):
    def next(self):
        # 当前K线数据
        current_close = self.data.close[0]     # 当前收盘价
        prev_close = self.data.close[-1]       # 前一根K线收盘价
        current_volume = self.data.volume[0]   # 当前成交量
        current_date = self.data.datetime.date(0)  # 当前日期

        # 持仓信息
        position = self.getposition(self.data)
        print(f'Position size: {position.size}')
        print(f'Average price: {position.price:.2f}')

        # 账户信息
        cash = self.broker.getcash()           # 可用资金
        value = self.broker.getvalue()         # 总资产
        print(f'Available cash: {cash:.2f}, Total value: {value:.2f}')
```


---

## 内置技术指标

```python
class MyStrategy(bt.Strategy):
    def __init__(self):
        # 均线
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=20)
        self.wma = bt.indicators.WeightedMovingAverage(self.data.close, period=20)

        # MACD
        self.macd = bt.indicators.MACD(self.data.close)
        # self.macd.macd = DIF线, self.macd.signal = DEA线, self.macd.histo = MACD柱

        # RSI
        self.rsi = bt.indicators.RSI(self.data.close, period=14)

        # Bollinger Bands
        self.boll = bt.indicators.BollingerBands(self.data.close, period=20, devfactor=2.0)
        # self.boll.mid = 中轨, self.boll.top = 上轨, self.boll.bot = 下轨

        # KDJ (Stochastic Oscillator)
        self.stoch = bt.indicators.Stochastic(self.data, period=14)

        # ATR (Average True Range)
        self.atr = bt.indicators.ATR(self.data, period=14)

        # Crossover signals
        self.crossover = bt.indicators.CrossOver(self.sma, self.ema)
        # crossover > 0 表示金叉, < 0 表示死叉
```

---

## 券商/经纪商设置

```python
cerebro = bt.Cerebro()

# 设置初始资金
cerebro.broker.setcash(1000000.0)

# 设置手续费
cerebro.broker.setcommission(commission=0.001)  # 0.1%

# 设置手续费 by percentage
cerebro.broker.setcommission(
    commission=0.0003,     # 0.03%
    margin=None,           # 保证金（期货用）
    mult=1.0               # 合约乘数（期货用）
)

# Set slippage
cerebro.broker.set_slippage_perc(perc=0.001)    # 百分比滑点
cerebro.broker.set_slippage_fixed(fixed=0.02)   # 固定滑点

# Set trade size per order
cerebro.addsizer(bt.sizers.FixedSize, stake=100)        # 固定100股
cerebro.addsizer(bt.sizers.PercentSizer, percents=95)   # 总资产的95%
```

---

## 分析器

```python
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)

# 添加分析器
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')       # 夏普比率
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')        # 最大回撤
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')          # 收益率
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')     # 交易统计
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')                 # 系统质量数
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual')     # 年化收益

results = cerebro.run()
strat = results[0]

# 获取分析结果
print(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
print(f"Max Drawdown: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
print(f"Total Return: {strat.analyzers.returns.get_analysis()['rtot']:.4f}")

# 交易统计
trade_analysis = strat.analyzers.trades.get_analysis()
print(f"Total trades: {trade_analysis['total']['total']}")
print(f"Winning trades: {trade_analysis['won']['total']}")
print(f"Losing trades: {trade_analysis['lost']['total']}")
```


---

## 参数优化

```python
# Use optstrategy for parameter grid search
cerebro = bt.Cerebro()
cerebro.optstrategy(
    MyStrategy,
    fast_period=range(5, 15),     # Fast MA: 5 to 14
    slow_period=range(20, 40, 5)  # Slow MA: 20, 25, 30, 35
)

data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

# 运行优化（自动遍历所有参数组合）
results = cerebro.run(maxcpus=4)  # 多核并行

# 提取最优参数
best_sharpe = -999
best_params = None
for result in results:
    for strat in result:
        sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        if sharpe and sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = strat.params
            
print(f'Best params: fast={best_params.fast_period}, slow={best_params.slow_period}')
print(f'Best Sharpe: {best_sharpe:.2f}')
```

---

## 进阶示例

### MACD + 布林带组合策略

```python
import backtrader as bt

class MACDBollStrategy(bt.Strategy):
    """MACD金叉 + 布林带下轨支撑组合买入策略"""
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('boll_period', 20),
        ('boll_dev', 2.0),
        ('stake', 100),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        self.boll = bt.indicators.BollingerBands(
            self.data.close, period=self.p.boll_period, devfactor=self.p.boll_dev
        )
        # MACD金叉信号
        self.macd_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position:
            # 买入条件：MACD金叉 且 价格低于布林带中轨（低位买入）
            if self.macd_cross[0] > 0 and self.data.close[0] < self.boll.mid[0]:
                self.buy(size=self.p.stake)
                print(f'{self.data.datetime.date(0)} Buy: {self.data.close[0]:.2f}')
        else:
            # 卖出条件：价格触及布林带上轨 或 MACD死叉
            if self.data.close[0] > self.boll.top[0] or self.macd_cross[0] < 0:
                self.sell(size=self.p.stake)
                print(f'{self.data.datetime.date(0)} Sell: {self.data.close[0]:.2f}')

    def notify_trade(self, trade):
        if trade.isclosed:
            print(f'Trade completed: net profit={trade.pnlcomm:.2f}')

# 运行回测
cerebro = bt.Cerebro()
cerebro.addstrategy(MACDBollStrategy)
data = bt.feeds.PandasData(dataname=df)  # df is a DataFrame containing OHLCV data
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(commission=0.001)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')
results = cerebro.run()
strat = results[0]
print(f'Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()["sharperatio"]:.2f}')
print(f'Max Drawdown: {strat.analyzers.dd.get_analysis()["max"]["drawdown"]:.2f}%')
cerebro.plot()
```


### 海龟交易策略（完整实现）

```python
import backtrader as bt

class TurtleStrategy(bt.Strategy):
    """经典海龟交易策略 — 唐奇安通道突破 + ATR仓位管理"""
    params = (
        ('entry_period', 20),    # 入场通道周期
        ('exit_period', 10),     # 出场通道周期
        ('atr_period', 20),      # ATR周期
        ('risk_pct', 0.01),      # 每笔交易风险比例
    )

    def __init__(self):
        self.entry_high = bt.indicators.Highest(self.data.high, period=self.p.entry_period)
        self.entry_low = bt.indicators.Lowest(self.data.low, period=self.p.entry_period)
        self.exit_high = bt.indicators.Highest(self.data.high, period=self.p.exit_period)
        self.exit_low = bt.indicators.Lowest(self.data.low, period=self.p.exit_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.order = None

    def next(self):
        if self.order:
            return  # 有未完成订单，等待

        # 计算仓位大小（基于ATR的风险管理）
        atr_val = self.atr[0]
        if atr_val <= 0:
            return
        unit_size = int(self.broker.getvalue() * self.p.risk_pct / atr_val)
        unit_size = max(unit_size, 1)

        if not self.position:
            # 突破20日高点 → 做多
            if self.data.close[0] > self.entry_high[-1]:
                self.order = self.buy(size=unit_size)
        else:
            # 跌破10日低点 → 平仓
            if self.data.close[0] < self.exit_low[-1]:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'{self.data.datetime.date(0)} Buy {order.executed.size} shares @ {order.executed.price:.2f}')
            else:
                print(f'{self.data.datetime.date(0)} Sell @ {order.executed.price:.2f}')
        self.order = None
```

### 多股票轮动策略

```python
import backtrader as bt

class MomentumRotation(bt.Strategy):
    """动量轮动策略 — 每月持有动量最强的前N只股票"""
    params = (
        ('momentum_period', 20),  # 动量计算周期（交易日）
        ('hold_num', 3),          # 持股数量
        ('rebalance_days', 20),   # 调仓周期
    )

    def __init__(self):
        self.counter = 0
        # 计算每只股票的动量指标（N日收益率）
        self.momentums = {}
        for d in self.datas:
            self.momentums[d._name] = bt.indicators.RateOfChange(
                d.close, period=self.p.momentum_period
            )

    def next(self):
        self.counter += 1
        if self.counter % self.p.rebalance_days != 0:
            return  # 非调仓日

        # 计算并排序每只股票的动量
        rankings = []
        for d in self.datas:
            mom = self.momentums[d._name][0]
            rankings.append((d._name, d, mom))
        rankings.sort(key=lambda x: x[2], reverse=True)

        # 选取动量最强的前N只股票
        selected = [r[1] for r in rankings[:self.p.hold_num]]
        selected_names = [r[0] for r in rankings[:self.p.hold_num]]
        print(f'{self.data.datetime.date(0)} Selected stocks: {selected_names}')

        # 卖出不在目标列表中的持仓
        for d in self.datas:
            if self.getposition(d).size > 0 and d not in selected:
                self.close(data=d)

        # 等权重买入目标股票
        if selected:
            per_value = self.broker.getvalue() * 0.95 / len(selected)
            for d in selected:
                target_size = int(per_value / d.close[0])
                current_size = self.getposition(d).size
                if target_size > current_size:
                    self.buy(data=d, size=target_size - current_size)
                elif target_size < current_size:
                    self.sell(data=d, size=current_size - target_size)
```


---

## 使用技巧

- Backtrader是纯本地框架，不依赖在线服务，适合离线研究。
- 数据需要用户自行准备（可配合AKShare、Tushare等数据源使用）。
- 在 `__init__` 中定义指标，在 `next` 中编写交易逻辑 — 这是核心模式。
- 使用 `self.data.close[0]` 访问当前值，`[-1]` 访问前一个值。
- 通过 `optstrategy` 进行参数优化支持多核并行，显著加速。
- 绘图需要安装matplotlib；直接调用 `cerebro.plot()` 即可。
- 文档：https://www.backtrader.com/docu/

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
